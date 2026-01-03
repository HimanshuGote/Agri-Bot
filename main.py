"""
Agriculture Chatbot - FastAPI Backend
Intelligent RAG system for Citrus Disease and Government Schemes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Import custom modules
from agent import AgricultureAgent
from document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Agriculture Chatbot API",
    description="Intelligent backend for farmers to get information about citrus diseases and government schemes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
doc_processor = None
agent = None

# Request/Response Models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    intent: str
    answer: str
    sources: Optional[list] = []
    confidence: Optional[float] = None

@app.on_event("startup")
async def startup_event():
    """Initialize document processing and agent on startup"""
    global doc_processor, agent
    
    print("🚀 Starting Agriculture Chatbot...")
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Process PDFs and create vector stores
    print("📄 Processing documents...")
    doc_processor.process_documents()
    
    # Initialize agent
    print("🤖 Initializing agent...")
    agent = AgricultureAgent(
        disease_vectorstore=doc_processor.disease_vectorstore,
        scheme_vectorstore=doc_processor.scheme_vectorstore
    )
    
    print("✅ System ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Agriculture Chatbot API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "document_processor": doc_processor is not None,
            "agent": agent is not None,
            "vector_stores": {
                "disease": doc_processor.disease_vectorstore is not None if doc_processor else False,
                "scheme": doc_processor.scheme_vectorstore is not None if doc_processor else False
            }
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Main query endpoint for farmers
    
    Analyzes farmer's question, routes to appropriate knowledge base(s),
    and returns contextual answer with citations.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Process query through agent
        result = agent.process_query(request.question)
        
        return QueryResponse(
            success=True,
            intent=result["intent"],
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence=result.get("confidence")
        )
    
    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/test-intent")
async def test_intent(request: QueryRequest):
    """Test endpoint to check intent detection"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        intent = agent.detect_intent(request.question)
        return {
            "question": request.question,
            "detected_intent": intent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    if not doc_processor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {
        "total_documents": 2,
        "vector_stores": {
            "disease_kb": {
                "status": "active",
                "document": "CitrusPlantPestsAndDiseases.pdf"
            },
            "scheme_kb": {
                "status": "active", 
                "document": "GovernmentSchemes.pdf"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
