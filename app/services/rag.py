import logging
from typing import List, Dict, Any
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain_core.messages import BaseMessage

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

  async def rag_query_chain(self, user_id):
    llm = self.llm.get_chat_model()
    prompt = self.prompt_service.rag_prompt()
    retriever = self.vector_store.get_retriever()

    def get_context(input_dict: Dict[str, Any]):
      return retriever.get_relevant_documents(input_dict["question"])

    return (RunnableMap(
        {
            "context": get_context,
            "question": RunnablePassthrough(),
            "chat_history":
            lambda _: self.chat_session.get_chat_history(user_id)
        })
            | prompt
            | llm)
