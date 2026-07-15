import z_cv_extraction_set
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging
logger = logging.getLogger(__name__)

def extract_section_with_retry_return(section_name, extractor_fn, text_data):
    try:
        return extractor_fn(text_data)
    except Exception as e:
        logger.error(f"{section_name.upper()} FAILED PERMANENTLY ")
        return {f"{section_name}": "ALL RETRIES FAILED"}
    
def extract_full_cv(text_data) -> dict:
    main_file = {}
    sections = {
        "experience": z_cv_extraction_set.experience,
        "project": z_cv_extraction_set.project,
        "skills": z_cv_extraction_set.skills,
        "education": z_cv_extraction_set.education,
    }

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {
            executor.submit(extract_section_with_retry_return, name, fn, text_data): name
            for name, fn in sections.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            main_file[name] = future.result()

    return main_file


def extract_all_cvs(cv_dict: dict, save_path: str = "GPT_TEST") -> dict:
    results = {}
    total = len(cv_dict)

    # Sequential: one CV at a time, no thread pool here
    for i, (cv_id, text_data) in enumerate(cv_dict.items(), start=1):
        logger.info(f"Processing {cv_id} ({i}/{total})")
        try:
            results[cv_id] = extract_full_cv(text_data)
        except Exception as e:
            logger.exception(f"FAILED to process {cv_id}\n{type(e).__name__} - {e}")
            results[cv_id] = {"error": str(e)}

        logger.info(f"Completed {cv_id} ({i}/{total})")

        # save incrementally after each CV
        with open(f"{save_path}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Done. Processed {total} CVs.")
    return results

# with open("personal details\masked_all_text.json","r",encoding="utf-8") as f:
#     data = json.load(f)

# details = extract_all_cvs(data)
# print(details)