from langchain_chroma import Chroma
from modules.embedder import Embedder
from config import CHROMA_PATH

class VectorDatabase:
    def __init__(self):
        self.vector_db = None
        self.embedder = Embedder()
        self.chroma_path = CHROMA_PATH
    
    def initialize_db(self):
        """Initialize Chroma vector database"""
        try:
            embedding_model = self.embedder.get_embedding_model()
            self.vector_db = Chroma(
                persist_directory=self.chroma_path, 
                embedding_function=embedding_model
            )
            print("Chroma DB initialized successfully")
            return self.vector_db
        except Exception as e:
            print(f"Error initializing Chroma DB: {e}")
            raise e
    
    def get_db(self):
        """Get vector database instance"""
        if self.vector_db is None:
            return self.initialize_db()
        return self.vector_db
    
    def add_documents(self, chunks, ids=None):
        """Add documents to vector database"""
        if self.vector_db is None:
            self.initialize_db()
        
        embedding_model = self.embedder.get_embedding_model()
        
        if ids is None:
            ids = [str(i) for i in range(len(chunks))]
        
        # Add documents to Chroma
        self.vector_db.from_documents(
            chunks, 
            embedding_model, 
            ids=ids, 
            persist_directory=self.chroma_path
        )
        print(f"Added {len(chunks)} documents to Chroma DB")
    
    def get_document_count(self):
        """Get number of documents in the database"""
        if self.vector_db is None:
            return 0
        return self.vector_db._collection.count()
    
    def similarity_search(self, query, k=5):
        """Perform similarity search"""
        if self.vector_db is None:
            self.initialize_db()
        
        return self.vector_db.similarity_search(query, k=k)
    
    def delete_documents(self, ids):
        """Delete documents by IDs"""
        if self.vector_db is None:
            self.initialize_db()
        
        self.vector_db.delete(ids=ids)
        print(f"Deleted {len(ids)} documents")
    
    def get_all_ids(self):
        """Get all document IDs in the database"""
        if self.vector_db is None:
            return []
        return self.vector_db.get()['ids']
    
    def get_all_documents(self):
        if self.vector_db is None:
            return []

        result = self.vector_db.get()
        documents = []

        for i in range(len(result['ids'])):
            documents.append({
                'id': result['ids'][i],
                'content': result['documents'][i],
                'metadata': result['metadatas'][i]
            })

        return documents
    