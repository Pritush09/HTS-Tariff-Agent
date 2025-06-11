import logging
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from config.settings import OPENROUTER_API_KEY, MODEL_NAME
from src.tools.rag_tool import RAGTool

# Configure logger
logger = logging.getLogger("RAGAgent")
logger.setLevel(logging.INFO)

# Prompt for HTS RAG responses
TARIFFBOT_PROMPT_TEMPLATE = """
You are TariffBot — an intelligent assistant trained on U.S. International Trade Commission data.
You exist to help importers, analysts, and trade professionals quickly understand tariff rules, duty rates, and policy agreements.

- You always provide clear, compliant, and factual answers grounded in official HTS documentation.
- When asked about trade agreements (e.g., NAFTA, Israel FTA), you reference the relevant General Notes with citations.
- If a query is ambiguous or unsupported, you politely defer or recommend reviewing the relevant HTS section manually.

Context:
{context}

Question:
{question}
"""

class RAGAgent:
    def __init__(self, model_name="deepseek/deepseek-r1-0528:free"):
        load_dotenv()
        self.rag_tool = RAGTool()
        self.rag_tool.load()

        self.llm = ChatOpenAI(
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name=model_name,
            temperature=0
        )

        # Prompt takes both context and user question
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=TARIFFBOT_PROMPT_TEMPLATE
        )

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        combine_docs_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_variable_name="context"
        )

        self.chain = RetrievalQA(
            retriever=self.rag_tool.vectorstore.as_retriever(),
            combine_documents_chain=combine_docs_chain,
            return_source_documents=True
        )

    def run(self, query: str) -> str:
        try:
            result = self.chain({"query": query})
            answer = result["result"]
            sources = result.get("source_documents", [])

            logger.info(f"RAG query: {query}")
            logger.debug(f"Answer: {answer}")
            logger.debug(f"Sources: {[doc.metadata for doc in sources]}")

            # Skip sources if not retrieved (common for vague follow-ups like "elaborate")
            if not sources:
                return (
                    f"{answer}\n\n🛈 Note: No specific sources found for this response. "
                    "If this was a follow-up question, it may rely on prior conversation or general policy patterns."
                )

            # Extract clean source names
            source_info = "\n".join(
                f"- {doc.metadata.get('source', ' ')}" for doc in sources
            )

            return f"{answer}\n\n📄 Sources:\n{source_info}"

        except Exception as e:
            logger.error(f"RAG failed for query '{query}': {e}")
            return "⚠️ An error occurred while processing your query."
