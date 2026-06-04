from langchain_huggingface import HuggingFaceEmbeddings

# Manages the embedding model used for converting text chunks into vector representations.
class EmbeddingManager:

    def __init__(self,model_name:str ="sentence-transformers/all-MiniLM-L6-v2"):

        self.model_name = model_name

        print(
            f"[INFO] Loading embedding model: {model_name}"
        )

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=model_name
        ) # Load Hugging face embedding model

	# it returns embedding model instance
    def get_model(self):
		
        return self.embedding_model