from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import json

from build_index import build_index
from rag_chain import RAGChain

from pipeline.embedding import EmbeddingManager
from pipeline.faissvectorstore import VectorStoreManager
from pipeline.retrieve import RetrieverManager
from pipeline.llm import LLMManager


app = FastAPI()

# enable CORS so that frontend can communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root directory for storing notebooks, uploaded documents, and vector databases.
NOTEBOOKS_DIR = "notebooks"

os.makedirs(
    NOTEBOOKS_DIR,
    exist_ok=True
)

# Load all RAG components for a notebook:
#embeddings -> FAISS -> retriever -> LLM
def load_rag(faiss_dir):

    embedding_model = (
        EmbeddingManager()
        .get_model()
    )

    vectorstore = (
        VectorStoreManager(
            embedding_model,
            persist_dir=faiss_dir
        ).load()
    )

    retriever = RetrieverManager(
        vectorstore
    )

    llm = (
        LLMManager()
        .get_llm()
    )

    return RAGChain(
        retriever,
        llm
    )

# Request model for notebook creation
class NotebookRequest(BaseModel):
    name: str

#request model for user queries
class QueryRequest(BaseModel):
    notebook: str
    query: str
    top_k: int



# Health check endpoint
@app.get("/")
def root():
    return {"message": "Notebook RAG API"}



#return all available notebooks
@app.get("/notebooks")
def get_notebooks():

    notebooks = []

    for item in os.listdir(NOTEBOOKS_DIR):
        path = os.path.join(NOTEBOOKS_DIR, item)

        if os.path.isdir(path):
            notebooks.append(item)

    return notebooks



# Create a new notebook workspace
@app.post("/create-notebook")
def create_notebook(
    request: NotebookRequest
):

    notebook = request.name

    os.makedirs(
        os.path.join(
            NOTEBOOKS_DIR,
            notebook,
            "docs"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            NOTEBOOKS_DIR,
            notebook,
            "faiss_store"
        ),
        exist_ok=True
    )

    return {
        "message": "Notebook is created"
    }



#upload PDF documents to a notebook
@app.post("/upload/{notebook}")
async def upload_file(
    notebook: str,
    file: UploadFile = File(...)
):

    docs_dir = os.path.join(
        NOTEBOOKS_DIR,
        notebook,
        "docs"
    )

    save_path = os.path.join(
        docs_dir,
        file.filename
    )

    with open(save_path, "wb") as f:
        f.write(await file.read())

    return {
        "message": "File is Uploaded"
    }


#build FAISS index from uploaded documents
@app.post("/build-index/{notebook}")
def build(notebook: str):

    docs_dir = os.path.join(
        NOTEBOOKS_DIR,
        notebook,
        "docs"
    )

    faiss_dir = os.path.join(
        NOTEBOOKS_DIR,
        notebook,
        "faiss_store"
    )

    build_index(
        docs_folder=docs_dir,
        persist_dir=faiss_dir
    )

    return {
        "message": "Index built"
    }



# Process user question using RAG pipeline
@app.post("/ask")
def ask(
    request: QueryRequest
):

    faiss_dir = os.path.join(
        NOTEBOOKS_DIR,
        request.notebook,
        "faiss_store"
    )

    rag = load_rag(faiss_dir)

    stats_file = os.path.join(
        NOTEBOOKS_DIR,
        request.notebook,
        "stats.json"
    )

    if os.path.exists(stats_file):

        with open(stats_file, "r") as f:
            stats = json.load(f)

        stats["queries"] = stats.get("queries", 0) + 1

        with open(stats_file, "w") as f:
            json.dump(stats, f)

    result = rag.invoke(
        query=request.query,
        top_k=request.top_k
    )

    docs = []

    for doc in result["documents"]:

        docs.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })

    #return generated answer, retrieved chunks, and source documents
    return {
        "answer": result["answer"],
        "documents": docs,
        "sources": result["sources"]
    }

@app.get("/papers/{notebook}")
def get_papers(notebook: str):

    docs_dir = os.path.join(
        NOTEBOOKS_DIR,
        notebook,
        "docs"
    )

    if not os.path.exists(docs_dir):
        return []

    papers = []

    for file in os.listdir(docs_dir):
        if file.lower().endswith(".pdf"):
            papers.append(file)

    return papers


@app.get("/stats/{notebook}")
def get_stats(notebook: str):

    stats_file = os.path.join(
        NOTEBOOKS_DIR,
        notebook,
        "stats.json"
    )

    if not os.path.exists(stats_file):

        return {
            "papers": 0,
            "chunks": 0,
            "tokens": 0,
            "queries": 0
        }

    with open(stats_file, "r") as f:
        stats = json.load(f)

    return stats

