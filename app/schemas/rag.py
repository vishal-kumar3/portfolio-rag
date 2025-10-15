from typing import Optional
from pydantic import BaseModel


class ChatBotQuerySchema(BaseModel):
  query: str
  userId: Optional[str] = None
