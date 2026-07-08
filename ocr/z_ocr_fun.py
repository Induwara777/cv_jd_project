# Libraries
import re
import fitz
import os


# OCR Extraction (PDF - TEXABLE)
def extraction(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text = text + page.get_text()
    text1 = re.sub("\n"," ",text)
    return text1.strip()


# OCR text length fun
def text_len(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text = text + page.get_text()
    return len(text)

# Catching all names in a folder
def file_name(folder):
    names = [f for f in os.listdir(folder) if f.endswith(".pdf") ]
    return names
 