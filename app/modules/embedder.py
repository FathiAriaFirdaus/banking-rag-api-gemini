import pickle
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import EMBEDDING_PATH

class Embedder:
    def __init__(self):
        self.embedding_model = None
        self.embedding_path = EMBEDDING_PATH
    
    def load_embedding_model(self):
        """Load pre-trained embedding model"""
        try:
            with open(self.embedding_path, 'rb') as f:
                self.embedding_model = pickle.load(f)
            print("Embedding model loaded successfully")
            return self.embedding_model
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            raise e
    
    def get_embedding_model(self):
        """Get embedding model, load if not already loaded"""
        if self.embedding_model is None:
            return self.load_embedding_model()
        return self.embedding_model