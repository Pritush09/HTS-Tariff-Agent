# Streamlit UI entrypoint
import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.tariff_agent import TariffAgent
from agents.rag_agent import RagAgent
from utils.duty_calculator import DutyCalculator
from utils.hts_parser import HTSParser

# Page configuration
st.set_page_config(
    page_title="HTS Tariff Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_agents():
    """Initialize the agents if not already in session state"""
    if 'tariff_agent' not in st.session_state:
        st.session_state.tariff_agent = TariffAgent()
    if 'rag_agent' not in st.session_state:
        st.session_state.rag_agent = RagAgent()
    if 'duty_calculator' not in st.session_state:
        st.session_state.duty_calculator = DutyCalculator()

def main():
    # Header
    st.markdown('<h1 class="main-header">🏛️ HTS Tariff Classification Agent</h1>', 
                unsafe_allow_html=True)
    
    # Initialize agents
    initialize_agents()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Agent Selection")
        agent_type = st.selectbox(
            "Choose Agent Type:",
            ["Tariff Classification", "RAG Query", "Duty Calculator"]
        )
        
        st.markdown("### ℹ️ About")
        st.info("""
        This application provides two main facilities:
        
        1. **Tariff Classification**: Classify products and find HTS codes
        2. **RAG Query**: Search through tariff documentation
        3. **Duty Calculator**: Calculate import duties and taxes
        """)
        
        # Settings
        st.markdown("### ⚙️ Settings")
        show_details = st.checkbox("Show detailed results", value=True)
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7, 0.1)
    
    # Main content area
    if agent_type == "Tariff Classification":
        tariff_classification_interface(show_details, confidence_threshold)
    elif agent_type == "RAG Query":
        rag_query_interface(show_details)
    else:
        duty_calculator_interface(show_details)

def tariff_classification_interface(show_details, confidence_threshold):
    """Interface for tariff classification agent"""
    st.markdown('<h2 class="section-header">📋 Product Classification</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Product description input
        product_description = st.text_area(
            "Product Description:",
            placeholder="Enter detailed description of your product...",
            height=100,
            help="Provide as much detail as possible about your product including materials, use, composition, etc."
        )
        
        # Additional options
        with st.expander("🔍 Advanced Options"):
            country_of_origin = st.selectbox(
                "Country of Origin:",
                ["", "China", "Mexico", "Canada", "Germany", "Japan", "India", "Other"]
            )
            
            product_value = st.number_input(
                "Product Value (USD):",
                min_value=0.0,
                value=0.0,
                step=0.01
            )
            
            special_programs = st.multiselect(
                "Special Trade Programs:",
                ["NAFTA/USMCA", "GSP", "CBI", "ATPA", "AGOA"]
            )
    
    with col2:
        st.markdown("### 💡 Tips")
        st.info("""
        **For better results:**
        - Be specific about materials
        - Include intended use
        - Mention manufacturing process
        - Add dimensions if relevant
        """)
    
    # Classification button
    if st.button("🔍 Classify Product", type="primary"):
        if product_description.strip():
            with st.spinner("Classifying product..."):
                try:
                    # Call tariff agent
                    result = st.session_state.tariff_agent.classify_product(
                        product_description,
                        confidence_threshold=confidence_threshold,
                        country_of_origin=country_of_origin or None,
                        product_value=product_value if product_value > 0 else None
                    )
                    
                    display_classification_results(result, show_details)
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', 
                              unsafe_allow_html=True)
        else:
            st.warning("Please enter a product description.")

def rag_query_interface(show_details):
    """Interface for RAG query agent"""
    st.markdown('<h2 class="section-header">🔍 Document Search</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input
        query = st.text_input(
            "Search Query:",
            placeholder="Enter your question about tariffs, HTS codes, or trade regulations...",
            help="Ask questions about specific HTS codes, tariff rates, or trade policies"
        )
        
        # Query options
        with st.expander("🔧 Search Options"):
            search_type = st.selectbox(
                "Search Type:",
                ["Semantic Search", "Keyword Search", "Hybrid"]
            )
            
            max_results = st.slider(
                "Maximum Results:",
                min_value=1,
                max_value=20,
                value=5
            )
            
            document_types = st.multiselect(
                "Document Types:",
                ["HTS Schedule", "Trade Agreements", "Rulings", "Regulations"]
            )
    
    with col2:
        st.markdown("### 💡 Example Queries")
        st.info("""
        - "What is the tariff rate for steel imports?"
        - "HTS code for electronic components"
        - "NAFTA preferential rates"
        - "Classification of textile products"
        """)
    
    # Search button
    if st.button("🔍 Search Documents", type="primary"):
        if query.strip():
            with st.spinner("Searching documents..."):
                try:
                    # Call RAG agent
                    result = st.session_state.rag_agent.query(
                        query,
                        search_type=search_type.lower().replace(" ", "_"),
                        max_results=max_results,
                        document_types=document_types
                    )
                    
                    display_rag_results(result, show_details)
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', 
                              unsafe_allow_html=True)
        else:
            st.warning("Please enter a search query.")

def duty_calculator_interface(show_details):
    """Interface for duty calculator"""
    st.markdown('<h2 class="section-header">💰 Duty Calculator</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Input fields
        hts_code = st.text_input(
            "HTS Code:",
            placeholder="e.g., 8471.30.0100",
            help="Enter the 10-digit HTS code"
        )
        
        value = st.number_input(
            "Product Value (USD):",
            min_value=0.0,
            value=1000.0,
            step=0.01
        )
        
        quantity = st.number_input(
            "Quantity:",
            min_value=1,
            value=1,
            step=1
        )
        
        country_of_origin = st.selectbox(
            "Country of Origin:",
            ["China", "Mexico", "Canada", "Germany", "Japan", "India", "Other"]
        )
    
    with col2:
        # Additional options
        st.markdown("### Additional Fees")
        
        harbor_maintenance_fee = st.checkbox("Harbor Maintenance Fee", value=True)
        merchandise_processing_fee = st.checkbox("Merchandise Processing Fee", value=True)
        
        special_programs = st.multiselect(
            "Trade Programs:",
            ["NAFTA/USMCA", "GSP", "CBI", "ATPA", "AGOA"]
        )
        
        # Entry type
        entry_type = st.selectbox(
            "Entry Type:",
            ["Formal Entry", "Informal Entry"]
        )
    
    # Calculate button
    if st.button("💰 Calculate Duties", type="primary"):
        if hts_code.strip():
            with st.spinner("Calculating duties..."):
                try:
                    # Call duty calculator
                    result = st.session_state.duty_calculator.calculate_duty(
                        hts_code=hts_code,
                        value=value,
                        quantity=quantity,
                        country_of_origin=country_of_origin,
                        special_programs=special_programs,
                        include_fees={
                            'harbor_maintenance_fee': harbor_maintenance_fee,
                            'merchandise_processing_fee': merchandise_processing_fee
                        },
                        entry_type=entry_type.lower().replace(" ", "_")
                    )
                    
                    display_duty_results(result, show_details)
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', 
                              unsafe_allow_html=True)
        else:
            st.warning("Please enter an HTS code.")

def display_classification_results(result, show_details):
    """Display tariff classification results"""
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    
    if result.get('success'):
        st.success("✅ Classification completed successfully!")
        
        # Main results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "HTS Code",
                result.get('hts_code', 'N/A'),
                help="Harmonized Tariff Schedule Code"
            )
        
        with col2:
            st.metric(
                "Confidence",
                f"{result.get('confidence', 0):.1%}",
                help="Classification confidence score"
            )
        
        with col3:
            st.metric(
                "Tariff Rate",
                result.get('tariff_rate', 'N/A'),
                help="General tariff rate"
            )
        
        # Description
        if result.get('description'):
            st.markdown(f"**Description:** {result['description']}")
        
        # Show details if requested
        if show_details and result.get('details'):
            with st.expander("📋 Detailed Information"):
                for key, value in result['details'].items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    else:
        st.error(f"❌ Classification failed: {result.get('error', 'Unknown error')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_rag_results(result, show_details):
    """Display RAG query results"""
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    
    if result.get('success'):
        st.success(f"✅ Found {len(result.get('results', []))} relevant documents")
        
        # Display results
        for i, doc in enumerate(result.get('results', []), 1):
            with st.expander(f"📄 Result {i}: {doc.get('title', 'Document')}"):
                st.markdown(f"**Score:** {doc.get('score', 0):.3f}")
                st.markdown(f"**Source:** {doc.get('source', 'Unknown')}")
                st.markdown(f"**Content:** {doc.get('content', 'No content available')}")
                
                if show_details and doc.get('metadata'):
                    st.json(doc['metadata'])
    
    else:
        st.error(f"❌ Search failed: {result.get('error', 'Unknown error')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_duty_results(result, show_details):
    """Display duty calculation results"""
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    
    if result.get('success'):
        st.success("✅ Duty calculation completed!")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Import Duty",
                f"${result.get('import_duty', 0):,.2f}"
            )
        
        with col2:
            st.metric(
                "Additional Fees",
                f"${result.get('additional_fees', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                "Total Cost",
                f"${result.get('total_cost', 0):,.2f}"
            )
        
        with col4:
            st.metric(
                "Effective Rate",
                f"{result.get('effective_rate', 0):.2%}"
            )
        
        # Breakdown
        if show_details and result.get('breakdown'):
            with st.expander("💰 Cost Breakdown"):
                breakdown = result['breakdown']
                
                for category, amount in breakdown.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(category.replace('_', ' ').title())
                    with col2:
                        st.write(f"${amount:,.2f}")
    
    else:
        st.error(f"❌ Calculation failed: {result.get('error', 'Unknown error')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat interface (bonus feature)
def chat_interface():
    """Simple chat interface for interactive queries"""
    st.markdown('<h2 class="section-header">💬 Chat with Tariff Agent</h2>', 
                unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about tariffs and trade..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # This would call your agent's chat method
                    response = st.session_state.tariff_agent.chat(prompt)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.write(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()