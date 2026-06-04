from langchain_text_splitters import RecursiveCharacterTextSplitter

# it splits the loaded documents into smaller overlapping chunks to improve retrieval quality in the RAG pipeline.

def chunking(documents,chunk_size: int = 1000, chunk_overlap: int = 200):
	
	splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size,
											  chunk_overlap = chunk_overlap,
											  length_function =len,
											  separators =["\n\n",'\n'," ",""]
											 ) # Initialize text splitter
	# Creates chunks from documents
	chunks = splitter.split_documents(documents)
	
	print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks")
	return chunks