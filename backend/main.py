
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv
import shutil
import uuid

load_dotenv()


google_api_key = os.getenv("GOOGLE_API_KEY")

# 1. document loading
def load_document(file_path):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents
    else:
        raise ValueError("Unsupported file type")


# 2. text splitting
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

# 3. create embedding and store in vector database
def create_vector_db(chunks, db_directory="vectorstore"):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=google_api_key,
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_directory
    )
    vectorstore.persist()
    return vectorstore

# 4. create reterival  question answer chain
def create_qa_chain(vectorstore):
    llm = ChatGoogleGenerativeAI(
        model = "gemini-2.0-flash-001",
        google_api_key=google_api_key,
        tempature=0
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    return qa_chain

# 5. answer ques
def answer_question(qa_chain, question):
    result = qa_chain({"query": question})
    return {
        "answer": result["result"],
        "sources": [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]]
    }

# example usage in a processing script
def process_new_document(file_path, db_directory="vectorstore"):
    documents = load_document(file_path)
    chunks = split_documents(documents)
    
    # check if vectorstore already exists
    if os.path.exists(db_directory):
        # loading existing vectorstore
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_api_key,
        )
        vectorstore = Chroma(persist_directory=db_directory, embedding_function=embeddings)
        # adding new docs
        vectorstore.add_documents(chunks)
    else:
        # creating new vectorstore
        vectorstore = create_vector_db(chunks, db_directory)
    
    return vectorstore



app = FastAPI()

# frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load vectorstore and qa chain
VECTOR_DB_DIR = "vectorstore"
if os.path.exists(VECTOR_DB_DIR):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=google_api_key,
    )
    vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    qa_chain = create_qa_chain(vectorstore)
else:
    # Create empty vectorstore or handle appropriately
    vectorstore = None
    qa_chain = None


# folder to store documents
DOCUMENTS_DIR = "documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

@app.get("/documents")
async def list_documents():
    try:
        files = os.listdir(DOCUMENTS_DIR)
        files = [f for f in files if not f.startswith(".")]  
        return {"documents": [{"name": f} for f in files]}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # temp_file_path = f"temp_{uuid.uuid4()}.pdf"
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    global vectorstore, qa_chain
    vectorstore = process_new_document(file_path, VECTOR_DB_DIR)
    qa_chain = create_qa_chain(vectorstore)
        
    return {"message": "Document uploaded and processed successfully"}

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    if not qa_chain:
        return {"error": "No documents have been uploaded yet"}
    
    result = answer_question(qa_chain, question)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)