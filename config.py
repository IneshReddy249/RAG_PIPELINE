from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment")
if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not found in environment")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Chunking
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Embedding
EMBEDDING_MODEL = "text-embedding-3-small"

# Vector Store
CHROMA_COLLECTION_NAME = "rag_documents"

# Retrieval
TOP_K = 5
SIMILARITY_THRESHOLD = 0.3

# LLM
LLM_MODEL = "meta/llama-3.1-8b-instruct"
LLM_BASE_URL = "https://integrate.api.nvidia.com/v1"
TEMPERATURE = 0.1
MAX_TOKENS = 512