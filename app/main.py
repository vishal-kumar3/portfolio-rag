from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.logging import setup_logging
from app.services.chat import ChatSession
from app.services.llm import LLMService
from app.services.prompt import Prompt_Template
from app.services.session import SessionManager
from app.services.vector_store import VectorStoreService
from app.services.rag import RAGService
from app.core.config import settings

from app.api.v1.endpoints.rag import router as RagRouter

# TODO: Logging setup
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  logger.info("Starting RAG Backend Application")

  prompt_template = Prompt_Template()
  llm_service = LLMService()
  session_manager = SessionManager()
  chat_session = ChatSession(session_manager, prompt_template)
  app.state.chat_session = chat_session
  app.state.session_manager = session_manager
  app.state.vector_store = VectorStoreService(llm_service.embedding_model)
  app.state.rag_service = RAGService(app.state.vector_store, llm_service,
                                     app.state.chat_session, prompt_template)

  logger.info("Application started successfully")
  yield

  logger.info("Application shutdown completed")


def create_app() -> FastAPI:
  app = FastAPI(title="RAG Backend",
                version="1.0.0",
                description="Backend service for portfolio RAG application",
                lifespan=lifespan)

  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.CORS_ORIGINS,
      allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
      allow_methods=settings.CORS_ALLOW_METHODS,
      allow_headers=settings.CORS_ALLOW_HEADERS,
  )

  app.add_middleware(GZipMiddleware, minimum_size=1000)
  # app.add_middleware(LoggingMiddleware)
  # app.add_middleware(RateLimitMiddleware)

  # app.include_router(health.router, prefix=settings.API_V1_PREFIX)
  # app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
  # app.include_router(query.router, prefix=settings.API_V1_PREFIX)
  # app.include_router(admin.router, prefix=settings.API_V1_PREFIX)

  return app


app = create_app()

app.include_router(RagRouter)
