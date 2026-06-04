from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

#it loads all PDF files from that directory
def load_all_docs(data_directory : str):

	data_path = Path(data_directory).resolve()

	print(f"[DEBUG] Data path: {data_path}")

	documents =[]

	#pdf files

	pdf_files = list(data_path.glob("**/*.pdf"))  # it searchs recursively for PDF files

	print(f"\n[DEBUG] Found {len(pdf_files)} PDF files")

	for pdf_file in pdf_files:

		print(f"\nProcessing PDF: {pdf_file.name}")

		try:

			pdf_loader = PyPDFLoader(str(pdf_file)) #load PDF pages

			pdf_docs = pdf_loader.load() 

			for page in pdf_docs: #add metadata for source tracking
				page.metadata["source_file"] = pdf_file.name
				page.metadata["file_type"] = "pdf"

			documents.extend(pdf_docs)

			print(f"Loaded {len(pdf_docs)} PDF pages")

		except Exception as error:

			print(f"Error loading PDF {pdf_file.name}: {error}")

	print(f"\nTotal documents loaded: {len(documents)}")

	return documents