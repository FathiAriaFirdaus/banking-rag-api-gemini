from langchain_classic.retrievers import MultiQueryRetriever
from modules.vector_database import VectorDatabase
from config import RETRIEVER_CONFIG

class Retriever:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.k = RETRIEVER_CONFIG["k"]
        self.retriever = None
    
    def setup_retriever(self, llm=None):
        """Setup retriever with optional LLM for multi-query"""
        vector_db_instance = self.vector_db.get_db()
        
        if llm:
            # Use multi-query retriever if LLM is provided
            self.retriever = MultiQueryRetriever.from_llm(
                retriever=vector_db_instance.as_retriever(
                    search_kwargs={"k": self.k}
                ),
                llm=llm
            )
            print("Multi-query retriever setup successfully")
        else:
            # Use basic retriever
            self.retriever = vector_db_instance.as_retriever(
                search_kwargs={"k": self.k}
            )
            print("Basic retriever setup successfully")
        
        return self.retriever
    
    def get_relevant_documents(self, query, llm=None):
        """Get relevant documents for a query"""
        if self.retriever is None:
            self.setup_retriever(llm)
        
        return self.retriever.invoke(query)
    
    def simple_search(self, query, k=None):
        """Simple similarity search without LLM"""
        if k is None:
            k = self.k
        
        vector_db_instance = self.vector_db.get_db()
        return vector_db_instance.similarity_search(query, k=k)