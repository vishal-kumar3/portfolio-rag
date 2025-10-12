from pydantic import BaseModel

class ChatBotQuerySchema(BaseModel):
  query: str
