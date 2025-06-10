import os
import pandas as pd
from PyPDF2 import PdfReader

def load_csvs(section_folder):
    dfs = []
    for file in sorted(os.listdir(section_folder)):
        if file.endswith(".csv"):
            dfs.append(pd.read_csv(os.path.join(section_folder, file)))
    return pd.concat(dfs, ignore_index=True)

# def extract_pdf_text(pdf_path):
#     reader = PdfReader(pdf_path)
#     return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

import fitz  # PyMuPDF

def extract_pdf_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text