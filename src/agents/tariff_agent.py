# Tariff duty calculator agent
### 13. src/agents/tariff_agent.py
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.tools.tariff_tool import TariffTool
from src.utils.database import HTSDatabase

class TariffAgent(BaseAgent):
    """Agent for handling HTS duty calculations and tariff lookups."""
    
    def __init__(self, database: HTSDatabase):
        super().__init__("TariffAgent")
        self.tariff_tool = TariffTool(database)
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process tariff calculation and lookup queries."""
        try:
            # Determine query type and extract parameters
            query_type = self._determine_query_type(query, kwargs)
            
            if query_type == "calculate_duties":
                return self._handle_duty_calculation(kwargs)
            elif query_type == "lookup_hts":
                return self._handle_hts_lookup(kwargs)
            elif query_type == "search_description":
                return self._handle_description_search(kwargs)
            elif query_type == "sample":
                return self._handle_sample_calculation()
            else:
                return {
                    "success": False,
                    "error": "Unable to determine query type",
                    "suggestion": "Please provide HTS number or product description"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing tariff query: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _determine_query_type(self, query: str, kwargs: Dict[str, Any]) -> str:
        """Determine the type of query based on input."""
        if kwargs.get("hts_number") and kwargs.get("product_cost") is not None:
            return "calculate_duties"
        elif kwargs.get("hts_number"):
            return "lookup_hts"
        elif kwargs.get("description"):
            return "search_description"
        elif "sample" in query.lower() or "example" in query.lower():
            return "sample"
        else:
            return "unknown"
    
    def _handle_duty_calculation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle duty calculation requests."""
        required_params = ["hts_number", "product_cost", "freight", "insurance", "unit_weight", "quantity"]
        
        # Validate required parameters
        for param in required_params:
            if param not in params:
                return {
                    "success": False,
                    "error": f"Missing required parameter: {param}",
                    "required_params": required_params
                }
        
        return self.tariff_tool.calculate_duties(
            hts_number=params["hts_number"],
            product_cost=float(params["product_cost"]),
            freight=float(params["freight"]),
            insurance=float(params["insurance"]),
            unit_weight=float(params["unit_weight"]),
            quantity=int(params["quantity"])
        )
    
    def _handle_hts_lookup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTS information lookup."""
        hts_number = params.get("hts_number")
        if not hts_number:
            return {
                "success": False,
                "error": "HTS number is required for lookup"
            }
        
        return self.tariff_tool.lookup_hts_info(hts_number)
    
    def _handle_description_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product description search."""
        description = params.get("description")
        limit = params.get("limit", 10)
        
        if not description:
            return {
                "success": False,
                "error": "Product description is required for search"
            }
        
        return self.tariff_tool.search_by_description(description, limit)
    
    def _handle_sample_calculation(self) -> Dict[str, Any]:
        """Handle sample calculation request."""
        return self.tariff_tool.get_sample_calculation()
    
    def get_capabilities(self) -> List[str]:
        return [
            "Calculate import duties and landed costs",
            "Look up HTS tariff information",
            "Search products by description",
            "Parse and validate HTS numbers",
            "Handle percentage, specific, and compound duty rates"
        ]
    
    def get_sample_queries(self) -> List[str]:
        return [
            "Calculate duties for HTS 0101.30.00.00 with $10,000 cost",
            "Look up tariff rates for HTS 0201.10.05.00",
            "Search for cattle in HTS database",
            "What are the duty rates for beef imports?",
            "Show me a sample duty calculation"
        ]