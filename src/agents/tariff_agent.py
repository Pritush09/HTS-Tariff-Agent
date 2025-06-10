

from src.tools.tariff_tool import TariffCalculatorTool


# TariffAgent class becomes a simple calculator wrapper
class TariffAgent:
    def __init__(self):
        self.tool = TariffCalculatorTool()

    def calculate_duty(self, hts_code, product_cost, freight, insurance, unit_weight, quantity):
        return self.tool.calculate_duty(
            hts_code=hts_code,
            product_cost=product_cost,
            freight=freight,
            insurance=insurance,
            unit_weight=unit_weight,
            quantity=quantity
        )
