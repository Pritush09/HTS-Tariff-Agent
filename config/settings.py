# Configuration settings
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "deepseek/deepseek-r1-0528:free"
HTS_DATA_DIR = "data/downloads/"
VECTORSTORE_DIR = "data/vectorstore/"