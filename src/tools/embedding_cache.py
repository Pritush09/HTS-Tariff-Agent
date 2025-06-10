import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings

@st.cache_resource(show_spinner="Loading embeddings model...")
def get_cached_embeddings():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
