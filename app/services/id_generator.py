import time
import secrets
import hashlib


class IDGenerator:

  @staticmethod
  def generate_id() -> str:
    timestamp = str(int(time.time() * 1000))
    random_bytes = secrets.token_hex(8)
    raw_string = f"{timestamp}{random_bytes}"

    hash_object = hashlib.sha256(raw_string.encode())
    id = hash_object.hexdigest()[:32]

    return id
