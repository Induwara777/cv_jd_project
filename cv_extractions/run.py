import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv_extractions.z_cv_extraction_full as full
import logging, json,time

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def process_masked_texts(masked_texts: dict) -> dict:
    results = {}
    total = len(masked_texts)
 
    for idx, text in masked_texts.items():
        flag = True
        start = time.monotonic()
        logger.info(f"PROCESSING CV NUMBER : {idx}")
 
        try:
            data = full.final_CV_details(text)
            flag = True
        except Exception as e:
            logger.exception(f"UNEXPECTED FAILURE ON CV {idx}: \n{type(e).__name__} \nError - {e}")
            flag = False
            data = {}

        results[idx] = data if data else None
        if flag:
            logger.info(f"JSON FILE FOR CV NUMBER {idx} IS  SUCCESSFULLY SAVED !")
        else:
             logger.info(f"JSON FILE FOR CV NUMBER {idx} IS FAILED!")
        end = time.monotonic()
        elapsed = end - start
        if elapsed < 15:
            waiting = float(15) - float(elapsed)
            if waiting > 0:
                time.sleep(waiting)
        with open(f"cv_extractions\\{idx}.json", "w", encoding="utf-8") as f:
            json.dump(results[idx], f, indent=2, ensure_ascii=False)

    success_count = sum(1 for r in results.values() if r)
    logger.info(f"BATCH COMPLETED : {success_count}/{total} SUCCEEDED !")

# Run 
with open("personal details\\masked_all_text.json" , "r", encoding="utf-8") as f:
    dataset = json.load(f)
process_masked_texts(masked_texts=dataset)