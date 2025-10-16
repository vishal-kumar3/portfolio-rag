import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableMap, RunnablePassthrough

from app.services.chat import ChatSession
from app.services.prompt import Prompt_Template
from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService

logger = logging.getLogger(__name__)


class RAGService:

  def __init__(self, vector_store: VectorStoreService, llm_service: LLMService,
               chat_session: ChatSession, prompt_template: Prompt_Template):
    self.vector_store = vector_store
    self.llm = llm_service
    self.prompt_service = prompt_template
    self.chat_session = chat_session

  @staticmethod
  def preprocess_query(query: str) -> dict:
    synonyms = {
        "email": {
            "filter": {
                "type": "contact"
            }
        },
        "contact": {
            "filter": {
                "type": "contact"
            }
        },
        "connect": {
            "filter": {
                "type": "contact"
            }
        },
        # "personal project": {
        #   "filter": {
        #     "directory": "project"
        #   }
        # },
        # "current employment": {
        #   "filter": {
        #     "directory": "experience"
        #   }
        # }
    }
    query_lower = query.lower()
    for key, value in synonyms.items():
      if key in query_lower:
        return {"query": query, "filter": value["filter"]}
    return {"query": query, "filter": {}}

  async def rag_query_chain(self, user_id, streaming: bool = False):
    llm = self.llm.get_chat_model(streaming=streaming)
    prompt = self.prompt_service.rag_prompt()
    retriever = self.vector_store.get_retriever()

    def get_context(input_dict: Dict[str, Any]):
      result = retriever.get_relevant_documents(input_dict["question"])
      return result

    chain = (RunnableMap(
        {
            "context": get_context,
            "question": RunnablePassthrough(),
            "chat_history":
            lambda _: self.chat_session.get_chat_history(user_id)
        })
             | prompt
             | llm)

    return chain
