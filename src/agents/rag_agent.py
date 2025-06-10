from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from config.settings import OPENROUTER_API_KEY, MODEL_NAME
from src.tools.rag_tool import RAGTool

# TariffBot persona as a system preamble
TARIFFBOT_PROMPT_TEMPLATE = """
You are TariffBot — an intelligent assistant trained on U.S. International Trade Commission data.
You exist to help importers, analysts, and trade professionals quickly understand tariff rules, duty rates, and policy agreements.

- You always provide clear, compliant, and factual answers grounded in official HTS documentation.
- When given an HTS code and product information, you explain all applicable duties and cost components.
- When asked about trade agreements (e.g., NAFTA, Israel FTA), you reference the relevant General Notes with citations.
- If a query is ambiguous or unsupported, you politely defer or recommend reviewing the relevant HTS section manually.
- You do not speculate or make policy interpretations — you clarify with precision and data.

Answer the following using the provided context:

{context}
"""

class RAGAgent:
    def __init__(self,model_name="deepseek/deepseek-r1-0528:free"):
        load_dotenv()
        self.rag_tool = RAGTool()
        self.rag_tool.load()

        self.llm = ChatOpenAI(
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name=model_name,
            temperature=0
        )

        # ✅ Use PromptTemplate instead of ChatPromptTemplate
        prompt = PromptTemplate(
            input_variables=["context"],
            template=TARIFFBOT_PROMPT_TEMPLATE
        )

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        combine_docs_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_variable_name="context"
        )

        self.chain = RetrievalQA(
            retriever=self.rag_tool.vectorstore.as_retriever(),
            combine_documents_chain=combine_docs_chain
        )

    def run(self, query: str) -> str:
        return self.chain.run(query)
