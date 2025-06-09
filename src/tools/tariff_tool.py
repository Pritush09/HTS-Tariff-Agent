# Tariff tool logic
### 10. src/tools/tariff_tool.py
from typing import Dict, Any, Optional
import logging

from src.utils.database import HTSDatabase
from src.utils.duty_calculator import DutyCalculator
from src.utils.hts_parser import HTSParser

logger = logging.getLogger(__name__)

class TariffTool:
    def __init__(self, database: HTSDatabase):
        self.database = database
        self.calculator = DutyCalculator()
        self.parser = HTSParser()
    
    def calculate_duties(self, hts_number: str, product_cost: float, freight: float, 
                        insurance: float, unit_weight: float, quantity: int) -> Dict[str, Any]:
        """
        Calculate duties for a given HTS number and product information.
        
        Args:
            hts_number: HTS classification number
            product_cost: FOB cost of the product
            freight: Freight charges
            insurance: Insurance charges
            unit_weight: Weight per unit in kg
            quantity: Number of units
            
        Returns:
            Dictionary with complete duty calculation
        """
        try:
            # Validate inputs
            if product_cost < 0 or freight < 0 or insurance < 0:
                return self._error_response("Cost values cannot be negative")
            
            if unit_weight <= 0 or quantity <= 0:
                return self._error_response("Weight and quantity must be positive")
            
            # Validate and normalize HTS number
            is_valid, error_msg = self.parser.validate_hts_number(hts_number)
            if not is_valid:
                return self._error_response(f"Invalid HTS number: {error_msg}")
            
            normalized_hts = self.parser.normalize_hts_number(hts_number)
            
            # Look up HTS data
            hts_data = self.database.get_hts_by_number(normalized_hts)
            if not hts_data:
                return self._error_response(f"HTS number {hts_number} not found in database")
            
            # Calculate duties
            calculation = self.calculator.calculate_landed_cost(
                hts_data, product_cost, freight, insurance, unit_weight, quantity
            )
            
            # Format response
            response = {
                "success": True,
                "hts_number": self.parser.format_hts_number(hts_number),
                "calculation": calculation,
                "formatted_breakdown": self.calculator.format_cost_breakdown(calculation),
                "message": "Duty calculation completed successfully"
            }
            
            logger.info(f"Calculated duties for HTS {hts_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error calculating duties: {e}")
            return self._error_response(f"Calculation error: {str(e)}")
    
    def lookup_hts_info(self, hts_number: str) -> Dict[str, Any]:
        """Look up HTS information without calculation."""
        try:
            is_valid, error_msg = self.parser.validate_hts_number(hts_number)
            if not is_valid:
                return self._error_response(f"Invalid HTS number: {error_msg}")
            
            normalized_hts = self.parser.normalize_hts_number(hts_number)
            hts_data = self.database.get_hts_by_number(normalized_hts)
            
            if not hts_data:
                return self._error_response(f"HTS number {hts_number} not found")
            
            hierarchy = self.parser.get_hts_hierarchy(hts_number)
            
            return {
                "success": True,
                "hts_data": hts_data,
                "hierarchy": hierarchy,
                "formatted_number": self.parser.format_hts_number(hts_number)
            }
            
        except Exception as e:
            logger.error(f"Error looking up HTS info: {e}")
            return self._error_response(f"Lookup error: {str(e)}")
    
    def search_by_description(self, description: str, limit: int = 10) -> Dict[str, Any]:
        """Search HTS entries by product description."""
        try:
            if not description.strip():
                return self._error_response("Description cannot be empty")
            
            results = self.database.search_hts_by_description(description, limit)
            
            if not results:
                return {
                    "success": True,
                    "results": [],
                    "message": f"No HTS entries found matching '{description}'"
                }
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "hts_number": self.parser.format_hts_number(result['hts_number']),
                    "description": result['description'],
                    "general_rate": result.get('general_rate', 'N/A'),
                    "special_rate": result.get('special_rate', 'N/A')
                })
            
            return {
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "message": f"Found {len(formatted_results)} matching entries"
            }
            
        except Exception as e:
            logger.error(f"Error searching by description: {e}")
            return self._error_response(f"Search error: {str(e)}")
    
    def get_sample_calculation(self) -> Dict[str, Any]:
        """Get a sample calculation for demonstration."""
        return self.calculate_duties(
            hts_number="0101.30.00.00",
            product_cost=10000,
            freight=500,
            insurance=100,
            unit_weight=100,
            quantity=5
        )
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "success": False,
            "error": message,
            "calculation": None,
            "formatted_breakdown": f"Error: {message}"
        }