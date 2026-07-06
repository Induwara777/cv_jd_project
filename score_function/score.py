import json_files,json_preprocessing,llm_fun,prompt,pydentic_validation
import logging
import time
import random

logger = logging.getLogger(__name__)
def cv_score():
    score = {"Education_score":"",
             "Soft_score":"",
             "Technical_score":"",
             "Impact_score":"",
             "Experience_score":""}
    try :
        edu_soft = llm_fun.main_fun(prompt=prompt.EDU_SOFT_IMPACT_PROMPT_TEMPLATE,
                                    jd_json=json_files.jd_selected_data, 
                                    cv_json=json_files.cv_selected_data,
                                    validation_method=pydentic_validation.fullScore)
        score["Education_score"] = list(edu_soft.values())[0]
        score["Soft_score"] = list(edu_soft.values())[1]
        time.sleep(random.randint(0,5))
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN EDUCATION AND SOFT SCORE FUNCTION {type(e).__name__} - {e}")
        time.sleep(random.randint(0,5))
    try :
        tech_impact = llm_fun.main_fun(prompt=prompt.EXP_TECH_IMPACT_PROMPT_TEMPLATE,
                                    jd_json=json_files.jd_selected_data_2, 
                                    cv_json=json_files.cv_selected_data_2,
                                    validation_method=pydentic_validation.skillScore)
        score["Technical_score"] = list(tech_impact.values())[0]
        score["Impact_score"] = list(tech_impact.values())[1]
        time.sleep(random.randint(0,5))
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN TECH AND IMPACT SCORE FUNCTION {type(e).__name__} - {e}")
        time.sleep(random.randint(0,5))
    try :
        exp_tech = llm_fun.main_fun(prompt=prompt.EXP_TEMPLATE,
                                    jd_json=json_files.jd_selected_data_3, 
                                    cv_json=json_files.cv_selected_data_3,
                                    validation_method=pydentic_validation.ExpScore)
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN EXPERIENCE (TECHNICAL) SCORE FUNCTION {type(e).__name__} - {e}") 

    try:
        exp_year = json_preprocessing.score_experience_years(cv_exp=json_files.cv_ep,needed_exp=json_files.need_ep)
        score["Experience_score"] = list(exp_tech.values())[0] + exp_year
    except Exception as e:
        logger.exception(f"THERE IS A PROBLEM IN EXPERIENCE (YEAR) OR EXPERIENCE (TECHNICAL) SCORE FUNCTION {type(e).__name__} - {e}")

    return score

result = cv_score()
print(result)






















