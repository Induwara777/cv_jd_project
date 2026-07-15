import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from openai import OpenAI
import os
from ocr.z_ocr_fun import extraction
import logging
from groq import RateLimitError, BadRequestError
logger = logging.getLogger(__name__)
import time
import re


# LLM API KEY
os.environ['OPENAI_API_KEY'] = "masked"
client = OpenAI(
    base_url="https://api.groq.com/openai/v1"
)


# Full fucntion
def final_CV_details(text):
    prompt = f"""You are an expert HR information extraction system.

MSUT Extract skills, project, experiences, education  information from the CV text.

Rules for extracting skills:
- Return all technical and soft skills in the CV in profile_summary and soft_skills section.

Rules for project:
- Return summary of each projects mentioned in the CV in project_details section.
- Must Return technical or related keywords mentioned in the CV in keywords section.
- Add experience details to project section.

Rules for experiences:
CALCULATION RULES (follow exactly, do not explain your steps in the output):
- DO NOT GUESS for duration_year
- Read entire data.
- Find all related to experiences.
- using your intelligence, give experiences as month counts. IT IS MUST.
- For every job, MUST CALCULATE duration_month. IT IS ALSO MUST.
- Finaly, MUST CALCULATE total_experience_years.

Rules for education:
- Extract O/L, A/L, degree, and certificate information if available.
- Set "highest_qualification" to the highest completed qualification (ol, al, hnd, degree).
- No need education institution names.

Common rules for every section:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Use null for missing values.

JSON STRUCTURE:
{{
  "technical_skills": [],
  "soft_skills": [],
  "projects": [
    {{
      "project_name": "",
      "project_details": "",
      "keywords": []
    }}
  ],
  "experience": {{
    "total_experience_years": null,
    "jobs": [
      {{
        "job_title": "",
        "duration_month": ""
      }}
    ]
  }},
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
    for attempt in range(2): 
      try: 
        response = client.chat.completions.create(
            model = "openai/gpt-oss-120b",
            messages = [{
                "role":"user",
                "content" : prompt
            }],
            temperature=0.0,
            max_tokens = 2500,
            response_format={"type": "json_object"}
        )

      except RateLimitError as e:
          retry = e.response.headers.get("retry-after")
          logger.warning(f"LLM: RATE LIMITED, RETRY_AFTER={retry}")
          if retry:
              time.sleep(float(retry)+60)
              continue        
  
      except Exception as e:
          status_code = getattr(e,"status_code",None)
          if status_code == 400:
            logger.exception(f"LLM DON'T PROVIDE VALID JSON. PLEASE INCREASE MAX_TOKEN_SIZE !!!. \n{type(e).__name__} \nERROR- {e}")
            break
          elif status_code == 401:
             logger.exception(f"LLM API KEY IS INVALID OR MISSING API KEY! \n{type(e).__name__} \nERROR- {e}")
             break
          elif status_code == 403:
             logger.exception(f"ACESS OF LLM API KEY IS DENIED! \n{type(e).__name__} \nERROR- {e}")
             break
          elif status_code == 404:
             logger.exception(f"LLM API NAME IS WRONG! \n{type(e).__name__} \nERROR- {e}")
             break  
          elif status_code == 413:
             logger.exception(f"YOUR PROMPT EXCEEDED SIZE LIMIT. REDUCE IT. \n{type(e).__name__} \nERROR- {e}")
             break
          else:
            logger.exception(f"LLM FUNCTION API CALL FAILED\n{type(e).__name__} \nERROR- {e}")
            time.sleep(4)
            continue

      choice = response.choices[0]
      finish_reason = getattr(choice, "finish_reason", None)
      completion_tokens = response.usage.completion_tokens if response.usage else None
      output = (choice.message.content or "").strip()

      logger.info(f"OUTPUT_TOKEN={completion_tokens}")

      if finish_reason == "content_filter":
          logger.warning("FUNCTION: response blocked by content_filter, retrying...")
          continue

      if output:
          break 

    if not output:
        logger.error("LLM FUNCTION FAILED: EMPTY OUTPUT AFTER ALL RETRIES...")
        data = {}
        return data

    output_clean = output.strip().encode("ascii", "ignore").decode()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_clean)
    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.exception(f"PROJECT FUNCTION JSON PARSE FAILED\n{type(e).__name__} - {e}\nRAW OUTPUT: {output!r}")
        data ={}
    return data