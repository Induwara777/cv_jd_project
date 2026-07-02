# Libraries
import logging
import os
import re
import z_ocr_fun
import z_personal_data
import z_text_preprocess

# Error Handling
logger = logging.getLogger(__name__)

# Function
def llm_text(filepath):
    # file checking
    if not os.path.isfile(filepath):
        logger.error("File not found : %s",filepath)
        return None
    
    # OCR Text data
    try:
        extracted_data = z_ocr_fun.extraction(filepath)
    except Exception as e:
        logger.exception("Extraction is failed for %s: %s", filepath,e)
        return None
    
    # peronal data extraction
    try:
        data_file = z_personal_data.personal_data(filepath)
    except Exception as e:
        logger.error("LLM Output is wrong!!!.Check it %s:  %s",filepath,e)
        data_file = {}
    
    values = [v for v in data_file.values() if v]
    pattern = "|".join(re.escape(v) for v in values)
    masked = re.sub(pattern, "[MASKED]", extracted_data) if pattern else None
    
    # email masked
    try:
        masked1 = z_text_preprocess.emails_masked(masked)
    except Exception as e:
        logger.exception("Masked data is wrong!!! ",e)
    masked1 = masked1 if masked1 else None

    # phone number masked
    try:
        masked2 = z_text_preprocess.ph_num_masked(masked1)
    except Exception as e:
        logger.exception("Masked data is wrong!!! ",e)
    masked2 = masked2 if masked2 else None
    
    # person names masked
    try:
        masked3 = z_text_preprocess.person(masked2)
    except Exception as e:
        logger.exception("Masked data is wrong!!! ",e)
    
    # final one
    masked3 = masked3 if masked3 else None
    return masked3

print(llm_text("y_Associate Data Scientist Induwara Dilshan.pdf"))