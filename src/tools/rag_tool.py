from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
from src.tools.embedding_cache import get_cached_embeddings
# from config.settings import HTS_DATA_DIR, VECTORSTORE_DIR
from src.tools.data_ingestion import extract_pdf_text

HTS_DATA_DIR = "data/downloads/"
VECTORSTORE_DIR = "data/vectorstore/"

class RAGTool:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                            chunk_overlap=200,
                                                            separators=["\n\n", "\n", ".", " "])
        self.embeddings = get_cached_embeddings()  # Cached here
        self.vectorstore = None

    def ingest(self):
        text = extract_pdf_text(os.path.join(HTS_DATA_DIR, "GN.pdf"))
        chunks = self.text_splitter.split_documents([Document(page_content=text)])
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local(VECTORSTORE_DIR)

    def load(self):
        # self.vectorstore = FAISS.load_local(VECTORSTORE_DIR, self.embeddings)
        self.vectorstore = FAISS.load_local(
            VECTORSTORE_DIR,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

    def search(self, query):
        return self.vectorstore.similarity_search(query)
    
if __name__ == "__main__":
    v = RAGTool()
    v.ingest()
    