import fitz
import numpy as np
import cv2
from rapidocr import RapidOCR
import logging

engine = RapidOCR()
logger = logging.getLogger(__name__)

def scanned_doc_ocr(filepath):
    text_output = []
    doc= None
    try:      
        doc = fitz.open(filepath)
        for page_num,page in enumerate(doc,start=1):
            try:
                pix = page.get_pixmap(dpi=150,alpha =False)
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
                logger.exception(f"SCANED CV PDF IS FAILED ON PAGE : {page_num} \n{type(e).__name__} \nError - {e}")
    except Exception as e:
        logger.exception(f"FAILED TO OPEN OR PROCESS PDF FILES !!! \n{type(e).__name__} \nError - {e}")

    finally:
        if doc is not None:
            doc.close()
    final_text = "\n".join(text_output) if len(str(text_output))>50 else ""
    return final_text

# print(scanned_doc_ocr("y_bimali.pdf"))
# 12 s