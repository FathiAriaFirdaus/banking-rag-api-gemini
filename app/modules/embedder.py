import pickle
import os
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import EMBEDDING_PATH

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self):
        self.embedding_model = None
        self.embedding_path = EMBEDDING_PATH
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def download_embedding_model(self):
        # Download and save embedding model
        try:
            logger.info(f"Downloading embedding model: {self.model_name}")
            huggingface_embedding = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            # Create directory if does not exist
            os.makedirs(os.path.dirname(self.embedding_path), exist_ok=True)

            # Test the model before saving
            test_embedding = huggingface_embedding.embed_query('test')
            logger.info(f"Model test successfull, embedding dimension: {len(test_embedding)}")

            # Save the model
            with open(self.embedding_path, 'wb') as f:
                pickle.dump(huggingface_embedding, f)

            logger.info(f"Embedding model saved to: {self.embedding_path}")
            return huggingface_embedding
        
        except Exception as e:
            logger.error(f"Error downloading embedding model: {e}")
            raise e
    
    def load_embedding_model(self):
        # Load pretrained model, download if doesnt exist
        try:
            # check if embedding model exist
            if not os.path.exists(self.embedding_path):
                logger.warning(f"Embedding model not found at {self.embedding_path}")
                return self.download_embedding_model()
            
            # Verify file is not corrupt
            file_size = os.path.getsize(self.embedding_path)
            if file_size == 0:
                logger.warning("Embedding file is empty, re-downloading...")
                return self.download_embedding_model()
            
            # Load existing model
            with open(self.embedding_path, 'rb') as f:
                self.embedding_model = pickle.load(f)

            # Test if the loaded model works
            test_embedding = self.embedding_model.embed_query("test")
            logger.info(f"Embedding model loaded successfully, dimension: {len(test_embedding)}")
            return self.embedding_model
        
        except (pickle.PickleError, EOFError, AttributeError) as e:
            logger.error(f"Embedding file corrupted: {e}")
            logger.info("Downloading fresh model...")
            return self.download_embedding_model()

        except Exception as e:
            logger.error(f"Unexpected error loading embedding model: {e}")
            logger.info("Attempting to download fresh model...")
            return self.download_embedding_model()
    
    def get_embedding_model(self):
        """Get embedding model, load if not already loaded"""
        if self.embedding_model is None:
            return self.load_embedding_model()
        return self.embedding_model
    
    def force_reload(self):
        # force reload of embedding model (for updates)
        self.embedding_model = None
        return self.get_embedding_model()