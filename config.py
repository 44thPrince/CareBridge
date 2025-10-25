import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "carebridgedb")
DB_USER = os.getenv("DB_USER", "nazeershaikh")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
