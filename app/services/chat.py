from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from langchain_core.messages import BaseMessage, HumanMessage

from app.core.config import settings
from app.services.id_generator import IDGenerator
from app.services.prompt import Prompt_Template


@dataclass
class Chat:
  last_seen: datetime = field(default_factory=datetime.now)
  created_at: datetime = field(default_factory=datetime.now)
  chat_history: List[BaseMessage] = field(default_factory=list)


class ChatSession:

  def __init__(self, prompt_template: Prompt_Template):
    self._chat_history: Dict[str, Chat] = {}
    self.prompt_service = prompt_template
    self._active_sessions = set()
    self.max_inactivity = timedelta(days=2)
    self.max_chat_length = 50

  def get_raw_chat_history(self, chat_id: str) -> List[BaseMessage] | None:
    chat = self._chat_history.get(chat_id)
    return chat.chat_history if chat else []

  def get_chat(self, chat_id: str) -> Chat | None:
    return self._chat_history.get(chat_id)

  def create_chat(self) -> Tuple[Chat, str]:
    user_id = self.generate_user_id()
    self._chat_history[user_id] = Chat()
    return self._chat_history[user_id], user_id

  def get_chat_history(self, user_id: str) -> str:
    chat_history = self.get_raw_chat_history(user_id)

    if chat_history is None:
      raise ValueError("No chat found!")

    def seed_initial_prompt():
      if not len(chat_history) or len(chat_history) == 1:
        prompt = self.prompt_service.inject_system_prompt(
            settings.USER_NAME, settings.ASSISTANT_NAME)
        return prompt
      return ''

    return seed_initial_prompt() + "\n".join([
        f"{'Visitor' if isinstance(msg, HumanMessage) else settings.ASSISTANT_NAME}: {msg.content}"
        for msg in chat_history
    ])

  def get_chat_history_for_user(self, user_id: str):
    chat_history = self.get_raw_chat_history(user_id)
    if chat_history is None:
      return []

    user_chat_history = [{
        "user": msg.content
    } if isinstance(msg, HumanMessage) else {
        settings.ASSISTANT_NAME: msg.content
    } for msg in chat_history]
    return user_chat_history

  def add_message(self, user_id: str, message: BaseMessage):
    chat = self.get_chat(user_id)
    if chat is not None:
      chat.last_seen = datetime.now()
      chat.chat_history.append(message)

  def generate_user_id(self) -> str:
    user_id = None
    retry = 3
    while retry > 0:
      potential_id = IDGenerator.generate_id()
      if potential_id not in self._active_sessions:
        user_id = potential_id
        self._active_sessions.add(user_id)
        break
      retry -= 1

    if user_id is None:
      raise RuntimeError("Failed to generate unique session ID")

    return user_id

  def session_exists(self, user_id: str) -> bool:
    return True if self._chat_history.get(user_id) else False

  def remove_inactive_session(self):
    expired_sessions_ids = []
    for id, chat in self._chat_history.items():
      if (datetime.now() - chat.last_seen > self.max_inactivity) or len(
          chat.chat_history) > self.max_chat_length:
        expired_sessions_ids.append(id)

    for id in expired_sessions_ids:
      del self._chat_history[id]
