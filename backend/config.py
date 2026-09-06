import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load .env from backend or project root
load_dotenv(BASE_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")

# Configuration settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'gramvantage.db'}")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

BUSINESSES_FILE = DATA_DIR / "businesses.json"
SCHEMES_FILE = DATA_DIR / "schemes.json"
