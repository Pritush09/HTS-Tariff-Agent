import pandas as pd
from typing import Dict
from src.utils.duty_calculator import calculate_duties_for_dataframe

class TariffCalculatorTool:
    def __init__(self, data_dir: str = "data/downloads/section1.csv"):
        self.data = pd.read_csv(data_dir)

    def calculate_duty(self, hts_code: str, product_cost: float, freight: float, insurance: float,
                       unit_weight: float, quantity: int) -> Dict:
        """
        Look up the HTS code and calculate all applicable duties.
        """
        df = self.data
        match = df[df["HTS Number"].astype(str).str.startswith(hts_code)]

        if match.empty:
            return {"error": f"No entry found for HTS code {hts_code}"}

        filtered = calculate_duties_for_dataframe(
            match,
            product_cost=product_cost,
            freight=freight,
            insurance=insurance,
            unit_weight=unit_weight,
            quantity=quantity
        )

        record = filtered.iloc[0].to_dict()
        return {
            "HTS Number": record["HTS Number"],
            "Description": record["Description"],
            "CIF Value": record["CIF Value"],
            "General Rate Duty": record.get("General Rate of Duty Duty Amount", 0),
            "Special Rate Duty": record.get("Special Rate of Duty Duty Amount", 0),
            "Column 2 Duty": record.get("Column 2 Rate of Duty Duty Amount", 0),
            "Total Estimated Duty": sum([
                record.get("General Rate of Duty Duty Amount", 0),
                record.get("Special Rate of Duty Duty Amount", 0),
                record.get("Column 2 Rate of Duty Duty Amount", 0),
            ])
        }
