import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi path (TETAP SAMA)
DOCUMENT_PATH = "rancangan-pkpb-tabungan-2023.md"
EMBEDDING_PATH = "../data/embeddings/all-MiniLM-L6-v2.pkl"
CHROMA_PATH = "../data/vector_db/chroma_db"

# Gemini Configuration (BARU)
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY"),  # Ganti dengan API key Anda
    "model": "gemini-2.5-flash",
    "temperature": 0.3,
    "max_tokens": 1000
}

# Text Splitting Configuration (TETAP SAMA)
SPLITTER_CONFIG = {
    "chunk_size": 380,
    "chunk_overlap": 100
}

# Retrieval Configuration (TETAP SAMA)
RETRIEVER_CONFIG = {
    "k": 3
}