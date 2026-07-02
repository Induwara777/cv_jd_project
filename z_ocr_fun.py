# Libraries
import re
import fitz
import requests


# OCR Extraction (PDF - TEXABLE)
def extraction(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text = text + page.get_text()
    text1 = re.sub("\n"," ",text)
    return text1


# OCR Extraction (PDF - SCANNED DOC)
def ocr_space(file_path,api_key = "helloworld"):
    url = "http://api.ocr.space/parse/image"

    with open(file_path,"rb") as f:
        response = requests.post(
            url , 
            files = {"file":f},
            data ={
                "apikey":api_key,
                "language":"eng"
            }
        )
    
    result = response.json()
    text_data = result["ParsedResults"][0]["ParsedText"]

    return text_data


# OCR text length fun
def text_len(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text = text + page.get_text()
    return len(text)
 