import z_cv_json_creation
import z_ocr_fun
import z_scanned_ocr
import logging

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
            length = z_ocr_fun.text_len(pdf)
            if length <= 30:
                try:
                    text = z_scanned_ocr.scanned_doc_ocr(pdf)
                except Exception as e:
                    logger.exception("Scaned ocr function is failed!!!",e)
            else:               
                try:
                    text = z_ocr_fun.extraction(pdf)
                except Exception as e:
                    logger.error("Extraction is Failed!!!",e)
            text = text if len(text) > 20 else ""
            extracted_data[i] = text.encode("ascii", "ignore").decode().strip()
    except Exception as e:
        logger.error("CV name list can be empty list !!!",e)
    return extracted_data
