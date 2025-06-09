from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
from config.settings import HTS_DATA_DIR, VECTORSTORE_DIR
from src.tools.data_ingestion import extract_pdf_text

class RAGTool:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None

    def ingest(self):
        text = extract_pdf_text(os.path.join(HTS_DATA_DIR, "General Notes.pdf"))
        chunks = self.text_splitter.split_documents([Document(page_content=text)])
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local(VECTORSTORE_DIR)

    def load(self):
        self.vectorstore = FAISS.load_local(VECTORSTORE_DIR, self.embeddings)

    def search(self, query):
        return self.vectorstore.similarity_search(query, k=3)