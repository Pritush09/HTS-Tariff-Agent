from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from src.tools.tariff_tool import TariffCalculatorTool

class TariffAgent:
    def __init__(self, api_key: str):
        self.tool = TariffCalculatorTool()
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",  # for OpenRouter
            model="deepseek-ai/deepseek-r1-0528:free"
        )

        self.tools = [
            Tool(
                name="DutyEstimator",
                func=self.query_tool,
                description=(
                    "Use this tool to estimate duty for a given HTS code and shipment info. "
                    "Inputs must be a string in this format: "
                    "'hts_code=0101.21.0000, cost=1000, freight=50, insurance=20, weight=200, quantity=10'"
                )
            )
        ]

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def query_tool(self, query: str) -> str:
        try:
            params = dict(
                part.split("=") for part in query.split(",") if "=" in part
            )
            result = self.tool.calculate_duty(
                hts_code=params["hts_code"].strip(),
                product_cost=float(params["cost"]),
                freight=float(params["freight"]),
                insurance=float(params["insurance"]),
                unit_weight=float(params["weight"]),
                quantity=int(params["quantity"])
            )
            return str(result)
        except Exception as e:
            return f"Error parsing or processing request: {str(e)}"

    def run(self, prompt: str) -> str:
        return self.agent.run(prompt)
