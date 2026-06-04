#Main RAG pipeline
# Retrieves relevant chunks and generates answers using the LLM
class RAGChain:

    def __init__(self, retriever, llm):

        self.retriever = retriever
        self.llm = llm

	#convert retrieved documents into a structured context containing source information and content.
    def format_context(self, docs):
		
	    context_parts = []
	
	    for doc in docs:
	
	        source = doc.metadata.get(
	            "source_file",
	            "Unknown Source"
	        )
	
	        page = doc.metadata.get(
	            "page",
	            "Unknown Page"
	        )
	
	        context_parts.append(
	            f"""
				Source: {source}
				Page: {page}
				
				Content:
				{doc.page_content}
				"""
	        )
	
	    return "\n\n".join(context_parts)

	# execute the RAG workflow:
    # retrieve → build context → generate answer
    def invoke(self, query, top_k=6):

		# Retrieve relevant document chunks
        docs = self.retriever.retrieve(
            query,
            top_k=top_k
        )

		# Create context from retrieved documents
        context = self.format_context(docs)

        prompt = f"""
				You are a helpful AI research assistant.
				
				Answer using only the provided context.
				
				Focus on the main concepts and key ideas.
				Avoid unnecessary details such as training steps, batch sizes, and implementation specifics unless the question asks for them.
				
				Explain clearly and naturally.
				
				Context:
				{context}
				
				Question:
				{query}
				
				Answer:
				"""

		#Generate response from LLM
        response = self.llm.invoke(prompt)

		#Collect unique source documents
        sources = list(
			set(
				doc.metadata.get(
					"source_file",
					"Unknown"
				)
				for doc in docs
			)
		)

        return {
		    "answer": response.content,
		    "documents": docs,
		    "sources": sources
		}