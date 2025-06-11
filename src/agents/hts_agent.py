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



import re

from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from src.agents.rag_agent import RAGAgent
# from src.tools.tariff_tool import TariffCalculatorTool
from src.agents.tariff_agent import TariffAgent
from config.settings import OPENROUTER_API_KEY

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
        self.tariff_agent = TariffAgent()

        self.tools = [
            Tool(
                name="DutyEstimator",
                func=self._handle_tariff_query,
                description="""Calculate import duty. Input format: hts_code=..., cost=..., freight=..., insurance=..., weight=..., quantity=... 
                if the hts_code is not of format (10 digits with 3 dots) then convert it to the format by 
                padding it with 00 or 0 or placing the (.) at appropriate place
                to make the string look like XXXX.XX.XX.XX"""
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
        logger.info(f"DutyEstimator called with: {query}")
        try:
            parts = dict(p.strip().split("=", 1) for p in query.split(",") if "=" in p)
            
            # Normalize numeric fields using regex
            def clean_float(val):
                return float(re.findall(r"[\d.]+", val)[0])  # first number only

            def clean_int(val):
                return int(re.findall(r"\d+", val)[0])  # first integer only

            result = self.tariff_agent.calculate_duty(
                hts_code=parts["hts_code"].strip(),
                product_cost=clean_float(parts["cost"]),
                freight=clean_float(parts["freight"]),
                insurance=clean_float(parts["insurance"]),
                unit_weight=clean_float(parts["weight"]),
                quantity=clean_int(parts["quantity"])
            )
            if "error" in result:
                return f"❌ Could not find data for HTS code: {parts['hts_code']}. Please check the code and try again."
            logger.info(f"Tariff result: {result}")
            return str(result)

        except Exception as e:
            logger.error(f"Error in duty query: {e}")
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


if __name__ == "__main__":
    
    agent = HTSAgent()
    print(agent._handle_tariff_query(
    "hts_code=0101.21.0000, cost=1000, freight=50, insurance=20, weight=200, quantity=10"
))