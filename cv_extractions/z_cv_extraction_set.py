import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import json
from openai import OpenAI
import logging
from groq import RateLimitError
import time
logger = logging.getLogger(__name__)

# LLM API KEY
try:
    os.environ['OPENAI_API_KEY'] = "masked"
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1"
    )
except Exception as e:
    logger.exception(f"THERE IS A PROBLEM IN GPT OSS MODEL API KEY {type(e).__name__} - {e}")


import re
import json

def education(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

Rules:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Use null for missing values.
- Extract O/L, A/L, degree, and certificate information if available.
- Set "highest_qualification" to the highest completed qualification (ol, al, hnd, degree).


JSON STRUCTURE:
{{
  "education": {{
    "highest_qualification": null,

    "ol": {{
      "year": null,
      "subjects": [
        {{
          "subject": "",
          "grade": ""
        }}
      ]
    }},

    "al": {{
      "year": null,
      "stream": null,
      "subjects": [
        {{
          "subject": "",
          "grade": ""
        }}
      ]
    }},

    "degrees": [
      {{
        "degree_name": ""
      }}
    ],

    "certificates": [
      {{
        "name": ""
      }}
    ]
  }}
}}

TEXT:
{text}
"""

    data = {}
    output = ""

    for attempt in range(2):  
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.0,
                max_tokens=2000, 
                response_format={"type": "json_object"}
            )
        except RateLimitError as e:
            retry = e.response.headers.get("retry-after")
            logger.warning(f"FUCNTION: RATE LIMITED, retry_after={retry}")
            if retry:
                time.sleep(retry)
                continue
        except Exception as e:
            logger.exception(f"EDUCATION FUNCTION API CALL FAILED\n{type(e).__name__} - {e}")
            time.sleep(6)
            continue

        choice = response.choices[0]
        finish_reason = getattr(choice, "finish_reason", None)
        output = (choice.message.content or "").strip()

        logger.info(f"education() attempt {attempt+1} | finish_reason={finish_reason} | output_len={len(output)}")

        if finish_reason == "content_filter":
            logger.warning("education(): response blocked by content_filter, retrying...")
            time.sleep(6)
            continue

        if output:
            break 

    if not output:
        logger.error("EDUCATION FUNCTION FAILED: empty output after retries")
        return data

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output.strip())
    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.exception(f"EDUCATION FUNCTION JSON PARSE FAILED\n{type(e).__name__} - {e}\nRAW OUTPUT: {output!r}")
        data = {}

    return data


# skill fun
def skills(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

Rules:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Return all technical and soft skills in the CV in profile_summary and soft_skills section.


JSON STRUCTURE:
{{
    "Technical_skills": "",
    "soft_skills":""
}}

TEXT:
{text}
"""
    data = {}
    output = ""
    for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model = "openai/gpt-oss-120b",
                    messages = [{
                        "role":"user",
                        "content" : prompt
                    }],
                    temperature=0.0,
                    max_tokens = 2000,
                    response_format={"type": "json_object"}
                )
            
            except Exception as e:
                logger.exception(f"SKILL FUNCTION API CALL FAILED\n{type(e).__name__} - {e}")
                continue

            choice = response.choices[0]
            finish_reason = getattr(choice, "finish_reason", None)
            output = (choice.message.content or "").strip()

            logger.info(f"skill() attempt {attempt+1} | finish_reason={finish_reason} | output_len={len(output)}")

            if finish_reason == "content_filter":
                logger.warning("skill(): response blocked by content_filter, retrying...")
                continue

            if output:
                break 

            if not output:
                logger.error("SKILL FUNCTION FAILED: empty output after retries")
                return data

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output.strip())
    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.exception(f"SKILL FUNCTION JSON PARSE FAILED\n{type(e).__name__} - {e}\nRAW OUTPUT: {output!r}")
        data = {}

    return data


# experience fun
def experience(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.



CALCULATION RULES (follow exactly, do not explain your steps in the output):

1. DO NOT GUESS for duration_year
2. Read entire data.
3. Find all related to experiences.
4. using your intelligence, give experiences as month counts. IT IS MUST.
5. Finaly, MUST CALCULATE total_experience_years.

OUTPUT RULES:
- Return ONLY a single valid JSON object.
- Do NOT include any text, explanation, notes, or commentary before or after the JSON.
- Do NOT wrap the JSON in markdown code fences (no ```json).
- Do NOT add or remove fields from the structure below.
- Use null for any missing values.


JSON STRUCTURE:
{{
  "experience": [
    {{
    "total_experience_years": "",
    "jobs": [
      {{
        "job_title": "",
        "duration_month": null
      }}
    ]
    }}
]
}}

TEXT:
{text}
"""
    data = {}
    output = ""
    for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model = "openai/gpt-oss-120b",
                    messages = [{
                        "role":"user",
                        "content" : prompt
                    }],
                    temperature=0.0,
                    max_tokens = 2000,
                    response_format={"type": "json_object"}
                )
            
            except Exception as e:
                logger.exception(f"EXPERIENCE FUNCTION API CALL FAILED\n{type(e).__name__} - {e}")
                continue

            choice = response.choices[0]
            finish_reason = getattr(choice, "finish_reason", None)
            output = (choice.message.content or "").strip()

            logger.info(f"education() attempt {attempt+1} | finish_reason={finish_reason} | output_len={len(output)}")

            if finish_reason == "content_filter":
                logger.warning("experience(): response blocked by content_filter, retrying...")
                continue

            if output:
                break 

            if not output:
                logger.error("EXPERIENCE FUNCTION FAILED: empty output after retries")
                return data

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output.strip())
    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.exception(f"EXPERIENCE FUNCTION JSON PARSE FAILED\n{type(e).__name__} - {e}\nRAW OUTPUT: {output!r}")
        data = {}

    return data



# project fun
def project(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

Rules:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Return summary of each projects mentioned in the CV in project_details section.
- Must Return technical or related keywords mentioned in the CV in keywords section.


JSON STRUCTURE:
{{
  "projects": [
    {{
      "project_name": "",
      "project_details": "",
      "keywords": []
    }}
  ]
}}

TEXT:
{text}
"""
    data = {}
    output = ""
    for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model = "openai/gpt-oss-120b",
                    messages = [{
                        "role":"user",
                        "content" : prompt
                    }],
                    temperature=0.0,
                    max_tokens = 2000,
                    response_format={"type": "json_object"}
                )
            
            except Exception as e:
                logger.exception(f"PROJECT FUNCTION API CALL FAILED\n{type(e).__name__} - {e}")
                continue

            choice = response.choices[0]
            finish_reason = getattr(choice, "finish_reason", None)
            output = (choice.message.content or "").strip()

            logger.info(f"project() attempt {attempt+1} | finish_reason={finish_reason} | output_len={len(output)}")

            if finish_reason == "content_filter":
                logger.warning("project(): response blocked by content_filter, retrying...")
                continue

            if output:
                break 

            if not output:
                logger.error("PROJECT FUNCTION FAILED: empty output after retries")
                return data

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output.strip())
    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.exception(f"PROJECT FUNCTION JSON PARSE FAILED\n{type(e).__name__} - {e}\nRAW OUTPUT: {output!r}")
        data = {}

    return data