import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv_extractions.z_cv_extraction_full as full
from score_function import score2CLOUD
import logging, json, time

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def is_missing(value):
    return value is None or value == "" or value == [] or value == {}


def json_valid(data: dict) -> bool:
    if is_missing(data.get("technical_skills")):
        return False

    if is_missing(data.get("soft_skills")):
        return False

    if is_missing(data.get("projects")):
        return False

    if is_missing(data.get("experience", {}).get("total_experience_years")):
        return False

    if is_missing(data.get("education", {}).get("highest_qualification")):
        return False

    return True


# ---------------------------------------------------------------------------
# PROPOSED STRUCTURE (per-CV pipeline)
# Old flow: extract ALL CVs (phase 4) -> THEN score ALL CVs (phase 5)
#   -> both phases independently burst-fire requests -> TPM/RPM errors
# New flow: for each CV -> extract -> score -> save to DB -> next CV
#   -> only ever 1 extraction call + 1 scoring call in flight at a time
# ---------------------------------------------------------------------------
def process_and_score_texts(masked_texts: dict, job_spec_path: str, cv_details_dir: str) -> list:
    """
    For each CV: run extraction (1st LLM), save the extraction JSON to disk,
    run scoring (2nd LLM) against that saved JSON, validate, and write the
    score to the DB — all before moving on to the next CV.

    masked_texts:   dict of {cv_id: masked_ocr_text}, same shape as before.
    job_spec_path:  path to the uploaded job-spec file for this session.
    cv_details_dir: folder to save each CV's extracted JSON into. cv_score()
                    needs this saved JSON path (it reads from disk via
                    json_files.prepare_json_data), so writing to disk here
                    is required, not just a debug artifact.
    """
    os.makedirs(cv_details_dir, exist_ok=True)
    results = []
    total = len(masked_texts)
    consecutive_failure = 0

    for idx, text in masked_texts.items():
        start = time.monotonic()
        logger.info(f"PROCESSING CV NUMBER: {idx}")

        # ---------- Step 1: Extraction (1st LLM) ----------
        try:
            extracted = full.final_CV_details(text)
        except Exception as e:
            logger.exception(f"EXTRACTION FAILED FOR CV {idx}: {type(e).__name__}")
            extracted = {}

        cv_json_path = os.path.join(cv_details_dir, f"{idx}.json")
        with open(cv_json_path, "w", encoding="utf-8") as f:
            json.dump(extracted if extracted else None, f, indent=2, ensure_ascii=False)

        if not extracted or not json_valid(extracted):
            logger.warning(f"CV {idx}: EXTRACTION EMPTY/INCOMPLETE — SKIPPING SCORING FOR THIS CV")
            results.append({"cv_files": idx, "validation_status": "EXTRACTION_FAILED"})
            # Still pace even on a skipped CV, in case the extraction call
            # itself consumed quota before failing.
            elapsed = time.monotonic() - start
            if elapsed < 20:
                time.sleep(20 - elapsed)
            continue

        # ---------- Step 2: Scoring (2nd LLM) ----------
        try:
            minidata = score2CLOUD.cv_score(job_pth=job_spec_path, cv_pth=cv_json_path)
        except score2CLOUD.llm_fun.LLMFatalError:
            logger.info("DAILY QUOTA EXHAUSTED — STOPPING BATCH EARLY. RESULTS SO FAR ARE SAVED.")
            break
        except Exception as e:
            logger.error(f"SCORING FAILED FOR CV {idx}: {type(e).__name__}")
            results.append({"cv_files": idx, "validation_status": "SCORING_FAILED"})
            continue

        # ---------- Step 3: Validate ----------
        try:
            invalid = score2CLOUD.result_val(minidata)
            if invalid == 0:
                consecutive_failure = 0
                minidata["validation_status"] = "CORRECT"
                logger.info(f"CV {idx}: EXTRACTION + SCORING SUCCEEDED")
            else:
                consecutive_failure += 1
                minidata["validation_status"] = "INCORRECT"
                logger.info(f"CV {idx}: SCORING RETURNED INCOMPLETE FIELDS")
                if consecutive_failure >= 3:
                    logger.info("3 CVs FAILED IN A ROW — WAITING 2 MIN TO AVOID QUOTA EXHAUSTION...")
                    time.sleep(120)
                    consecutive_failure = 0
        except Exception:
            logger.error(f"VALIDATION FAILED FOR CV {idx}")
            minidata["validation_status"] = "SKIPPED VALIDATION PROCESS"

        # ---------- Step 4: Save to DB ----------
        try:
            score2CLOUD.db.LoadToDB(minidata)
            logger.info(f"CV {idx}: SCORE SAVED TO DB")
        except Exception as e:
            logger.error(f"DB WRITE FAILED FOR CV {idx}: {type(e).__name__}")

        results.append(minidata)

        # ---------- Pacing: ONE wait covering BOTH LLM calls for this CV ----------
        # Tune MIN_GAP_SECONDS to your actual combined RPM/TPM budget across
        # both the extraction model and the scoring model.
        MIN_GAP_SECONDS = 35
        elapsed = time.monotonic() - start
        if elapsed < MIN_GAP_SECONDS:
            waiting = MIN_GAP_SECONDS - elapsed
            logger.info(f"CV {idx}: PACING — WAITING {waiting:.1f}s BEFORE NEXT CV")
            time.sleep(waiting)

    success_count = sum(1 for r in results if r.get("validation_status") == "CORRECT")
    logger.info(f"BATCH COMPLETED: {success_count}/{total} SUCCEEDED")
    return results


# ---------------------------------------------------------------------------
# Kept for local/manual testing only (matches your note: not used by api.py
# in the merged flow, but still handy to run this file standalone).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    with open("personal details\\masked_all_text.json", "r", encoding="utf-8") as f:
        masked_texts = json.load(f)

    results = process_and_score_texts(
        masked_texts=masked_texts,
        job_spec_path="score_function\\jobpost_details_strongprompt.json",
        cv_details_dir="cv_extractions",
    )

    with open("cv_extractions\\final_cv_details.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)