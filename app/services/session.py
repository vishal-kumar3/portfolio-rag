import time
import secrets
import hashlib

from main import app


class SessionManager:

  def __init__(self):
    self.chat_session = app.state.chat_session

  def generate_user_id(self):
    user_id = None
    retry = 3
    while user_id or retry:
      user_id = self.generate_id()
      if self.chat_session.id_exists(user_id):
        retry -= 1
        user_id = None

    return user_id

  def generate_id(self):
    timestamp = str(int(time.time() * 1000))
    random_bytes = secrets.token_hex(8)
    raw_string = f"{timestamp}{random_bytes}"

    hash_object = hashlib.sha256(raw_string.encode())
    id = hash_object.hexdigest()[:32]

    return id
