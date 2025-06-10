# 🧠 TariffBot – Intelligent U.S. HTS Assistant 📦

TariffBot is an AI-powered assistant designed to help importers, analysts, and trade professionals interpret the **U.S. Harmonized Tariff Schedule (HTS)**. It combines document retrieval (RAG) and duty calculation into a single intelligent chat agent.

---

## ✨ Features

✅ Ask trade policy questions (e.g., NAFTA, Israel FTA)  
✅ Get detailed duty breakdowns (HTS + cost + weight + quantity)  
✅ Multi-turn memory for natural follow-up questions  
✅ Powered by LangChain agents and OpenRouter LLMs  
✅ Embedding + FAISS for General Notes PDF search  
✅ Streamlit UI 

---

## 🤖 Agent Personality (System Prompt)

> **You are TariffBot — an intelligent assistant trained on U.S. International Trade Commission data.**  
> - You provide factual answers grounded in HTS documentation.  
> - You explain all applicable duties when given HTS code + product info.  
> - You cite relevant General Notes when asked about trade agreements.  
> - You never speculate or offer legal interpretations.  

---

## 🧰 Project Structure
```
hts-agent/
├── README.md
├── requirements.txt
|── stremlit_app.py
├── .env.example
├── config/ # Settings (API key, model name)
├── data/ # Raw HTS PDFs and CSVs
│ ├── downloads/
│ └── vectorstore/
├── scripts/ # Setup scripts for ingestion/vector store
├── src/
│ ├── agents/ # HTSAgent, RAGAgent, TariffAgent
│ ├── tools/ # RAGTool, TariffTool, Embedding loader
│ ├── utils/ # duty calculator
```


---

## 🚀 Getting Started

### 1. Clone the repo
```
git clone https://github.com/yourusername/hts-agent.git
cd hts-agent
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Set API Key
    Add your OpenRouter key to .env

4. Prepare vectorstore (RAG)
```
python scripts/setup_data.py
```

5. Run the app
```
streamlit run streamlit_app.py
```

🧠 Supported LLMs (Free)
The app supports these OpenRouter free-tier models:

```
deepseek-ai/deepseek-r1-0528:free

openchat/openchat-3.5-1210:free

nousresearch/nous-capybara-7b:free

gryphe/mythomax-l2-13b:free

mistralai/mistral-7b-instruct:free

Select model in the sidebar UI.
```

🧪 Example Queries
💬 Trade Policy
```
What is the United States-Israel Free Trade Agreement?
Does NAFTA still apply? Where is General Note 12 referenced?
```

📦 Duty Calculation
```
Calculate duties for HTS 0101.30.00.10, cost 10000, 500 kg, 5 units
```

## 🧠 HTSAgent Architecture
A multi-agent system for tariff estimation and trade policy Q&A using LangChain and OpenRouter LLMs.
![alt text](<ChatGPT Image Jun 10, 2025, 07_00_01 PM.png>)