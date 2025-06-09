# RAG-based policy Q&A agent
### 12. src/agents/rag_agent.py
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.tools.rag_tool import RAGTool

class RAGAgent(BaseAgent):
    """Agent for handling trade policy and agreement questions using RAG."""
    
    def __init__(self, general_notes_path: str):
        super().__init__("RAGAgent")
        self.rag_tool = RAGTool()
        self.initialized = False
        self.general_notes_path = general_notes_path
        self._initialize()
    
    def _initialize(self):
        """Initialize the RAG system."""
        try:
            success = self.rag_tool.initialize_from_file(self.general_notes_path)
            if success:
                self.initialized = True
                self.logger.info("RAG Agent initialized successfully")
            else:
                self.logger.error("Failed to initialize RAG Agent")
        except Exception as e:
            self.logger.error(f"Error initializing RAG Agent: {e}")
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process trade policy and agreement questions."""
        if not self.initialized:
            return {
                "success": False,
                "error": "RAG system not properly initialized",
                "answer": "I'm sorry, but my knowledge base is not available right now."
            }
        
        try:
            result = self.rag_tool.query(query)
            return {
                "success": True,
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "query_type": "trade_policy",
                "agent": self.name
            }
        except Exception as e:
            self.logger.error(f"Error processing RAG query: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "I encountered an error while processing your question."
            }
    
    def get_capabilities(self) -> List[str]:
        return [
            "Answer questions about trade agreements (NAFTA, Israel FTA, etc.)",
            "Explain tariff policy and regulations",
            "Provide information from HTS General Notes",
            "Clarify trade compliance requirements"
        ]
    
    def get_sample_queries(self) -> List[str]:
        return [
            "What is the United States-Israel Free Trade Agreement?",
            "Explain the rules of origin requirements",
            "What are the benefits of NAFTA for importers?",
            "How does the Generalized System of Preferences work?",
            "What documentation is required for duty-free treatment?"
        ]