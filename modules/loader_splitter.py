from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from config import DOCUMENT_PATH, SPLITTER_CONFIG
import os

class DocumentLoaderSplitter:
    def __init__(self):
        self.chunk_size = SPLITTER_CONFIG["chunk_size"]
        self.chunk_overlap = SPLITTER_CONFIG["chunk_overlap"]
        self.header_to_split = [
            ('#', 'Header1'),
            ('##', 'Header2'),
            ('###', 'Header3')
        ]

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.header_to_split,
            strip_headers=False
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )

    def load_and_split(self, file_path: str):
        """
        Main method to load and split documents based on file type
        Support both excel and markdown file
        """

        try:
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".md":
                return self._process_markdown(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                return self._process_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Only .md, .xlsx, .xls are supported")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            raise e

    def _process_markdown(self, file_path: str):
        """Process markdown file using header based splitter"""
        try:
            # Load markdown file
            with open(file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            print(f"Loaded markdown file: {file_path}")

            # Split by header
            docs = self.markdown_splitter.split_text(markdown_content)
            print(f"Created {len(docs)} documents from markdown headers")

            return docs
        except Exception as e:
            print(f"error processing markdown file: {e}")
            raise e
        
    def _process_excel(self, file_path: str):
        """Process excel file using text splitter"""
        try:
            # Load excel file
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            print(f"Loaded {len(documents)} documents from Excel: {file_path}")

            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            print(f"Split Excel documents into {len(chunks)} chunks")

            return chunks
        except Exception as e:
            print(f"Error loading Excel document: {e}")
            raise e
        
    # LEGACY METHOD FOR BACKWARD COMPATIBILITY
    
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
