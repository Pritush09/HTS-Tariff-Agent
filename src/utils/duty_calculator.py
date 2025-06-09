# CIF and duty calculation logic
import pandas as pd
import re
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DutyCalculator:
    def __init__(self):
        self.duty_types = {
            'general': 'General Rate of Duty',
            'special': 'Special Rate of Duty', 
            'column2': 'Column 2 Rate of Duty'
        }
    
    def parse_duty_advanced(self, duty_str: str, unit_weight: Optional[float] = None, 
                          quantity: Optional[int] = None, cif_value: float = 0) -> Tuple[float, str]:
        """
        Parse duty string and return (duty_amount, duty_type).
        Returns duty amount in dollars and the type of duty applied.
        """
        if pd.isna(duty_str) or not duty_str or duty_str.strip() == "":
            return 0.0, "No duty"
        
        duty_str = duty_str.strip().lower()
        
        if "free" in duty_str:
            return 0.0, "Free"
        
        # Percentage duty (e.g., '5%', '2.5%')
        match = re.search(r"([\d.]+)\s*%", duty_str)
        if match:
            percentage = float(match.group(1)) / 100
            duty_amount = percentage * cif_value
            return duty_amount, f"{match.group(1)}% ad valorem"
        
        # Weight-based duty (e.g., '2.5¢/kg', '10¢/kg')
        match = re.search(r"([\d.]+)\s*¢/kg", duty_str)
        if match and unit_weight is not None:
            cents_per_kg = float(match.group(1))
            duty_amount = (cents_per_kg * unit_weight) / 100  # Convert cents to dollars
            return duty_amount, f"{match.group(1)}¢/kg specific duty"
        
        # Unit-based duty (e.g., '$1.00/unit', '$2.50/each')
        match = re.search(r"\$([\d.]+)/(unit|each)", duty_str)
        if match and quantity is not None:
            dollars_per_unit = float(match.group(1))
            duty_amount = dollars_per_unit * quantity
            return duty_amount, f"${match.group(1)}/unit specific duty"
        
        # Complex duties (e.g., "5% or 10¢/kg, whichever is greater")
        if "or" in duty_str and ("whichever is greater" in duty_str or "whichever is higher" in duty_str):
            duties = duty_str.split(" or ")
            duty1, type1 = self.parse_duty_advanced(duties[0], unit_weight, quantity, cif_value)
            duty2, type2 = self.parse_duty_advanced(duties[1].split(",")[0], unit_weight, quantity, cif_value)
            
            if duty1 >= duty2:
                return duty1, f"{type1} (higher of two options)"
            else:
                return duty2, f"{type2} (higher of two options)"
        
        logger.warning(f"Could not parse duty string: {duty_str}")
        return 0.0, f"Unparsed: {duty_str}"
    
    def calculate_landed_cost(self, hts_data: Dict[str, Any], product_cost: float, 
                            freight: float, insurance: float, unit_weight: float, 
                            quantity: int) -> Dict[str, Any]:
        """
        Calculate complete landed cost breakdown for a product.
        
        Args:
            hts_data: HTS tariff information from database
            product_cost: FOB cost of the product
            freight: Freight charges
            insurance: Insurance charges
            unit_weight: Weight per unit in kg
            quantity: Number of units
            
        Returns:
            Dictionary with complete cost breakdown
        """
        # Calculate CIF value
        cif_value = product_cost + freight + insurance
        total_weight = unit_weight * quantity
        
        # Initialize result dictionary
        result = {
            'hts_number': hts_data.get('hts_number', 'Unknown'),
            'description': hts_data.get('description', 'Unknown'),
            'product_cost': product_cost,
            'freight': freight,
            'insurance': insurance,
            'cif_value': cif_value,
            'quantity': quantity,
            'unit_weight': unit_weight,
            'total_weight': total_weight,
            'duties': {},
            'total_duty': 0.0,
            'landed_cost': 0.0
        }
        
        # Calculate each type of duty
        for duty_key, duty_name in self.duty_types.items():
            duty_rate = hts_data.get(duty_name.lower().replace(' ', '_'), '')
            if duty_rate:
                duty_amount, duty_description = self.parse_duty_advanced(
                    duty_rate, total_weight, quantity, cif_value
                )
                result['duties'][duty_key] = {
                    'rate': duty_rate,
                    'amount': duty_amount,
                    'description': duty_description
                }
        
        # Determine applicable duty (usually the general rate unless special conditions apply)
        applicable_duty = 0.0
        applicable_duty_type = 'none'
        
        if 'general' in result['duties'] and result['duties']['general']['amount'] > 0:
            applicable_duty = result['duties']['general']['amount']
            applicable_duty_type = 'general'
        
        # Check if special rate is lower and applicable
        if 'special' in result['duties'] and result['duties']['special']['amount'] > 0:
            if applicable_duty == 0 or result['duties']['special']['amount'] < applicable_duty:
                applicable_duty = result['duties']['special']['amount']
                applicable_duty_type = 'special'
        
        result['total_duty'] = applicable_duty
        result['applicable_duty_type'] = applicable_duty_type
        result['landed_cost'] = cif_value + applicable_duty
        
        return result
    
    def format_cost_breakdown(self, calculation: Dict[str, Any]) -> str:
        """Format the cost calculation results into a readable string."""
        lines = [
            f"=== HTS DUTY CALCULATION ===",
            f"HTS Number: {calculation['hts_number']}",
            f"Description: {calculation['description']}",
            "",
            f"=== COST BREAKDOWN ===",
            f"Product Cost (FOB): ${calculation['product_cost']:,.2f}",
            f"Freight: ${calculation['freight']:,.2f}",
            f"Insurance: ${calculation['insurance']:,.2f}",
            f"CIF Value: ${calculation['cif_value']:,.2f}",
            "",
            f"Quantity: {calculation['quantity']} units",
            f"Unit Weight: {calculation['unit_weight']} kg",
            f"Total Weight: {calculation['total_weight']} kg",
            "",
            f"=== DUTY RATES ===",
        ]
        
        for duty_type, duty_info in calculation['duties'].items():
            lines.append(f"{duty_type.title()} Rate: {duty_info['rate']}")
            lines.append(f"  Amount: ${duty_info['amount']:,.2f} ({duty_info['description']})")
        
        lines.extend([
            "",
            f"=== FINAL CALCULATION ===",
            f"Applicable Duty ({calculation['applicable_duty_type']}): ${calculation['total_duty']:,.2f}",
            f"Total Landed Cost: ${calculation['landed_cost']:,.2f}",
            f"Effective Duty Rate: {(calculation['total_duty'] / calculation['cif_value'] * 100):.2f}%"
        ])
        
        return "\n".join(lines)