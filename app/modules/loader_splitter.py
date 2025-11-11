from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from config import DOCUMENT_PATH, SPLITTER_CONFIG

class DocumentLoaderSplitter:
    def __init__(self):
        self.chunk_size = SPLITTER_CONFIG["chunk_size"]
        self.chunk_overlap = SPLITTER_CONFIG["chunk_overlap"]
    
    def load_document(self, document_path=None):
        """Load document from Excel file"""
        if document_path is None:
            document_path = DOCUMENT_PATH
            
        try:
            loader = UnstructuredExcelLoader(document_path)
            documents = loader.load()
            print(f"Loaded {len(documents)} documents from {document_path}")
            return documents
        except Exception as e:
            print(f"Error loading document: {e}")
            raise e
    
    def split_documents(self, documents, chunk_size=None, chunk_overlap=None):
        """Split documents into chunks"""
        if chunk_size is None:
            chunk_size = self.chunk_size
        if chunk_overlap is None:
            chunk_overlap = self.chunk_overlap
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Split documents into {len(chunks)} chunks")
        return chunks
    
    def create_chunks(self, document_path=None):
        """Complete process: load and split documents"""
        documents = self.load_document(document_path)
        chunks = self.split_documents(documents)
        return chunks
    
class MarkdownLoaderSplitter:
    def __init__(self):
        self.header_to_split = [
            ('#', 'Header1'),
            ('##', 'Header2'),
            ('###', 'Header3')
        ]

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.header_to_split,
            strip_headers=False
        )

    def load_and_split(self, file_path: str):
        try:
            # Load markdown file
            with open(file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            print(f"Loaded mardown file: {file_path}")

            # Split by header
            docs = self.markdown_splitter.split_text(markdown_content)
            print(f"Created {len(docs)} documents from headers")

            return docs
        
        except Exception as e:
            print(f"Error processing markdown file: {e}")
            raise e
