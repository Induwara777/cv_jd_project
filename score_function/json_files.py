import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from score_function import json_preprocessing as jp
import logging
logger = logging.getLogger(__name__)

# jd_json,cv_json = jp.json_preprocess(job_pth="jobpost_details_strongprompt.json",cv_pth="one_cv_extraction.json")

# Fun 1
def prepare_json_data(job_path ,cv_path ):
    jd_json,cv_json = jp.json_preprocess(job_pth=job_path,cv_pth=cv_path)
    data = {}

    try:
        data["jd_selected_data"] = {
            "Education": jd_json["education"],
            "softskill": jd_json["skills"]["soft_required"]
        }

        data["cv_selected_data"] = {
            "Education": cv_json["education"],
            "softskill": cv_json["soft_skills"]
        }

        # Fun 2
        data["jd_selected_data_2"] = {
            "tech_required_skill": jd_json["skills"]["technical_required"],
            "tech_preffered_skill": jd_json["skills"]["technical_preferred"]
        }

        data["cv_selected_data_2"] = {
            "technical_skill": jp.getting_keyword(cv_json),
            "impact_details": jp.getting_text_project(cv_json)
        }

        # Fun 3
        data["jd_selected_data_3"] = {
            "job_role": jd_json["responsibilities"]
        }

        data["cv_selected_data_3"] = {
            "jobs":jp.getting_text_project(cv_json)
        }

        data["cv_ep"] = cv_json['experience']['total_experience_years']
        data["need_ep"] = jd_json['experience']['min_experience_years']
    except Exception as e:
        logger.exception(f"JD/CV DETAILS ARE NOT FOUND : {type(e).__name__} - {e}")
        data = {}

    return data


