# Libraries
import logging
import z_text_preprocess
import z_ocr_fun
import os
import re

# Error Handling
logger = logging.getLogger(__name__)

# Personal details Extractor
def preprocess(ext_data, llm_per_data):
    result = {
        "name":"",
        "phone":"",
        "email":"",
        "location":""
    }
    if not ext_data:
        logger.warning("OCR text data is empty. Check OCR process!!!")
        return result
    
    text = ext_data[:1000]
    values = list(llm_per_data.values()) if llm_per_data else []
    
    # name and location
    result["name"] = values[0] if len(values) > 0 else ""
    result["location"] = values[1] if len(values) > 0 else ""

    # Phone number
    try:
        phone = z_text_preprocess.ph_num(text)
        result["phone"]= phone[0] if phone else ""
    
    except Exception as e:
        logger.warnings("Phome number extraction is failed!!!.")
    
    # Email
    try:
        email = z_text_preprocess.emails(text)
        result["email"] = email[0] if email else ""
    
    except Exception as e:
        logger.warning("Email extraction is failed!!!.")
    
    return result

#Final function
def personal_data(filepath):
    if not os.path.isfile(filepath):
        logger.error("File not found : ",filepath)
        return None
    
    # OCR Text data
    try:
        extracted_data = z_ocr_fun.extraction(filepath)
    
    except Exception as e:
        logger.exception("Extraction is failed for ", filepath,e)

    if not extracted_data or not extracted_data.strip():
        logger.warning("No text extraction from  ",filepath)
        return None
    
    # Name and Location
    try:
        cleaned = re.sub('\n'," ",extracted_data[:1000])
        name_loc = z_text_preprocess.all(cleaned)
    
    except Exception as e:
        logger.error("LLM Output is wrong!!!.Check it",filepath,e)
        name_loc = {}

    return preprocess(extracted_data,name_loc)

print(personal_data("y_Associate Data Scientist Induwara Dilshan.pdf"))

# Checking part
# result = personal_data("y_Associate Data Scientist Induwara Dilshan.pdf")
# if result:
#     print(result)
# else:
#     print("Personal Data Extraction is failed!!!")