# AskMyPDF

AskMyPDF is a Retrieval-Augmented Generation (RAG) application that allows users to upload research papers, build a vector database, and ask questions about the uploaded documents using an LLM.

## Features

- Create multiple notebooks
- Upload PDF research papers
- Build FAISS vector indexes
- Semantic search using HuggingFace embeddings
- Question answering with Groq Llama 3.3
- Source-aware responses
- Notebook statistics
  - Number of papers
  - Number of chunks
  - Number of tokens
  - Number of queries

## Tech Stack

### Backend
- FastAPI
- LangChain
- FAISS
- HuggingFace Embeddings
- Groq API

### Frontend
- HTML
- CSS
- JavaScript

## Project Structure

```text
Backend/
│
├── build_index.py
├── main.py
├── rag_chain.py
│
└── pipeline/
    ├── chunking.py
    ├── data_loader.py
    ├── embedding.py
    ├── faissvectorstore.py
    ├── llm.py
    └── retrieve.py

Frontend/
│
├── index.html
├── script.js
├── style.css
│
└── images/
    ├── Logo.png
    └── favicon.png

requirements.txt
```

## How It Works

1. Upload PDF research papers.
2. Documents are split into chunks.
3. Chunks are converted into embeddings.
4. Embeddings are stored in a FAISS vector database.
5. User asks a question.
6. Relevant chunks are retrieved using semantic search.
7. Retrieved context is sent to the LLM.
8. The generated answer is returned along with source documents.

## Setup

### Clone Repository

```bash
git clone https://github.com/haritejameesala/AskMyPDF-spider-applied-ml-task-.git
cd AskMyPDF-spider-applied-ml-task-
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file inside the Backend folder:

```env
GROQ_API_KEY=your_groq_api_key
```

### Run Backend

```bash
cd Backend
uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

### Run Frontend

```bash
cd Frontend
python -m http.server 5500
```

Frontend runs on:

```text
http://127.0.0.1:5500
```

## Screenshots

![Screenshot 1](screenshots/Screenshot-1.png)

![Screenshot 2](screenshots/Screenshot-2.png)

## Future Improvements

- Chat history
- PDF preview
- Figure and table retrieval
- Citation-aware answers
- Multi-user support
- Docker deployment

## Author

Hari Teja  Meesala
B.Tech CSE, NIT Trichy
