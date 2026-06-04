# Handles retrieval of relevant chunks from the vector database
class RetrieverManager:

    def __init__(self, vectorstore):

        self.vectorstore = vectorstore

	#retrieve top relevant documents using
    def retrieve(self, query, top_k=6):

		# Maximum Marginal Relevance (MMR) search
        return self.vectorstore.max_marginal_relevance_search(
		    query,
		    k=top_k,
		    fetch_k=20
		)
    
	