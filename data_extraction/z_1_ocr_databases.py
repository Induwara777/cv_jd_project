import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import ocr.z_ocr_fun
import ocr.z_scanned_ocr
import logging
import z_cv_json_creation

logger = logging.getLogger(__name__)

def text_save(filepath):
    try:
        file_names = z_cv_json_creation.file_name(filepath)
    except Exception as e:
        logger.error("Getting CV names is failed !!!",e)

    file_names = file_names if len(file_names) >= 1 else []

    extracted_data = {}
    try:
        for i,pdf in enumerate(file_names):
            try:
                text = ocr.z_ocr_fun.extraction(pdf)
            except Exception as e:
                logger.exception(f"PDF TEXABLE EXTRACTION FUNCTION IS FAILED. {type(e).__name__} - {e}")
            length = len(text) if len(text) else 0
            if length <= 50:
                try:
                    text = ocr.z_scanned_ocr.scanned_doc_ocr(pdf)
                except Exception as e:
                    logger.exception("Scaned ocr function is failed!!!",e)          
            text = text if len(text) > 50 else ""
            extracted_data[i] = text.encode("ascii", "ignore").decode().strip()
    except Exception as e:
        logger.error("CV NAME LIST CAN'T BE EMPTY !!!",e)
    return extracted_data



