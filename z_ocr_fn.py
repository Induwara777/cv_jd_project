import fitz
import re

# OCR PDF (Texable PDF file) fn
def extraction(file):
    doc = fitz.open(file)
    text = ""
    for i in doc:
        text = text + i.get_text()
    text1 = re.sub("\n"," ",text).strip()
    
    return text1

# PDF Checking fn
def pdf_checking(file):
    doc = fitz.open(file)
    text = ""
    for i in doc:
        text = text + i.get_text()
    
    return len(text)


