import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE = os.getenv("DATABASE_PATH", str(BASE_DIR / "legal_xray.db"))
API_KEY = os.getenv("OPENAI_API_KEY", "")
IS_GROQ = API_KEY.startswith("gsk_")
MODEL = os.getenv("OPENAI_MODEL") or ("openai/gpt-oss-20b" if IS_GROQ else "gpt-4o-mini")
VISION_MODEL = os.getenv("OPENAI_VISION_MODEL") or (
    "qwen/qwen3.8-27b" if IS_GROQ else MODEL
)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or (
    "https://api.groq.com/openai/v1" if IS_GROQ else None
)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
MAX_TEXT_LENGTH = 30000
RATE_LIMIT = 10
RATE_WINDOW_SECONDS = 3600
CLIENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,80}$")
IMG_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", *IMG_TYPES}
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
