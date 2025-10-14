from dataclasses import dataclass
from typing import List, Tuple
from langchain_core.messages import BaseMessage

from app.services.prompt import Prompt_Template
from app.services.session import SessionManager


@dataclass
class Chat:
  id: str
  chat_history: List[BaseMessage]


class ChatSession:

  def __init__(self, session_manager: SessionManager,
               prompt_template: Prompt_Template):
    self._chat_history: List[Chat] = []
    self.prompt_service = prompt_template
    self.session_manager = session_manager

  def id_exists(self, user_id: str) -> bool:
    for chat in self._chat_history:
      if chat.id == user_id:
        return True
    return False

  def get_raw_chat_history(self, user_id: str) -> List[BaseMessage] | None:
    for chat in self._chat_history:
      if chat.id == user_id:
        return chat.chat_history
    return None

  def create_chat(self) -> Tuple[List[BaseMessage], str]:
    user_id = self.session_manager.generate_id()
    chat = Chat(id=user_id, chat_history=[])
    self._chat_history.append(chat)
    return chat.chat_history, user_id

  def get_chat_history(self, user_id: str) -> str:
    chat_history = self.get_raw_chat_history(user_id)

    if chat_history is None:
      chat_history, user_id = self.create_chat()

    def seed_initial_prompt():
      if not len(chat_history):
        prompt = self.prompt_service.inject_initial_prompt()
        return prompt
      return ''

    return seed_initial_prompt() + "\n".join([
        f"{'Human' if i % 2 == 0 else 'Assistant'}: {msg.content}"
        for i, msg in enumerate(chat_history)
    ])

  def add_message(self, user_id: str, message: BaseMessage):
    chat_history = self.get_raw_chat_history(user_id)
    if chat_history is not None:
      chat_history.append(message)
