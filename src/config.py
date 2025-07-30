import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Memory Configuration ---
CHROMA_PERSIST_DIRECTORY = "data/chroma_db"
CHROMA_COLLECTION_NAME = "echomind_memory_gemini"
SQLITE_DB_PATH = "data/memory_metadata.db"

# --- Retrieval Configuration ---
# The relevance score threshold for recalling a memory.
# A higher value makes retrieval stricter (more relevant).
MEMORY_RELEVANCE_THRESHOLD = 0.65

# The number of top memories to fetch for relevance checking.
TOP_K_MEMORIES = 3

# --- Google Gemini Models ---
# Note: Using specific model names for clarity
EMBEDDING_MODEL = "models/text-embedding-004"
CHAT_MODEL = "gemini-2.5-flash-lite"
MEMORY_ANALYST_MODEL = "gemini-2.5-flash-lite" # Faster and cheaper for analysis