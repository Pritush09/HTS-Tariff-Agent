from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from config.settings import OPENROUTER_API_KEY, MODEL_NAME
from src.tools.rag_tool import RAGTool

class RAGAgent:
    def __init__(self):
        self.rag_tool = RAGTool()
        self.rag_tool.load()
        self.llm = ChatOpenAI(openai_api_key=OPENROUTER_API_KEY, openai_api_base="https://openrouter.ai/api/v1", model_name=MODEL_NAME)
        self.chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=self.rag_tool.vectorstore.as_retriever())

    def run(self, query):
        return self.chain.run(query)
