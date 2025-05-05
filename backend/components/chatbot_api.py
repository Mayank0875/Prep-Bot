"""
FastAPI server for the university chatbot
"""
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

import os
import shutil
import uuid
from typing import List

from components.qa_utils import create_qa_chain, answer_question, load_vector_db_from_persist_dir
from components.vectordb_builder import process_pdf_directory


# Create the FastAPI app
app = FastAPI(title="University Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRESIST_DIR = os.path.join(BASE_DIR, "../artifacts/chroma_db")
DOCUMENTS_DIR = "documents"
# PRESIST_DIR = "/Users/mayankgupta/Desktop/Project/ExamBot/backend/artifacts/chroma_db"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)


vectorstore = None
qa_chain = None


async def load_db_and_chain():
    global vectorstore, qa_chain, search_tool
    try:
        if os.path.exists(PRESIST_DIR):
            vectorstore = load_vector_db_from_persist_dir(PRESIST_DIR)
            qa_chain = create_qa_chain(vectorstore)
            return True
        else:
            return False
    except Exception as e:
        print("[ERROR] Failed to load vector DB or create QA chain:", e)
        return False


# Try to load the vector database on startup
@app.on_event("startup")
async def startup_event():
    await load_db_and_chain()

# Background task to process uploaded documents
def process_uploaded_documents(new_files: List[str]):
    global vectorstore, qa_chain
    vectorstore = process_pdf_directory(DOCUMENTS_DIR, PRESIST_DIR)
    if vectorstore:
        qa_chain = create_qa_chain(vectorstore)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "University Chatbot API is running"}

@app.get("/status")
async def get_status():
    """Check if the vector database is loaded"""
    return {"db_loaded": vectorstore is not None}

@app.get("/documents")
async def list_documents():
    """List all documents in the documents directory"""
    try:
        files = os.listdir(DOCUMENTS_DIR)
        files = [f for f in files if not f.startswith(".") and f.endswith(".pdf")]
        return {"documents": [{"name": f} for f in files]}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a document and add it to the vector database"""
    if not file.filename.endswith('.pdf'):
        return JSONResponse(
            content={"error": "Only PDF files are supported"},
            status_code=400
        )
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(process_uploaded_documents, [file_path])
    
    return {"message": "Document uploaded and being processed"}

@app.post("/rebuild-db")
async def rebuild_database(background_tasks: BackgroundTasks):
    """Rebuild the vector database from all documents"""
    background_tasks.add_task(process_uploaded_documents, [])
    return {"message": "Database rebuild started"}

@app.post("/ask")
async def ask_question_endpoint(question: str = Form(...)):
    """Ask a question to the chatbot"""
    if not qa_chain:
        if not load_db_and_chain():
            return JSONResponse(
                content={"error": "No vector database available. Please upload documents first."},
                status_code=400
            )
    
    try:
        result = answer_question(qa_chain, question, vectorstore=vectorstore)
        return result
    except Exception as e:
        return JSONResponse(
            content={"error": f"Error answering question: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)