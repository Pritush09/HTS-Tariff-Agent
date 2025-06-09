# Script to setup vector store or clean data
from src.tools.rag_tool import RAGTool

if __name__ == "__main__":
    tool = RAGTool()
    tool.ingest()
    print("Ingested and stored vector data")
