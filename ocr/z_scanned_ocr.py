import fitz
import numpy as np
import cv2
from rapidocr import RapidOCR
import logging

engine = RapidOCR()
logger = logging.getLogger(__name__)

def scanned_doc_ocr(filepath):
    text_output = []
    try:      
        doc = fitz.open(filepath)
        for page_num,page in enumerate(doc,start=1):
            try:
                pix = page.get_pixmap(dpi=200)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, pix.n
                )
                if pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                result = engine(img)
                text_output.append(" ".join(result.txts))
            except Exception as e:
                logger.exception(f"SCANED CV PDF IS FAILED ON PAGE : {page_num}")
        doc.close()
    except Exception as e:
        logger.exception("Failed to open or process PDF file",e)
    final_text = "\n".join(text_output) if len(str(text_output))>50 else ""
    return final_text
