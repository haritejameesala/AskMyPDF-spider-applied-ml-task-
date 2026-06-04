from pipeline.data_loader import load_all_docs
from pipeline.chunking import chunking
from pipeline.embedding import EmbeddingManager
from pipeline.faissvectorstore import VectorStoreManager

import json
import os

# complete indexing pipeline:
# load PDFs -> chunk documents -> generate embeddings -> build FAISS index
def build_index(
    docs_folder,
    persist_dir="faiss_store",
    chunk_size=1000,
    chunk_overlap=200
):

    print(f"[INFO] Loading documents from {docs_folder}")

    # load all PDF documents
    docs = load_all_docs(docs_folder)

    # split documents into smaller chunks
    chunks = chunking(
        docs,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    total_tokens = sum(
        len(chunk.page_content.split())
        for chunk in chunks
    )

    stats = {
        "papers": len(
            set(
                doc.metadata["source_file"]
                for doc in docs
            )
        ),
        "chunks": len(chunks),
        "tokens": total_tokens,
        "queries": 0
    }

    # Load embedding model
    embedding_model = EmbeddingManager().get_model()

    # create vector store manager
    faissVS = VectorStoreManager(
        embedding_model,
        persist_dir
    )

    # build and save FAISS index
    faissVS.createfaiss(chunks)
    faissVS.save()

    stats_path = os.path.join(
        os.path.dirname(persist_dir.rstrip("/\\")),
        "stats.json"
    )

    with open(stats_path, "w") as f:
        json.dump(stats, f)

    print(f"[INFO] Stats saved to {stats_path}")
    print("[INFO] Index created successfully.")