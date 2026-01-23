"""
FastAPI Backend for RAgent Mobile App
Provides REST API endpoints for document management, Q&A, quiz, and summarization
"""

import os
import hashlib
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

# Existing modules
from src.ingestion.document_loader import DocumentLoader
from src.embedding.vector_db import VectorDatabase
from src.rag.rag_system import RAGSystem
from src.rag.quiz_generator import QuizGenerator
from src.rag.summarizer import Summarizer
from src.utils.voice import VoiceHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAgent API",
    description="Intelligent Document Q&A System with RAG",
    version="1.0.0"
)

# CORS settings for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mobile app'ten gelecek istekler için
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
doc_loader = DocumentLoader()
vector_db = VectorDatabase()
rag_system = RAGSystem()
quiz_gen = QuizGenerator()
summarizer = Summarizer()
voice_handler = VoiceHandler()

# In-memory document storage (gelecekte database'e taşınabilir)
documents_store = {}

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
    
class QuizRequest(BaseModel):
    document_ids: Optional[List[str]] = None
    num_questions: int = 5
    difficulty: str = "orta"
    
class SummaryRequest(BaseModel):
    document_ids: Optional[List[str]] = None
    summary_type: str = "genel"  # genel, detaylı, madde
    
class DocumentLabel(BaseModel):
    doc_id: str
    labels: List[str]
    
class DocumentStatus(BaseModel):
    doc_id: str
    is_active: bool


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "message": "RAgent API is running",
        "version": "1.0.0",
        "endpoints": ["/docs", "/upload", "/documents", "/question", "/quiz", "/summary"]
    }


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    labels: Optional[str] = Form(None)
):
    """
    Upload a document (PDF, DOCX, PPTX, TXT)
    Returns: Document ID and metadata
    """
    try:
        # Create temp directory
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded file
        temp_path = os.path.join(temp_dir, file.filename)
        content = await file.read()
        
        logger.info(f"Uploading: {file.filename}, size: {len(content)} bytes")
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Generate unique document ID
        file_hash = hashlib.md5(content).hexdigest()[:8]
        doc_id = f"{file_hash}_{file.filename}"
        
        # Load and process document
        chunks = doc_loader.load_document(temp_path)
        logger.info(f"Document split into {len(chunks)} chunks")
        
        # Store in vector database
        label_list = labels.split(",") if labels else []
        metadata = {
            "source": file.filename,
            "doc_id": doc_id,
            "labels": ",".join(label_list) if label_list else "",
            "is_active": True
        }
        
        chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        vector_db.add_documents(chunks, metadatas=[metadata] * len(chunks), ids=chunk_ids)
        
        # Store document info
        documents_store[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "size": len(content),
            "chunks": len(chunks),
            "labels": label_list,
            "is_active": True
        }
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return JSONResponse({
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks),
            "message": f"{file.filename} başarıyla yüklendi"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/documents")
async def get_documents():
    """
    Get list of all uploaded documents
    Returns: List of documents with metadata
    """
    try:
        docs = list(documents_store.values())
        return JSONResponse({
            "success": True,
            "count": len(docs),
            "documents": docs
        })
    except Exception as e:
        logger.error(f"Get documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the database"""
    try:
        if doc_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove from vector DB (tüm chunk'ları sil)
        vector_db.collection.delete(where={"doc_id": doc_id})
        
        # Remove from store
        doc_info = documents_store.pop(doc_id)
        
        return JSONResponse({
            "success": True,
            "message": f"{doc_info['filename']} silindi"
        })
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/question")
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded documents
    Returns: Answer with sources
    """
    try:
        # Filter by document IDs if specified
        allowed_sources = None
        if request.document_ids:
            allowed_sources = [documents_store[doc_id]["filename"] 
                             for doc_id in request.document_ids 
                             if doc_id in documents_store]
        
        # Get answer from RAG system (pass vector_db and proper params)
        result = rag_system.process_question(
            request.question,
            vector_db,
            k_results=5,
            allowed_sources=allowed_sources,
            return_sources=True,
        )
        
        return JSONResponse({
            "success": True,
            "question": request.question,
            "answer": result.get("answer", "Cevap bulunamadı"),
            "sources": result.get("sources", []),
            "search_results": result.get("search_results", [])
        })
        
    except Exception as e:
        logger.error(f"Question error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate quiz questions from documents
    Returns: List of quiz questions
    """
    try:
        # Get document text
        allowed_sources = None
        if request.document_ids:
            allowed_sources = [documents_store[doc_id]["filename"] 
                             for doc_id in request.document_ids 
                             if doc_id in documents_store]
        
        # Search relevant context
        context_results = vector_db.search(
            query="genel içerik",
            k=10,
            allowed_sources=allowed_sources
        )
        
        document_text = "\n\n".join([r["text"] for r in context_results])
        
        # Generate quiz
        questions = quiz_gen.generate_quiz(
            document_text=document_text,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        return JSONResponse({
            "success": True,
            "count": len(questions),
            "questions": questions
        })
        
    except Exception as e:
        logger.error(f"Quiz error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/summary")
async def generate_summary(request: SummaryRequest):
    """
    Generate summary of documents
    Returns: Summary text
    """
    try:
        # Get document text
        allowed_sources = None
        if request.document_ids:
            allowed_sources = [documents_store[doc_id]["filename"] 
                             for doc_id in request.document_ids 
                             if doc_id in documents_store]
        
        # Get all document chunks
        all_results = vector_db.search(
            query="genel içerik özet",
            k=20,
            allowed_sources=allowed_sources
        )
        
        document_text = "\n\n".join([r["text"] for r in all_results])
        
        # Map Turkish summary types to internal keys and generate summary
        mapping = {
            'genel': 'general',
            'detaylı': 'detailed',
            'madde': 'bullet'
        }
        summary_type = mapping.get(request.summary_type, 'general')
        summary = summarizer.summarize(
            document_text=document_text,
            summary_type=summary_type
        )
        
        return JSONResponse({
            "success": True,
            "summary": summary,
            "type": request.summary_type
        })
        
    except Exception as e:
        logger.error(f"Summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/labels")
async def update_labels(request: DocumentLabel):
    """Update document labels"""
    try:
        if request.doc_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        documents_store[request.doc_id]["labels"] = request.labels
        
        return JSONResponse({
            "success": True,
            "message": "Labels updated"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/status")
async def update_status(request: DocumentStatus):
    """Toggle document active/inactive status"""
    try:
        if request.doc_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        documents_store[request.doc_id]["is_active"] = request.is_active
        
        return JSONResponse({
            "success": True,
            "message": f"Document {'activated' if request.is_active else 'deactivated'}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/database/clear")
async def clear_database():
    """Clear entire vector database"""
    try:
        vector_db.clear_database()
        documents_store.clear()
        
        return JSONResponse({
            "success": True,
            "message": "Database cleared"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting RAgent API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
