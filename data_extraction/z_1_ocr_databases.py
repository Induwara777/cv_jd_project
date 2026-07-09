import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import ocr.z_ocr_fun , ocr.z_scanned_ocr
import logging
import z_cv_json_creation

logger = logging.getLogger(__name__)

def text_save(filepath):
    try:
        file_names = z_cv_json_creation.file_name(filepath)
    except Exception as e:
        logger.error(f"CV NAMES LOADING IS FAILD.!!! PLEASE CHECK CV LOCATION. \n{type(e).__name__}  \nError - {e}")
        file_names = []
    
    file_names = file_names if len(file_names) >= 1 else []

    extract_read = ocr.z_ocr_fun.extraction
    extract_scann = ocr.z_scanned_ocr.scanned_doc_ocr
    extracted_data = {}
    try:
        for i,pdf in enumerate(file_names):
            try:
                text = extract_read(pdf)
            except Exception as e:
                logger.exception(f"PDF TEXABLE EXTRACTION FUNCTION IS FAILED. \n{type(e).__name__} \nError - {e}")
            length = len(text) if len(text) else 0
            if length <= 50:
                try:
                    text = extract_scann(pdf)
                except Exception as e:
                    logger.exception(f"SCANNED DOC FUNCTION IS FAILED!!! \n{type(e).__name__} \nError - {e}")          

            extracted_data[i] = text.encode("ascii", "ignore").decode().strip() if len(text) > 50 else ""
    except Exception as e:
        logger.error(f"CV NAME LIST CAN'T BE EMPTY !!! \n{type(e).__name__} \nError - {e}")
    return extracted_data
