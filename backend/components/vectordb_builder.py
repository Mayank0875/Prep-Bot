from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import pickle
import glob
import hashlib
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def load_document(file_path: str):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def get_file_hash(file_path: str) -> str:
    """Get SHA-256 hash of file to detect changes."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def save_processed_files_info(processed_files: Dict[str, str], file_path: str):
    """Save information about processed files and their hashes."""
    with open(file_path, 'wb') as f:
        pickle.dump(processed_files, f)

def load_processed_files_info(file_path: str) -> Dict[str, str]:
    """Load information about previously processed files."""
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return {}

def process_pdf_directory(pdf_dir: str, persist_dir: str, processed_files_cache: str = 'processed_files.pkl'):

    os.makedirs(persist_dir, exist_ok=True)
    os.makedirs(os.path.dirname(processed_files_cache) if os.path.dirname(processed_files_cache) else '.', exist_ok=True)

    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    processed_files = load_processed_files_info(processed_files_cache)
    new_or_modified_files = []
    for pdf_file in pdf_files:
        file_hash = get_file_hash(pdf_file)
        if pdf_file not in processed_files or processed_files[pdf_file] != file_hash:
            new_or_modified_files.append(pdf_file)
    
    if not new_or_modified_files:
        print("No new or modified files to process")
        return
    
    print(f"Found {len(new_or_modified_files)} new or modified PDF files to process")
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )

    if os.path.exists(persist_dir):
        print("Loading existing vector store...")
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
    else:
        print("Creating new vector store...")
        vectorstore = None
    
    for pdf_file in new_or_modified_files:
        print(f"Processing {pdf_file}...")
        try:
            documents = load_document(pdf_file)
            chunks = split_documents(documents)
            
            if not vectorstore:
                vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    persist_directory=persist_dir
                )
            else:
                vectorstore.add_documents(chunks)
            
            processed_files[pdf_file] = get_file_hash(pdf_file)
            print(f"  Added {len(chunks)} chunks from {pdf_file}")
            
        except Exception as e:
            print(f"  Error processing {pdf_file}: {str(e)}")
    
    if vectorstore:
        print("Vector store saved successfully")
    
    save_processed_files_info(processed_files, processed_files_cache)
    print(f"Processed files information saved to {processed_files_cache}")
    
    return vectorstore

if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    pdf_dir = './data'
    abs_pdf_dir = os.path.abspath(pdf_dir)
    persist_dir = 'artifacts/chroma_db'
    process_pdf_directory(abs_pdf_dir, persist_dir)