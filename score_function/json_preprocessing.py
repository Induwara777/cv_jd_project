import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import logging

logger = logging.getLogger(__name__)

def getting_keyword(json):
    keyword = []
    keyword.extend([kw for i in range(len(json['projects'])) for kw in list(json['projects'][i].values())[2]])
    tech = json['technical_skills']
    keywords = keyword + tech
    return list(set(keywords))

def getting_text_project(json):
    text = []
    for i in range(len(json["projects"])):
        data = list(json['projects'][i].values())[1]
        text.append(data)
    return text

def score_experience_years(needed_exp, cv_exp, max_marks=15):
    if cv_exp >= needed_exp:
        return max_marks
    elif needed_exp == 0:
        return max_marks
    else:
        return round((cv_exp / needed_exp) * max_marks)

def json_preprocess(job_pth:str,cv_pth:str) ->tuple[dict,dict]:
    jd_json = {}
    cv_json = {}
    try:
        with open(job_pth, "r") as f:
            jd_json = json.load(f)
    except Exception as e:
        logger.exception(f"JOB DETAILS JSON FILLES ARE NOT FOUND : {job_pth} \nERROR : {e}")

    try:
        with open(cv_pth, "r") as f:
            cv_json = json.load(f)
    except Exception as e:
        logger.exception(f"CV DETAILS JSON FILLES ARE NOT FOUND : {cv_pth} \nERROR : {e}")

    return jd_json,cv_json
