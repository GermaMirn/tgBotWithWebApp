from pydantic import BaseModel

class TelegramMiniAppPayload(BaseModel):
  id: int
  username: str
  full_name: str
