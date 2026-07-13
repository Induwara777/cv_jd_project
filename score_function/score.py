import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from score_function import json_files
from score_function import json_preprocessing
from score_function import llm_fun
from score_function import prompt
from score_function import pydentic_validation
from score_function import db

import logging
import time
import random
import glob

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def cv_score(job_pth,cv_pth):
    score = {
        "cv_files":os.path.basename(cv_pth),
        "Education_score":"",
        "Soft_score":"",
        "Technical_score":"",
        "Impact_score":"",
        "Experience_score":""}
    data = json_files.prepare_json_data(job_path=job_pth, cv_path=cv_pth)
    try :
        edu_soft = llm_fun.main_fun(prompt=prompt.EDU_SOFT_IMPACT_PROMPT_TEMPLATE,
                                    jd_json=data["jd_selected_data"], 
                                    cv_json=data["cv_selected_data"],
                                    validation_method=pydentic_validation.fullScore)
        score["Education_score"] = list(edu_soft.values())[0]
        score["Soft_score"] = list(edu_soft.values())[1]
        time.sleep(random.randint(0,5))
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN EDUCATION AND SOFT SCORE FUNCTION {type(e).__name__} - {e}")
        time.sleep(random.randint(0,5))
    try :
        tech_impact = llm_fun.main_fun(prompt=prompt.EXP_TECH_IMPACT_PROMPT_TEMPLATE,
                                    jd_json=data["jd_selected_data_2"], 
                                    cv_json=data["cv_selected_data_2"],
                                    validation_method=pydentic_validation.skillScore)
        score["Technical_score"] = list(tech_impact.values())[0]
        score["Impact_score"] = list(tech_impact.values())[1]
        time.sleep(random.randint(0,5))
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN TECH AND IMPACT SCORE FUNCTION {type(e).__name__} - {e}")
        time.sleep(random.randint(0,5))
    try :
        exp_tech = llm_fun.main_fun(prompt=prompt.EXP_TEMPLATE,
                                    jd_json=data["jd_selected_data_3"], 
                                    cv_json=data["cv_selected_data_3"],
                                    validation_method=pydentic_validation.ExpScore)
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN EXPERIENCE (TECHNICAL) SCORE FUNCTION {type(e).__name__} - {e}") 

    try:
        exp_year = json_preprocessing.score_experience_years(cv_exp=data["cv_ep"],needed_exp=data["need_ep"])
        score["Experience_score"] = list(exp_tech.values())[0] + exp_year
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN EXPERIENCE (YEAR) OR EXPERIENCE (TECHNICAL) SCORE FUNCTION {type(e).__name__} - {e}")

    return score

def run_batch(job_path,cv_folder):
    cv_files = glob.glob(os.path.join(cv_folder,"*.json"))
    result = []

    for cv_path in cv_files:
        try:
            logger.info(f"SCORING {os.path.basename(cv_path)}")
            start = time.monotonic()
            result.append(cv_score(job_pth=job_path , cv_pth=cv_path))
            logger.info(f"SCORING OF CV {os.path.basename(cv_path)} SUCCESSFULLY FINISHED!")
            end = time.monotonic()
            wait = end-start
            if wait < 25:
                waiting = 25-wait
                time.sleep(waiting)
                continue
            else:
                continue
        except Exception as e:
            logger.exception(f"THERE IS A PROBLEM IN CV PATH {cv_path} \n{type(e).__name__} \nError - {e}")

    try:
        if result:
            logger.info(f"LLM OUTPUT OF {os.path.basename(cv_path)} IS SUCCUSSFUL")
        else:
            logger.info(f"LLM OUTPUT OF {os.path.basename(cv_path)} IS FAILED")
    except Exception as e:
        logger.exception(f"{type(e).__name__} \nError - {e}")
        result = []
    
    return result
# data = run_batch(job_path="jobpost_details_strongprompt.json",cv_folder="cv_extractions")
# db.database(data)















