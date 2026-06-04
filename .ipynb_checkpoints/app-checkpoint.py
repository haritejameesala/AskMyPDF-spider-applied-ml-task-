from pipeline.embedding import EmbeddingManager
from pipeline.faissvectorstore import VectorStoreManager
from pipeline.retrieve import RetrieverManager
from pipeline.llm import LLMManager
from pipeline.rag_chain import RAGChain


embedding_model = EmbeddingManager().get_model()

vectorstore = VectorStoreManager(
    embedding_model,
    "faiss_store"
).load()

retriever = RetrieverManager(
    vectorstore
)

llm = LLMManager().get_llm()

rag = RAGChain(
    retriever,
    llm
)

print("RAG Chatbot Ready!")

while True:

    query = input("\nYou: ")

    if query.lower() == "exit":
        break

    result = rag.invoke(query)

    print("\nAssistant:")
    print(result["answer"])

	for doc in result["documents"]:
	    print(doc.metadata)