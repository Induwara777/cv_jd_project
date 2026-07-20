import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv_extractions.z_cv_extraction_full as full
import logging, json,time

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def process_masked_texts(masked_texts: dict,output_dir:str) -> dict:
    results = {}
    total = len(masked_texts)
    os.makedirs(output_dir, exist_ok=True)
 
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
        if elapsed < 20:
            waiting = float(20) - float(elapsed)
            if waiting > 0:
                time.sleep(waiting)
        with open(os.path.join(output_dir, f"{idx}.json"), "w", encoding="utf-8") as f:
            json.dump(results[idx], f, indent=2, ensure_ascii=False)

    success_count = sum(1 for r in results.values() if r)
    logger.info(f"BATCH COMPLETED : {success_count}/{total} SUCCEEDED !")

    return results

def process_masked_texts_file(input_json, output_dir, combined_output_path):
    with open(input_json, "r", encoding="utf-8") as f:
        dataset = json.load(f)
 
    results = process_masked_texts(dataset, output_dir)
 
    os.makedirs(os.path.dirname(combined_output_path), exist_ok=True)
    with open(combined_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
 
    return results

if __name__ == "__main__":
    process_masked_texts_file(
        input_json="personal details\\masked_all_text.json",
        output_dir="cv_extractions",
        combined_output_path="cv_extractions\\final_cv_details.json",
    )