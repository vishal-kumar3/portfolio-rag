from typing import Any, Dict, Optional, List
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from app.core.config import settings


class VectorStoreService:

  def __init__(self, embedding_model, vector_store_path=None):
    self.embedding_model = embedding_model
    self.client = self.create_vector_store(
        self.embedding_model, vector_store_path
        if vector_store_path is not None else settings.VECTOR_STORE_PATH)

  def add_documents(self, documents: List[Document]) -> None:
    try:
      self.client.add_documents(documents)
    except Exception as e:
      raise Exception(f"Failed to add documents to vector store: {str(e)}")

  def query(self, query_text: str, top_k: int = 2) -> List[Document]:
    try:
      results = self.client.similarity_search(query_text, k=top_k)
      return results
    except Exception as e:
      raise Exception(f"Failed to query vector store: {str(e)}")

  def get_retriever(self, search_kwargs: Optional[Dict[str, Any]] = None):
    kwargs = search_kwargs or {"k": 10}
    docs = self.client.as_retriever(search_kwargs=kwargs)
    return docs

  @staticmethod
  def create_vector_store(embedding_model, vector_store_path: str) -> Chroma:
    try:
      return Chroma(persist_directory=vector_store_path,
                    collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
                    embedding_function=embedding_model)
    except Exception as e:
      raise Exception(f"Failed to create vector store: {str(e)}")
