from dotenv import load_dotenv
import os

load_dotenv()

class Config:
  BOT_TOKEN = os.getenv("BOT_TOKEN")
  ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
