from pydantic import BaseModel
from typing import Optional

class TelegramMiniAppPayload(BaseModel):
  id: int
  username: str
  full_name: str
  chat_id: Optional[int] = None
