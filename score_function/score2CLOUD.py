import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from score_function import json_files
from score_function import json_preprocessing
from score_function import llm_fun
from score_function import prompt2CL
from score_function import pydentic_val
from score_function import db

import logging
import time
import glob

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def result_val(data):
    value = list(data.values())
    if '' in list(data.values()) or None in value:
        return 1
    return 0

def cv_score(job_pth,cv_pth):
    score = {
        "cv_files":os.path.basename(cv_pth),
        "Education_score":"",
        "Soft_score":"",
        "Technical_score":"",
        "Impact_score":"",
        "Experience_score":""}
    try:
        data = json_files.prepare_json_data(job_path=job_pth, cv_path=cv_pth)
    except Exception as e:
        logger.error(f"FAILED TO PREPARE JSON DATA FOR {cv_pth}: {type(e).__name__}")
        return score
    
    jd_full = {**data.get("jd_selected_data", {}),
               **data.get("jd_selected_data_2", {}),
               **data.get("jd_selected_data_3", {})}
    cv_full = {**data.get("cv_selected_data", {}),
               **data.get("cv_selected_data_2", {}),
               **data.get("cv_selected_data_3", {})}

    full = None
    try:
        full = llm_fun.main_fun(prompt=prompt2CL.FULL_PROMPT,
                                    jd_json=jd_full,
                                    cv_json=cv_full,
                                    validation_method=pydentic_val.FULLSCORE)
        
        if full is None:
            logger.info("DETAILS OF FULL SCORE IS NONE !!! ")
            raise RuntimeError("FULL SCORING FAILED AFTER ALL RETRIES")

        logger.info(f"[DEBUG] FULLSCORE KEYS RETURNED: {list(full.keys())}")

        score["Education_score"] = full.get("education_score", "")
        score["Soft_score"] = full.get("soft_skill_score", "")
        score["Technical_score"] = full.get("technical_score", "")
        score["Impact_score"] = full.get("impact_score", "")
        for _field in ("education_score","soft_skill_score","technical_score","impact_score"):
            if _field not in full:
                logger.warning(f"[SCHEMA MISMATCH] KEY '{_field}' NOT FOUND IN FULLSCORE OUTPUT — CHECK FIELD NAMES")
        print("scoring done in ONE call. wait 15 second")

    except llm_fun.LLMFatalError:
        raise
    except Exception as e:
        logger.error(f"THERE IS A PROBLEM IN FULL SCORE FUNCTION {type(e).__name__}")

    try:
        exp_year = json_preprocessing.score_experience_years(cv_exp=data["cv_ep"],needed_exp=data["need_ep"])
        if full is None:
            raise RuntimeError("CANNOT COMPUTE EXPERIENCE_SCORE — FULL SCORE IS MISSING")
        score["Experience_score"] = float(full["experience_score"]) + exp_year
    except Exception as e:
        logger.error(f"THERE IS A PROBLEM IN EXPERIENCE (YEAR) OR EXPERIENCE (LLM) SCORE FUNCTION {type(e).__name__}")

    return score



def run_batch(job_path,cv_folder):
    cv_files = glob.glob(os.path.join(cv_folder,"*.json"))
    if not cv_files:
        raise FileNotFoundError(f"NO CV JSON FILE IN THIS FOLDER : '{cv_folder}'")
    result = []
    consecutive_failure = 0
    for cv_path in cv_files:
        try:
            logger.info(f"SCORING START OF CV{os.path.basename(cv_path)}")
            start = time.monotonic()
            minidata = cv_score(job_pth=job_path , cv_pth=cv_path)
            
            try:
                validation = result_val(minidata)
                if validation == 0:
                    consecutive_failure = 0
                    logger.info(f"VALIDATION IS COMPLETED. \nSCORING OF CV {os.path.basename(cv_path)} SUCCESSFULLY FINISHED!")
                    minidata["validation_status"] = "CORRECT" 
                else:
                    consecutive_failure = consecutive_failure + 1
                    if consecutive_failure >= 3:
                        logger.info("3 CVs ARE FAILDED INA ROW. PLEASE WAIT FOR 5 MIN FOR AVOIDING DAYLY ROUTA EXHAUSTED..")
                        time.sleep(120)
                        consecutive_failure = 0
                    logger.info(f"SCORING OF CV {os.path.basename(cv_path)} FAILED!")
                    minidata["validation_status"] = "INCORRECT" 
    
            except Exception as e:
                print("VALIDATION FAILED")
                logger.error(f"VALIDATION TEST IS FAILED ON CV {os.path.basename(cv_path)}")
                minidata["validation_status"] = "SKIPPED VALIDATION PROCESS"
                if consecutive_failure >= 3:
                    logger.info("3 CVs ARE FAILDED INA ROW. PLEASE WAIT FOR 5 MIN FOR AVOIDING DAYLY ROUTA EXHAUSTED..")
                    print("WATING 3 MINITH")
                    time.sleep(120)
                    consecutive_failure = 0
            try:
                db.LoadToDB(minidata)
            except Exception as e:
                logger.error(f"DB WRITE FAILED for {os.path.basename(cv_path)}: {type(e).__name__}")

            result.append(minidata)
            end = time.monotonic()
            wait = end-start
            if wait < 50:
                waiting = 50-wait
                print("wating 50 second")
                time.sleep(waiting)
                continue
            else:
                continue
        except llm_fun.LLMFatalError:
            logger.info("DAILY QUOTA EXHAUSTED — TERMINATING BATCH EARLY. RESULTS SO FAR ARE SAVED.")
            break 
        except Exception as e:
            logger.error(f"THERE IS A PROBLEM IN CV PATH {cv_path} \n{type(e).__name__}")


    if result:
        logger.info(f"LLM OUTPUT OF {len(result)}/{len(cv_files)} IS SUCCUSSFUL")
    else:
        logger.info(f"LLM OUTPUT OF 0/{len(cv_files)} IS FAILED")
        result = []

    
    return result

data = run_batch(job_path="jobpost_details_strongprompt.json",cv_folder="cv_extractions")
print(data)
# db.database(data)