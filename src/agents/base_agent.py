# Base agent class
### 11. src/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all HTS agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process a user query and return response."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return []
    
    def get_sample_queries(self) -> List[str]:
        """Return list of sample queries this agent can handle."""
        return []
    
    def format_response(self, response: Dict[str, Any]) -> str:
        """Format response for display."""
        if response.get("success", False):
            return response.get("message", "Operation completed successfully")
        else:
            return f"Error: {response.get('error', 'Unknown error occurred')}"