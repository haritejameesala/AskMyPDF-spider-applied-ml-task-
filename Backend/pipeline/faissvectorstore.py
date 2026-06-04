import os
from langchain_community.vectorstores import FAISS

# IT handles creation, saving, loading of FAISS vector database.
class VectorStoreManager:

    def __init__(self, embedding_model, persist_dir="faiss_store"):
        
        self.embedding_model = embedding_model
        self.persist_dir = persist_dir

        os.makedirs(self.persist_dir, exist_ok=True)

        self.vectorstore = None
		
	# It creates FAISS index from document chunks
    def createfaiss(self, chunks):

        print("[INFO] Creating FAISS vector store...")

        self.vectorstore = FAISS.from_documents(
            chunks,
            self.embedding_model
        )

        print("[INFO] FAISS vector store created.")

	# Save the vector store to disk
    def save(self):

        if self.vectorstore is None:
            raise ValueError("Vector store has not been created.")

        self.vectorstore.save_local(self.persist_dir)

        print(f"[INFO] Saved FAISS store to {self.persist_dir}")

	# For Loading existing vector store
    def load(self):

        print(f"[INFO] Loading FAISS store from {self.persist_dir}")

        self.vectorstore = FAISS.load_local(
            self.persist_dir,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )

        print("[INFO] FAISS store loaded.")

        return self.vectorstore

	#return current vector store object
    def get_vectorstore(self):

        return self.vectorstore