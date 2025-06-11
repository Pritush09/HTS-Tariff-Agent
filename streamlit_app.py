import streamlit as st
from src.agents.hts_agent import HTSAgent
from config.settings import OPENROUTER_API_KEY
import pandas as pd

FREE_MODELS = [
    "deepseek/deepseek-r1-0528:free",
    "mistralai/mistral-7b-instruct:free",
    "deepseek/deepseek-r1-0528-qwen3-8b:free",
    "mistralai/devstral-small:free"
]

st.set_page_config(page_title="HTS Tariff Assistant", layout="wide")
st.title("HTS Tariff Assistant 🤖📦")

selected_model = st.sidebar.selectbox("🧠 Choose LLM Model", FREE_MODELS)

# Session State
if "agent" not in st.session_state or st.session_state.model_name != selected_model:
    st.session_state.agent = HTSAgent(model_name=selected_model)
    st.session_state.model_name = selected_model
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

agent = st.session_state.agent

st.markdown("""
💬 Example queries:
- “What is the United States-Israel Free Trade Agreement?”

- Duty Calculation assumes a structure like XXXX.XX.XX.XX (10 digits, 3 dots)
- “For duty calculation give input like: hts_code=0101.21.00.00, cost=1000, freight=50, insurance=20, weight=200, quantity=10”
""")

query = st.text_area("Enter your query")

if st.button("Submit"):
    if query.strip():
        with st.spinner("Thinking..."):
            response = agent.run(query)
            st.write(response)
            
            tool_used = "DutyEstimator" if "hts" in query.lower() else "TradePolicyQA"
            st.session_state.chat_log.append((query, response, tool_used))
    else:
        st.warning("Please enter a valid question.")

# ✅ Toggle to show chat history
if st.checkbox("📜 Show Chat History"):
    if st.session_state.chat_log:
        st.subheader("Chat History")
        for i, (q, r, tool) in enumerate(reversed(st.session_state.chat_log)):
            st.markdown(f"**You:** {q}")
            st.markdown(f"**Tool Used:** `{tool}`")
            if isinstance(r, dict):
                st.json(r)
                if st.button("📥 Export to CSV", key=f"csv_{i}"):
                    df = pd.DataFrame([r])
                    st.download_button(
                        label="Download CSV",
                        data=df.to_csv(index=False).encode("utf-8"),
                        file_name="tariff_result.csv",
                        mime="text/csv"
                    )
            else:
                st.markdown(f"**TariffBot:** {r}")
        # Optional: Clear button
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_log = []
            st.experimental_rerun()
    else:
        st.info("No conversation history yet.")
