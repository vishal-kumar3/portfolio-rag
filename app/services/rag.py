import logging
from langchain_core.runnables import RunnableMap, RunnablePassthrough

from app.services.prompt import Prompt_Template
from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService

logger = logging.getLogger(__name__)


class RAGService:

  def __init__(self, vector_store: VectorStoreService, llm_service: LLMService,
               prompt_template: Prompt_Template):
    self.vector_store = vector_store
    self.llm = llm_service
    self.prompt_service = prompt_template

  async def rag_query_chain(self):
    llm = self.llm.get_chat_model()
    prompt = self.prompt_service.rag_prompt()
    retriever = self.vector_store.get_retriever()

    return (
      RunnableMap({
        "context": lambda x: retriever.get_relevant_documents(x["question"]),
        "question": RunnablePassthrough()
      })
      | prompt
      | llm
    )
