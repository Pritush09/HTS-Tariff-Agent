import streamlit as st
from src.agents.rag_agent import RAGAgent
from src.agents.tariff_agent import TariffAgent

st.title("HTS Tariff Assistant")

agent_type = st.sidebar.selectbox("Choose Agent", ["RAG Agent", "Tariff Agent"])

if agent_type == "RAG Agent":
    agent = RAGAgent()
    query = st.text_input("Ask a trade question")
    if st.button("Submit"):
        response = agent.run(query)
        st.write(response)
else:
    code = st.text_input("Enter HTS Code")
    cost = st.number_input("Enter Product Cost", min_value=0.0)
    if st.button("Calculate"):
        agent = TariffAgent("data/downloads/section1/1.csv")  # load first CSV
        result = agent.run(code, cost)
        st.write(result)