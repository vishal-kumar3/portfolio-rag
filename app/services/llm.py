from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from app.core.config import settings


class LLMService:

  def __init__(self):
    self.embedding_model: GoogleGenerativeAIEmbeddings = self.create_embedding_model(
    )

  @staticmethod
  def create_embedding_model() -> GoogleGenerativeAIEmbeddings:
    try:
      return GoogleGenerativeAIEmbeddings(
          model=settings.EMBEDDING_MODEL_NAME,
          google_api_key=settings.MODEL_API_KEY)
    except Exception as e:
      raise Exception(f"Failed to create embedding model: {str(e)}")

  def get_chat_model(self, temp: float = 0.4) -> ChatGoogleGenerativeAI:
    try:
      return ChatGoogleGenerativeAI(model=settings.MODEL_NAME,
                                    google_api_key=settings.MODEL_API_KEY,
                                    temperature=temp)
    except Exception as e:
      raise Exception(f"Failed to create chat model: {str(e)}")
