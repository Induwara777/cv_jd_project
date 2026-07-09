import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Libraries
import logging
import z_text_preprocess
import re
import json

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

# personal_data_from_text function
def personal_data_from_text(cv_id,extracted_data):

    if not extracted_data or not extracted_data.strip():
        logger.warning("No text extraction from  ",cv_id)
        return None
    
    # Name and Location
    try:
        cleaned = re.sub('\n'," ",extracted_data[:1000])
        name_loc = z_text_preprocess.all(cleaned)
    
    except Exception as e:
        logger.error("LLM Output is wrong!!!.Check it",cv_id,e)
        name_loc = {}

    return preprocess(extracted_data,name_loc)

# Final Function
def personal_data_json(input_json, output_json):
    # loading input json
    with open(input_json,"r",encoding="utf-8") as f:
        row_ocr_data = json.load(f)
    
    results = {}

    for i,j in row_ocr_data.items():
        try:
            result = personal_data_from_text(i,j)
            results[i] = result
        except Exception as e:
            logger.exception("Failded preprocesing %s: %s",i,e)
            results[i] = None
        
    with open(output_json,"w",encoding="utf-8") as f:
        json.dump(results,f,indent=4)
    
    return results

print(personal_data_json("row_ocr_output\\row_ocr_cv_deatils.json","personal details\\full_personal_data.json"))