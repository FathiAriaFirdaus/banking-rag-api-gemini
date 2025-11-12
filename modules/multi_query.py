from langchain_community.llms import Ollama
from modules.retriever import Retriever
from config import OLLAMA_CONFIG

class MultiQuerySystem:
    def __init__(self):
        self.llm = None
        self.retriever = Retriever()
    
    def setup_llm(self):
        """Setup LLM for multi-query retrieval"""
        try:
            self.llm = Ollama(**OLLAMA_CONFIG)
            print("LLM setup successfully")
            return self.llm
        except Exception as e:
            print(f"Error setting up LLM: {e}")
            raise e
    
    def get_llm(self):
        """Get LLM instance"""
        if self.llm is None:
            return self.setup_llm()
        return self.llm
    
    def setup_rag_system(self):
        """Setup complete RAG system with multi-query retriever"""
        llm = self.get_llm()
        retriever = self.retriever.setup_retriever(llm)
        return retriever, llm
    
    def create_summary(self, documents, query, llm=None):
        """Create summary from retrieved documents"""
        if llm is None:
            llm = self.get_llm()
        
        try:
            all_text = ''
            for doc in documents:
                clean_text = ' '.join(doc.page_content.split())
                all_text += clean_text + '\n\n'

            summarization_prompt = f"""
            Berdasarkan informasi dari dokumen berikut, 
            buatlah RINGKASAN SINGKAT dan MUDAH DIPAHAMI  
            dalam Bahasa Indonesia 
            yang menjawab pertanyaan: "{query}"

            INFORMASI DOKUMEN:
            {all_text}

            RINGKASAN SINGKAT:
            """

            summary = llm.invoke(summarization_prompt)
            return summary
            
        except Exception as e:
            return f"Error creating summary: {e}"
    
    def generate_response(self, query):
        """Generate response using multi-query RAG system"""
        try:
            retriever, llm = self.setup_rag_system()
            results = retriever.invoke(query)
            
            if not results:
                return "Maaf, tidak menemukan informasi yang relevan untuk pertanyaan Anda."
            
            summary = self.create_summary(results, query, llm)
            return summary
            
        except Exception as e:
            return f"Error generating response: {e}"