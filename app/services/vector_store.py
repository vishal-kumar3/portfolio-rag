from typing import Any, Dict, Optional, List
import os
import time
import shutil
import logging

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings

logger = logging.getLogger(__name__)


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
  def _is_valid_sqlite(sqlite_path: str) -> bool:
    """Quick check whether the file at sqlite_path looks like a SQLite DB.

    Returns True if it starts with the SQLite header 'SQLite format 3\0'.
    """
    try:
      with open(sqlite_path, "rb") as f:
        header = f.read(16)
      return header.startswith(b"SQLite format 3\x00")
    except Exception:
      return False

  @staticmethod
  def create_vector_store(embedding_model, vector_store_path: str) -> Chroma:
    """Create a Chroma vector store, but detect and move aside a corrupted
    or non-sqlite `chroma.sqlite3` file (common when a git-lfs pointer was
    accidentally committed) so that Chroma can recreate the DB instead of
    crashing the app at startup.
    """
    # Ensure dir exists
    try:
      os.makedirs(vector_store_path, exist_ok=True)
    except Exception as e:
      logger.warning("Could not create vector store path %s: %s", vector_store_path, str(e))

    sqlite_file = os.path.join(vector_store_path, "chroma.sqlite3")
    if os.path.exists(sqlite_file):
      if not VectorStoreService._is_valid_sqlite(sqlite_file):
        # move aside with timestamp suffix to avoid data loss
        ts = int(time.time())
        backup_name = f"chroma.sqlite3.corrupt.{ts}"
        backup_path = os.path.join(vector_store_path, backup_name)
        try:
          shutil.move(sqlite_file, backup_path)
          logger.warning("Detected invalid sqlite at %s. Renamed to %s. A new DB will be created.", sqlite_file, backup_path)
        except Exception as e:
          # If we can't move it, log and continue; creation may still fail and bubble up
          logger.exception("Failed to move corrupt sqlite file %s: %s", sqlite_file, str(e))

    try:
      return Chroma(persist_directory=vector_store_path,
                    collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
                    embedding_function=embedding_model)
    except Exception as e:
      # Surface a helpful message that mentions common causes
      msg = str(e)
      logger.exception("Failed to create vector store: %s", msg)
      raise Exception(
        f"Failed to create vector store: {msg}. If you see 'file is not a database' check for a git-lfs pointer at {sqlite_file}"
      )
