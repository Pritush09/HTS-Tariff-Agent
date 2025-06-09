# Configuration settings
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads"
PROCESSED_DIR = DATA_DIR / "processed"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Create directories if they don't exist
for dir_path in [DATA_DIR, DOWNLOADS_DIR, PROCESSED_DIR, VECTORSTORE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# HTS Data Configuration
HTS_BASE_URL = "https://hts.usitc.gov"
GENERAL_NOTES_URL = f"{HTS_BASE_URL}/view/General%20Notes%20Full%20Documentation"
HTS_SECTION_I_URL = f"{HTS_BASE_URL}/chapters/1-5"

# Database Configuration
DATABASE_PATH = PROCESSED_DIR / "hts_data.db"
VECTOR_STORE_PATH = str(VECTORSTORE_DIR)

# Agent Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000
TEMPERATURE = 0.1

# Streamlit Configuration
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"