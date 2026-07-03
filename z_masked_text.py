# Libraries
import logging
import re
import z_text_preprocess
import json

# Error Handling
logger = logging.getLogger(__name__)

# Function
def llm_text(peronal_json,extract_json,output_json):
    with open(peronal_json,"r",encoding="utf-8") as f:
        personal_data = json.load(f)
    
    with open(extract_json,"r",encoding="utf-8") as f:
        cv_data = json.load(f)
    
    masked_json = {}
    
    try:
        for cv_id,cv_text in cv_data.items():
            info = personal_data.get(cv_id,{})
            value = [ str(v).strip() for v in info.values() if v ]
            pattern = "|".join(re.escape(x) for x in value) if value else None
            masked = re.sub(pattern, "[MASKED]", cv_text) if pattern else None
        
            # email masked
            try:
                masked1 = z_text_preprocess.emails_masked(masked)
            except Exception as e:
                logger.exception(f"MASKING EMAIL IS FAILED ON CV : {cv_id} :{e} ")
            masked1 = masked1 if masked1 else None

            # phone number masked
            try:
                masked2 = z_text_preprocess.ph_num_masked(masked1)
            except Exception as e:
                logger.exception(f"MASKING PHONE NUMBER IS FAILED ON CV : {cv_id} :{e} ")
            masked2 = masked2 if masked2 else None
        
            # person names masked
            try:
                masked3 = z_text_preprocess.person(masked2)
            except Exception as e:
                logger.exception(f"MASKING PERONAL DATA IS FAILED ON CV : {cv_id} :{e} ")
            
            # final one
            masked3 = masked3 if masked3 else None
            masked_json[cv_id] = masked3
        with open(output_json,"w",encoding="utf-8") as f:
            json.dump(masked_json,f,indent=2)
    except Exception as e:
        logger.exception(f"ENTIRE CV TEXT MASKING PROCESS IS BROKEN! : {e}")
    
    return masked_json
llm_text(peronal_json="personal details\\full_personal_data.json",
         extract_json="row_ocr_output\\row_ocr_cv_deatils.json",
         output_json="personal details\\masked_all_text.json")
