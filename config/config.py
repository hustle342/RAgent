"""
RAgent Konfigürasyon Dosyası
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Proje yolu
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Database
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', str(PROJECT_ROOT / 'data' / 'chroma_db'))
COLLECTION_NAME = "documents"

# Embedding
EMBEDDING_MODEL = os.getenv(
    'EMBEDDING_MODEL',
    'sentence-transformers/all-MiniLM-L6-v2'
)
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2'nin çıktı boyutu

# Text Processing
CHUNK_SIZE = 1000  # Karakterde
CHUNK_OVERLAP = 200

# Groq API
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = "llama-3.1-70b-versatile"

# Search
SEARCH_K_RESULTS = 5  # Benzer dokümanları kaç tane döndüreceği

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Streamlit
STREAMLIT_PAGE_CONFIG = {
    "page_title": "RAgent 🤖",
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
