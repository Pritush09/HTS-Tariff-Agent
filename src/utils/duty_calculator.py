import re
import pandas as pd

def compute_cif(product_cost: float, freight: float, insurance: float) -> float:
    return product_cost + freight + insurance

def parse_duty_advanced(duty_str, cif_value, unit_weight=None, quantity=None):
    """
    Parses a duty string and returns the duty rate as a decimal fraction or calculated duty
    based on CIF, quantity, or weight.
    """
    if pd.isna(duty_str) or duty_str.strip() == "":
        return 0.0

    duty_str = duty_str.strip().lower()

    if "free" in duty_str:
        return 0.0

    # Percentage (e.g., "5%")
    match = re.search(r"([\d.]+)\\s*%", duty_str)
    if match:
        return float(match.group(1)) / 100

    # Per weight (e.g., "2.5¢/kg")
    match = re.search(r"([\\d.]+)\\s*¢/kg", duty_str)
    if match and unit_weight is not None:
        cents_per_kg = float(match.group(1))
        return (cents_per_kg * unit_weight) / (100 * cif_value)

    # Per unit (e.g., "$1.00/unit")
    match = re.search(r"\\$([\\d.]+)/unit", duty_str)
    if match and quantity is not None:
        dollars_per_unit = float(match.group(1))
        return (dollars_per_unit * quantity) / cif_value

    return 0.0

def calculate_duties_for_dataframe(df, product_cost, freight, insurance, unit_weight, quantity):
    """
    Applies the duty parser to a DataFrame and computes the total duties.
    """
    cif_value = compute_cif(product_cost, freight, insurance)

    duty_df = df[["HTS Number", "Description", "General Rate of Duty",
                  "Special Rate of Duty", "Column 2 Rate of Duty"]].copy()
    duty_df["CIF Value"] = cif_value
    duty_df["Product Cost"] = product_cost
    duty_df["Freight"] = freight
    duty_df["Insurance"] = insurance

    for col in ["General Rate of Duty", "Special Rate of Duty", "Column 2 Rate of Duty"]:
        parsed_col = f"{col} Parsed (%)"
        amount_col = f"{col} Duty Amount"
        duty_df[parsed_col] = duty_df[col].apply(lambda x: parse_duty_advanced(x, cif_value, unit_weight, quantity))
        duty_df[amount_col] = duty_df[parsed_col] * cif_value

    duty_df_filtered = duty_df[
        (duty_df["General Rate of Duty Duty Amount"] > 0) |
        (duty_df["Special Rate of Duty Duty Amount"] > 0) |
        (duty_df["Column 2 Rate of Duty Duty Amount"] > 0)
    ]

    return duty_df_filtered
