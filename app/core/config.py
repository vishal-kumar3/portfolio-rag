from typing import List
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

  # USER DETAILS
  USER_NAME: str = "Vishal"

  # RAG
  MODEL_PROVIDER: str
  MODEL_NAME: str
  EMBEDDING_MODEL_NAME: str
  MODEL_API_KEY: SecretStr
  VECTOR_STORE_PATH: str
  VECTOR_STORE_COLLECTION_NAME: str
  RAG_DOCUMENT_PATH: str

  # API
  API_V1_PREFIX: str = "/api/v1"
  CORS_ORIGINS: List[str] = ["*"]
  CORS_ALLOW_CREDENTIALS: bool = True
  CORS_ALLOW_METHODS: List[str] = ["*"]
  CORS_ALLOW_HEADERS: List[str] = ["*"]

  class Config:
    env_file = ".env"


settings = Settings()
