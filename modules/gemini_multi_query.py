from modules.retriever import Retriever
from modules.gemini_llm import GeminiLLM

class GeminiMultiQuery:
    def __init__(self):
        self.llm_wrapper = GeminiLLM()
        self.llm_model = None
        self.retriever_builder = Retriever()

    def setup(self):
        # Setup LLM
        self.llm_model = self.llm_wrapper.setup()
        print('Gemini Multi-Query System Ready')

    # def generate_query(self, question):
    #     prompt = f"""
    #     Buat 2 variasi pertanyaan dari: "{question}"
    #     Variasi harus sama artinya tapi pakai kata berbeda.
    #     Format: 1. [pertanyaan1] 2. [pertanyaan2]
    #     """

    #     try:
    #         response = self.llm.ask(prompt=prompt)

    #         # Extract queries from response
    #         queries = [question]

    #         # This part spilt the response from 
    #         # ['1. question'] > ['1.', 'question'] > [question]
    #         # and then append it to queries
    #         lines = response.split('\n')
    #         for line in lines:
    #             line = line.strip()
    #             if line.startswith(('1.', '2.', '3.')):
    #                 query = line.split('.', 1)[1].strip()
    #                 if query and query != question:
    #                     queries.append(query)

    #         return queries[:3]

    #     except Exception as e:
    #         return [question, f"jelaskan {question}"]
        
    # def search_document(self, question):
    #     queries = self.generate_query(question)
    #     print(f"Searching with: {queries}")

    #     all_docs = []
    #     retriever = self.retriever.setup_retriever()

    #     for query in queries:
    #         docs = retriever.get_relevant_documents(query)
    #         all_docs.extend(docs)
    #         print(f"Found {len(docs)} docs for: {query}")

    #     # Remove dupliacte
    #     unique_docs = []
    #     seen = set()

    #     for doc in all_docs:
    #         content_id = doc.page_content[:50]
    #         if content_id not in seen:
    #             seen.add(content_id)
    #             unique_docs.append(doc)

    #     print(f"Total unique docs: {len(unique_docs)}")
    #     return unique_docs
    
    def create_answer(self, question, documents):
        if not documents:
            return "No Relevant Information Found"
        
        # Prepare context
        context = "\n---\n".join([doc.page_content for doc in documents])

        # Simple prompt
        prompt = f"""
        Anda adalah asisten AI yang ahli.
        Berdasarkan informasi dari dokumen berikut, 
        buatlah jawaban yang jelas dan ringkas dalam Bahasa Indonesia
        untuk menjawab pertanyaan: "{question}"

        INFORMASI DOKUMEN (KONTEKS):
        ---
        {context}
        ---

        # JAWABAN: 
        # Jika konteks dokumen tidak memuat informasi spesifik untuk menjawab pertanyaan tersebut, balas dengan sopan bahwa Anda tidak dapat menemukan informasi yang relevan di dokumen.
        # """

        return self.llm_wrapper.ask(prompt)
    
    def chat(self, question):
        # MAIN CHAT METHOD (NEW LOGIC)
        try:
            # # Step 1: search documents
            # documents = self.search_document(question)
            # # Step2: create answer
            # answer = self.create_answer(question, documents)
            # return answer

            # LOGIKA RAG YANG BENAR
            # 1. Setup Retriever dan Berikan LLM Model (Dari LangChain)
            # ini akan memicu blok `if llm:` di retriever.py
            print('Setting up MultiQueryRetriever...')
            multi_query_retriever = self.retriever_builder.setup_retriever(llm=self.llm_model)

            # 2. Panggil Retrievernya
            # LangChain akan otomatis membuat query dan mencari dokumen
            print(f"Invoking MultiQueryRetriever for {question}") 
            documents = multi_query_retriever.invoke(question)

            print("\n--- KONTEN DOKUMEN YANG DITEMUKAN ---")
            for i, doc in enumerate(documents):
                print(f"[{i+1}] {doc.page_content[:150]}...") # Cetak 150 karakter pertama
            print("----------------------------------\n")

            print(f"Found {len(documents)} unique docs.")

            # 3. Buat Jawaban Berdasarkan Dokumen
            answer = self.create_answer(question, documents)
            return answer
        
        except Exception as e:
            return f"System error: {str(e)}"

