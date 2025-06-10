import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Set up logging to file
logging.basicConfig(
    filename="logs/hts_agent.log",
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("HTSAgent")




from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from src.agents.rag_agent import RAGAgent
from src.tools.tariff_tool import TariffCalculatorTool
from src.agents.tariff_agent import TariffAgent
from config.settings import OPENROUTER_API_KEY, MODEL_NAME

class HTSAgent:
    def __init__(self, model_name="deepseek/deepseek-r1-0528:free"):
        self.llm = ChatOpenAI(
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name=model_name,
            temperature=0
        )
        # self.tariff_tool = TariffCalculatorTool()
        self.rag_agent = RAGAgent(model_name)
        self.tariff_agent = TariffAgent(model_name)

        self.tools = [
            Tool(
                name="DutyEstimator",
                func=self._handle_tariff_query,
                description="Estimates duty given hts_code, cost, freight, insurance, weight, quantity"
            ),
            Tool(
                name="TradePolicyQA",
                func=self._handle_policy_query,
                description="Answers trade policy questions using HTS General Notes"
            )
        ]

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.agent = initialize_agent(tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True  # ✅ Add this to prevent hard crashes
            # LangChain agents expect response when using agent in specific format when it doesnt met then it throws error
        )

    def _handle_tariff_query(self, query: str) -> str:
        try:
            parts = dict(p.strip().split("=") for p in query.split(","))
            return str(self.tariff_agent.calculate_duty(
                hts_code=parts["hts_code"],
                product_cost=float(parts["cost"]),
                freight=float(parts["freight"]),
                insurance=float(parts["insurance"]),
                unit_weight=float(parts["weight"]),
                quantity=int(parts["quantity"])
            ))
        except Exception as e:
            return f"Error parsing tariff query: {e}"

    def _handle_policy_query(self, question: str) -> str:
        return self.rag_agent.run(question)

    def run(self, user_input: str) -> str:
        try:
            # Handle empty history
            history = getattr(self.memory.chat_memory, "messages", [])
            formatted_history = ""

            if history:
                for msg in history:
                    if msg.type == "human":
                        formatted_history += f"User: {msg.content}\n"
                    elif msg.type == "ai":
                        formatted_history += f"TariffBot: {msg.content}\n"

            # Combine prior + new input
            full_prompt = f"{formatted_history}User: {user_input}"

            return self.agent.run(full_prompt)

        except Exception as e:
            logger.error(f"Agent fallback due to parsing failure: {e}")
            return f"⚠️ Sorry, I encountered an error. Here's the raw output:\n\n{str(e)}"
