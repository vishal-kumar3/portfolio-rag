from dataclasses import dataclass
from typing import List, Dict, Tuple
from langchain_core.messages import BaseMessage, HumanMessage

from app.services.id_generator import IDGenerator
from app.services.prompt import Prompt_Template


@dataclass
class Chat:
  id: str
  chat_history: List[BaseMessage]


class ChatSession:

  def __init__(self, prompt_template: Prompt_Template):
    self._chat_history: Dict[str, List[BaseMessage]] = {}
    self.prompt_service = prompt_template
    self._active_sessions = set()

  def get_raw_chat_history(self, chat_id: str) -> List[BaseMessage] | None:
    return self._chat_history.get(chat_id)

  def create_chat(self) -> Tuple[List[BaseMessage], str]:
    user_id = self.generate_user_id()
    self._chat_history[user_id] = []
    return self._chat_history[user_id], user_id

  def get_chat_history(self, user_id: str) -> str:
    chat_history = self.get_raw_chat_history(user_id)

    if chat_history is None:
      raise ValueError("No chat found!")

    def seed_initial_prompt():
      if not len(chat_history):
        prompt = self.prompt_service.inject_initial_prompt()
        return prompt
      return ''

    return seed_initial_prompt() + "\n".join([
        f"{'Human' if i % 2 == 0 else 'Assistant'}: {msg.content}"
        for i, msg in enumerate(chat_history)
    ])

  def get_chat_history_for_user(self, user_id: str):
    chat_history = self.get_raw_chat_history(user_id)
    if chat_history is None:
      return []

    user_chat_history = [{
        "user": msg.content
    } if isinstance(msg, HumanMessage) else {
        "ai": msg.content
    } for msg in chat_history]
    return user_chat_history

  def add_message(self, user_id: str, message: BaseMessage):
    chat_history = self.get_raw_chat_history(user_id)
    if chat_history is not None:
      chat_history.append(message)

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

  def session_exists(self, session_id: str) -> bool:
    return session_id in self._active_sessions

  def remove_session(self, session_id: str) -> None:
    if session_id in self._active_sessions:
      self._active_sessions.remove(session_id)
