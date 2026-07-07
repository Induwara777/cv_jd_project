import z_cv_extraction_set
import logging
import time
import random
logger = logging.getLogger(__name__)

def extract_section_with_retry(main_file: dict, section_name: str, extractor_fn, text_data, retry: int = 3):
    for attempt in range(1, retry + 1):
        try:
            main_file.update(extractor_fn(text_data))
            return  
        except Exception as e:
            logger.exception(
                f"{section_name.upper()} SECTION FAILED (attempt {attempt}/{retry}): {type(e).__name__} - {e}"
            )
            time.sleep(random.randint(2, 4))

    logger.error(f"{section_name.upper()} SECTION FAILED PERMANENTLY after {retry} attempts")
    main_file[section_name] = {"ERROR": "ALL RETRIES FAILED"}


def extract_full_cv(text_data, retry: int = 3) -> dict:
    main_file = {}

    extract_section_with_retry(main_file, "education", z_cv_extraction_set.education, text_data, retry)
    extract_section_with_retry(main_file, "skills", z_cv_extraction_set.skills, text_data, retry)
    extract_section_with_retry(main_file, "project", z_cv_extraction_set.project, text_data, retry)
    extract_section_with_retry(main_file, "experience", z_cv_extraction_set.experience, text_data, retry)

    return main_file