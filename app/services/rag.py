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
            },
            "tags": "contact, email, linkedin, github, twitter, discord",
            "temperature": 0.3
        },
        "contact": {
            "filter": {
                "type": "contact"
            },
            "tags": "contact, email, linkedin, github, twitter, discord",
            "temperature": 0.3
        },
        "connect": {
            "filter": {
                "type": "contact"
            },
            "tags": "contact, email, linkedin, github, twitter, discord",
            "temperature": 0.3
        },
        "personal project": {
            "filter": {
                "directory": "project"
            },
            "tags": "Project, Devcord, WriteFlow, Interview-AI",
            "temperature": 0.5
        },
        "current employment": {
            "filter": {
                "directory": "experience",
                "timeline_status": "ongoing"
            },
            "tags": "Experience, Espo, Internship",
            "temperature": 0.3
        },
        "internship": {
            "filter": {
                "directory": "experience"
            },
            "tags": "Experience, Fiel, Espo, Internship",
            "temperature": 0.3
        },
        "geospatial": {
            "filter": {
                "directory": "experience",
                "source": "data/experience/fiel.md"
            },
            "tags": "Fiel, geospatial, filtering",
            "temperature": 0.3
        },
        "vilash": {
            "filter": {
                "directory": "about"
            },
            "tags": "Vishal, summary, about",
            "temperature": 0.3
        },
        "hobbies": {
            "filter": {
                "directory": "about"
            },
            "tags": "summary, about, hobbies, interests",
            "temperature": 0.3
        }
    }
    query_lower = query.lower()
    for key, value in synonyms.items():
      if key in query_lower:
        return {
            "query": query,
            "filter": value["filter"],
            "tags": value.get("tags", ""),
            "temperature": value.get("temperature", 0.4)
        }
    return {
        "query": query,
        "filter": {},
        "tags": "",
        "temperature": 0.4
    }

  async def rag_query_chain(self, user_id, streaming: bool = False):
    retriever = self.vector_store.get_retriever()
    prompt = self.prompt_service.rag_prompt()

    def transform_input(input_dict: Dict[str, Any]):
        # Preprocess the query to get filters, tags, and temperature
        processed = self.preprocess_query(input_dict["question"])

        # Get context based on processed query
        context = retriever.invoke(processed["query"])

        # Extract metadata for debugging
        metadata = [doc.metadata["source"].split("/")[-1] for doc in context]
        print("Retrieved documents:", metadata)

        # Get the query-specific settings
        temp = processed.get("temperature", 0.4)

        # Update LLM temperature if needed
        if temp != 0.4:
            self.llm.get_chat_model(temp=temp, streaming=streaming)

        return {
            "context": context,
            "tags": processed.get("tags", "No specific tags"),
            "filters": str(processed.get("filter", {})),  # Convert dict to string for template
            "question": input_dict["question"],
            "chat_history": self.chat_session.get_chat_history(user_id)
        }

    chain = (
        RunnablePassthrough() | transform_input | prompt |
        self.llm.get_chat_model(streaming=streaming)
    )

    return chain
