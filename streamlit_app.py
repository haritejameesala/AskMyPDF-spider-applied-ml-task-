import os
import streamlit as st
import traceback

from build_index import build_index

from pipeline.embedding import EmbeddingManager
from pipeline.faissvectorstore import VectorStoreManager
from pipeline.retrieve import RetrieverManager
from pipeline.llm import LLMManager
from pipeline.rag_chain import RAGChain


NOTEBOOKS_DIR = "notebooks"

os.makedirs(
    NOTEBOOKS_DIR,
    exist_ok=True
)


@st.cache_resource
def load_rag(faiss_dir):

    embedding_model = (
        EmbeddingManager()
        .get_model()
    )

    vectorstore = VectorStoreManager(
        embedding_model,
        persist_dir=faiss_dir
    ).load()

    retriever = RetrieverManager(
        vectorstore
    )

    llm = LLMManager().get_llm()

    return RAGChain(
        retriever,
        llm
    )


st.set_page_config(
    page_title="Notebook RAG",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Notebook RAG")


with st.sidebar:

    st.header("Notebooks")

    notebook_name = st.text_input(
        "Create Notebook"
    )

    if st.button("Create"):

        if notebook_name:

            os.makedirs(
                os.path.join(
                    NOTEBOOKS_DIR,
                    notebook_name,
                    "docs"
                ),
                exist_ok=True
            )

            os.makedirs(
                os.path.join(
                    NOTEBOOKS_DIR,
                    notebook_name,
                    "faiss_store"
                ),
                exist_ok=True
            )

            st.rerun()

    notebooks = sorted(
        [
            n
            for n in os.listdir(
                NOTEBOOKS_DIR
            )
            if os.path.isdir(
                os.path.join(
                    NOTEBOOKS_DIR,
                    n
                )
            )
        ]
    )

    selected_notebook = st.selectbox(
        "Select Notebook",
        notebooks
        if notebooks
        else ["No Notebook"]
    )


if notebooks:

    docs_dir = os.path.join(
        NOTEBOOKS_DIR,
        selected_notebook,
        "docs"
    )

    faiss_dir = os.path.join(
        NOTEBOOKS_DIR,
        selected_notebook,
        "faiss_store"
    )

    st.header(
        f"Notebook: {selected_notebook}"
    )

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Build Index"):

        for file in uploaded_files:

            with open(
                os.path.join(
                    docs_dir,
                    file.name
                ),
                "wb"
            ) as f:

                f.write(
                    file.getbuffer()
                )

        build_index(
            docs_folder=docs_dir,
            persist_dir=faiss_dir
        )

        load_rag.clear()

        st.success(
            "Notebook indexed successfully."
        )

    try:

        rag = load_rag(
            faiss_dir
        )

        query = st.text_input(
            "Ask a question"
        )

        top_k = st.slider(
            "Top K",
            1,
            10,
            4
        )

        if st.button("Ask") and query:

            result = rag.invoke(
                query=query,
                top_k=top_k
            )

            st.subheader(
                "Answer"
            )

            st.write(
                result["answer"]
            )

            st.subheader(
                "Sources"
            )

            for doc in result[
                "documents"
            ]:

                source = (
                    doc.metadata.get(
                        "source_file",
                        "Unknown"
                    )
                )

                st.write(
                    f"📄 {source}"
                )

            st.subheader(
                "Retrieved Chunks"
            )

            for i, doc in enumerate(
                result["documents"],
                start=1
            ):

                with st.expander(
                    f"Chunk {i}"
                ):

                    st.write(
                        doc.page_content
                    )

                    st.json(
                        doc.metadata
                    )

    except Exception as e:
        st.error(f"Error: {e}")
        st.code(traceback.format_exc())