class RAGChain:

    def __init__(self, retriever, llm):

        self.retriever = retriever
        self.llm = llm

    def format_context(self, docs):

        return "\n\n".join(
            doc.page_content
            for doc in docs
        )

    def invoke(self, query, top_k=4):

        docs = self.retriever.retrieve(
            query,
            top_k=top_k
        )

        context = self.format_context(docs)

        prompt = f"""
				You are a helpful research assistant.
				
				Answer the question using only the provided context.
				
				Context:
				{context}
				
				Question:
				{query}
				
				Answer:
				"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "documents": docs
        }