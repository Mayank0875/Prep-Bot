"""
Utility functions for question answering with a vector database
"""

from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from components.query_refine import refine_user_query
from prompt.db_summary import template

import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def load_vector_db_from_persist_dir(persist_directory: str):
    """Load a vector database from a persist directory"""
    if not os.path.exists(persist_directory):
        raise FileNotFoundError(f"Vector database directory not found: {persist_directory}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    return vectorstore

def create_qa_chain(vectorstore, model_name: str = "gemini-2.0-flash-001", temperature: float = 0):
    """Create a question-answering chain using the specified LLM and vector database"""
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature
    )

    prompt = PromptTemplate(
        input_variables=["context", "query"],
        template=template
    )
    
    qa_chain = prompt | llm
    return qa_chain

def answer_question(qa_chain, question: str, vectorstore) -> Dict[str, Any]:
    question = refine_user_query(question)
    if not question:
        return {"answer": "Unable to refine the question", "sources": []}
    retriver = vectorstore.as_retriever(search_type = "mmr", search_kwargs={"k": 3})
    docs = retriver.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    result = qa_chain.invoke({"query": question, "context": context})
    answer = result.content
    return {
        "answer": answer
    }





if __name__ == "main":
    ques = "Gernate 2 small coding Question on Maths"
    presist_path = '/Users/mayankgupta/Desktop/Project/ExamBot/backend/artifacts/chroma_db'
    vectorstore = load_vector_db_from_persist_dir(presist_path)

    chain = create_qa_chain(vectorstore=vectorstore, temperature=0)
    response = answer_question(chain, ques, vectorstore=vectorstore)

    print(response["answer"])
