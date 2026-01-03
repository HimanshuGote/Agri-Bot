"""
Document Processor Module
Handles PDF loading, text chunking, embedding generation, and vector store creation
"""

import os
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

class DocumentProcessor:
    """
    Processes PDF documents and creates separate vector stores for
    Disease and Scheme knowledge bases
    """
    
    def __init__(self):
        self.disease_pdf = "CitrusPlantPestsAndDiseases.pdf"
        self.scheme_pdf = "GovernmentSchemes.pdf"
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Text splitter with optimized settings for agricultural content
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Optimal for agricultural technical content
            chunk_overlap=200,  # Good overlap for context preservation
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.disease_vectorstore = None
        self.scheme_vectorstore = None
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """Load PDF and return documents"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📖 Loading {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        print(f"✓ Loaded {len(documents)} pages")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into optimized chunks"""
        print(f"✂️  Chunking documents...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    def add_metadata(self, chunks: List[Document], doc_type: str) -> List[Document]:
        """Add metadata to chunks for better retrieval"""
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "doc_type": doc_type,
                "chunk_id": i,
                "source_file": self.disease_pdf if doc_type == "disease" else self.scheme_pdf
            })
        return chunks
    
    def create_vectorstore(self, chunks: List[Document], collection_name: str) -> Chroma:
        """Create Chroma vector store from chunks"""
        print(f"🔍 Creating vector store: {collection_name}...")
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory=f"./chroma_db/{collection_name}"
        )
        
        print(f"✓ Vector store created with {len(chunks)} embeddings")
        return vectorstore
    
    def process_documents(self):
        """
        Main processing pipeline:
        1. Load PDFs
        2. Chunk text
        3. Add metadata
        4. Create vector stores
        """
        try:
            # Process Disease Knowledge Base
            print("\n📚 Processing Citrus Disease Knowledge Base...")
            disease_docs = self.load_pdf(self.disease_pdf)
            disease_chunks = self.chunk_documents(disease_docs)
            disease_chunks = self.add_metadata(disease_chunks, "disease")
            
            self.disease_vectorstore = self.create_vectorstore(
                disease_chunks,
                "citrus_diseases"
            )
            
            # Process Scheme Knowledge Base
            print("\n📚 Processing Government Schemes Knowledge Base...")
            scheme_docs = self.load_pdf(self.scheme_pdf)
            scheme_chunks = self.chunk_documents(scheme_docs)
            scheme_chunks = self.add_metadata(scheme_chunks, "scheme")
            
            self.scheme_vectorstore = self.create_vectorstore(
                scheme_chunks,
                "government_schemes"
            )
            
            print("\n✅ All documents processed successfully!")
            
        except Exception as e:
            print(f"❌ Error processing documents: {str(e)}")
            raise
    
    def get_disease_retriever(self, k: int = 4):
        """Get retriever for disease knowledge base"""
        if not self.disease_vectorstore:
            raise ValueError("Disease vector store not initialized")
        return self.disease_vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    
    def get_scheme_retriever(self, k: int = 4):
        """Get retriever for scheme knowledge base"""
        if not self.scheme_vectorstore:
            raise ValueError("Scheme vector store not initialized")
        return self.scheme_vectorstore.as_retriever(
            search_kwargs={"k": k}
        )

if __name__ == "__main__":
    # Test document processing
    processor = DocumentProcessor()
    processor.process_documents()
    print("Document processing test completed!")
