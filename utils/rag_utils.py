import os
import shutil
import time
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document 

def get_embeddings_model():
    return OllamaEmbeddings(model="mxbai-embed-large:latest")

def index_codebase(file_documents):
    """
    Takes list of {'source': path, 'content': text} and builds a searchable index.
    """
    print(f"RAG: Indexing {len(file_documents)} files into Vector DB...")
    
    docs = [Document(page_content=d['content'], metadata={"source": d['source']}) for d in file_documents]
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    
    if os.path.exists("./chroma_db"):
        try:
            shutil.rmtree("./chroma_db")
            print("Cleared old database cache.")
            time.sleep(1)
        except Exception as e:
            print(f"Warning: Could not clear old DB: {e}")

    print(f"Saving database to: {os.path.abspath('./chroma_db')}")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=get_embeddings_model(),
        collection_name="repo_codebase",
        persist_directory="./chroma_db"
    )
    
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def query_rag(retriever, query):
    """
    Searches the codebase for the answer to a specific question.
    """
    relevant_docs = retriever.invoke(query)
    return "\n\n".join([f"File: {d.metadata['source']}\n{d.page_content}" for d in relevant_docs])