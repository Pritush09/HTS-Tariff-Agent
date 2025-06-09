# RAG tool logic
import os
from typing import List, Dict, Any
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from pathlib import Path
import logging

from config.settings import VECTOR_STORE_PATH, OPENAI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class RAGTool:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.vectorstore = None
        self.retrieval_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
    def load_documents(self, file_path: str) -> List[Dict[str, Any]]:
        """Load and chunk documents from file."""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len,
            )
            
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Loaded {len(chunks)} document chunks from {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return []
    
    def create_vectorstore(self, documents: List[Dict[str, Any]]) -> bool:
        """Create vector store from documents."""
        try:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=VECTOR_STORE_PATH
            )
            self.vectorstore.persist()
            logger.info(f"Created vector store with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return False
    
    def load_existing_vectorstore(self) -> bool:
        """Load existing vector store if available."""
        try:
            if Path(VECTOR_STORE_PATH).exists():
                self.vectorstore = Chroma(
                    persist_directory=VECTOR_STORE_PATH,
                    embedding_function=self.embeddings
                )
                logger.info("Loaded existing vector store")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def setup_retrieval_chain(self):
        """Setup the conversational retrieval chain."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        
        llm = OpenAI(
            openai_api_key=OPENAI_API_KEY,
            temperature=0.1,
            model_name="deepseek/deepseek-r1-0528:free"
        )
        
        self.retrieval_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
            return_source_documents=True,
            verbose=True
        )
        
        logger.info("Setup retrieval chain successfully")
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        if not self.retrieval_chain:
            self.setup_retrieval_chain()
        
        try:
            # Add context to make the agent respond as TariffBot
            enhanced_question = f"""
            You are TariffBot, an intelligent assistant trained on U.S. International Trade Commission data.
            You help importers, analysts, and trade professionals understand tariff rules, duty rates, and policy agreements.
            Always provide clear, compliant, and factual answers grounded in official HTS documentation.
            
            Question: {question}
            """
            
            result = self.retrieval_chain({"question": enhanced_question})
            
            response = {
                "answer": result["answer"],
                "sources": [],
                "question": question
            }
            
            # Extract source information
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    response["sources"].append({
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata
                    })
            
            logger.info(f"Answered question: {question[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def initialize_from_file(self, file_path: str) -> bool:
        """Initialize the RAG system from a document file."""
        try:
            # Load existing vectorstore first
            if self.load_existing_vectorstore():
                logger.info("Using existing vector store")
                return True
            
            # If no existing vectorstore, create new one
            documents = self.load_documents(file_path)
            if not documents:
                return False
            
            success = self.create_vectorstore(documents)
            if success:
                self.setup_retrieval_chain()
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            return False





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

