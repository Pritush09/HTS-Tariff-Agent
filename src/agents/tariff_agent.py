# from langchain.agents import Tool, initialize_agent
# from langchain.chat_models import ChatOpenAI
# from langchain.agents.agent_types import AgentType
# from src.tools.tariff_tool import TariffCalculatorTool

# class TariffAgent:
#     def __init__(self, api_key: str):
#         self.tool = TariffCalculatorTool()
#         self.llm = ChatOpenAI(
#             temperature=0,
#             openai_api_key=api_key,
#             openai_api_base="https://openrouter.ai/api/v1",  # for OpenRouter
#             model="deepseek-ai/deepseek-r1-0528:free"
#         )

#         self.tools = [
#             Tool(
#                 name="DutyEstimator",
#                 func=self.query_tool,
#                 description=(
#                     "Use this tool to estimate duty for a given HTS code and shipment info. "
#                     "Inputs must be a string in this format: "
#                     "'hts_code=0101.21.0000, cost=1000, freight=50, insurance=20, weight=200, quantity=10'"
#                 )
#             )
#         ]

#         self.agent = initialize_agent(
#             tools=self.tools,
#             llm=self.llm,
#             agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#             verbose=True
#         )

#     def query_tool(self, query: str) -> str:
#         try:
#             params = dict(
#                 part.split("=") for part in query.split(",") if "=" in part
#             )
#             result = self.tool.calculate_duty(
#                 hts_code=params["hts_code"].strip(),
#                 product_cost=float(params["cost"]),
#                 freight=float(params["freight"]),
#                 insurance=float(params["insurance"]),
#                 unit_weight=float(params["weight"]),
#                 quantity=int(params["quantity"])
#             )
#             return str(result)
#         except Exception as e:
#             return f"Error parsing or processing request: {str(e)}"

#     def run(self, prompt: str) -> str:
#         return self.agent.run(prompt)


from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from src.tools.tariff_tool import TariffCalculatorTool

TARIFFBOT_SYSTEM_PROMPT = """
You are TariffBot — an intelligent assistant trained on U.S. International Trade Commission data.
You exist to help importers, analysts, and trade professionals quickly understand tariff rules, duty rates, and policy agreements.
- You always provide clear, compliant, and factual answers grounded in official HTS documentation.
- When given an HTS code and product information, you explain all applicable duties and cost components.
- When asked about trade agreements (e.g., NAFTA, Israel FTA), you reference the relevant General Notes with citations.
- If a query is ambiguous or unsupported, you politely defer or recommend reviewing the relevant HTS section manually.
- You do not speculate or make policy interpretations — you clarify with precision and data.
"""
from config.settings import OPENROUTER_API_KEY

class TariffAgent:
    def __init__(self, model_name="deepseek/deepseek-r1-0528:free"):
        self.tool = TariffCalculatorTool()

        self.llm = ChatOpenAI(
            temperature=0,
            model=model_name,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
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
            full_prompt = f"""{TARIFFBOT_SYSTEM_PROMPT.strip()}

{query.strip()}
"""
            params = dict(part.split("=") for part in query.split(",") if "=" in part)
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
        full_prompt = f"{TARIFFBOT_SYSTEM_PROMPT.strip()}\n\n{prompt.strip()}"
        return self.agent.run(full_prompt)
