import os
import shutil
import time
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document 

def get_embeddings_model():
    return OllamaEmbeddings(model="mxbai-embed-large:latest")

def index_codebase(file_documents, current_sha):
    """
    Smart RAG: Checks if the DB matches the current Commit SHA.
    If match -> Load (Fast).
    If mismatch -> Rebuild (Slow).
    """
    db_path = "./chroma_db"
    version_file = os.path.join(db_path, "version.txt")
    
    if os.path.exists(db_path) and os.path.exists(version_file):
        try:
            with open(version_file, "r") as f:
                cached_sha = f.read().strip()
            
            if cached_sha == current_sha:
                print(f"RAG: Cache Hit! Loading existing DB for commit {current_sha[:7]}...")
                vectorstore = Chroma(
                    persist_directory=db_path,
                    embedding_function=get_embeddings_model(),
                    collection_name="repo_codebase"
                )
                return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            else:
                print(f"RAG: Code changed ({cached_sha[:7]} -> {current_sha[:7]}). Rebuilding DB...")
                shutil.rmtree(db_path)
                time.sleep(1) # Wait for file lock release
        except Exception as e:
            print(f"⚠️ Cache check failed ({e}). Rebuilding...")
            if os.path.exists(db_path):
                shutil.rmtree(db_path)

    # 2. BUILD NEW DB
    print(f"RAG: Creating NEW Vector DB from {len(file_documents)} files...")
    
    docs = [Document(page_content=d['content'], metadata={"source": d['source']}) for d in file_documents]
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    
    if os.path.exists(db_path):
        try:
            shutil.rmtree(db_path)
            time.sleep(1)
        except:
            pass

    print(f"Saving database to: {os.path.abspath(db_path)}")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=get_embeddings_model(),
        collection_name="repo_codebase",
        persist_directory=db_path
    )
    
    # SAVE THE VERSION
    try:
        with open(version_file, "w") as f:
            f.write(current_sha)
    except Exception as e:
        print(f"⚠️ Warning: Could not save version file: {e}")
    
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def query_rag(retriever, query):
    """
    Searches the codebase for the answer to a specific question.
    """
    relevant_docs = retriever.invoke(query)
    return "\n\n".join([f"File: {d.metadata['source']}\n{d.page_content}" for d in relevant_docs])