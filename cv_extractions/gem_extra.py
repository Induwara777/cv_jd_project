import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import logging
import time
import re
from google import genai
from google.genai import types, errors

logger = logging.getLogger(__name__)

try:
    os.environ["GEMINI_API_KEY"] = "API KEY"
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    logger.error(f"THERE IS A PROBLEM IN GEMINI FLASH API KEY {type(e).__name__}")

def final_CV_details(text):
    prompt = f"""You are an expert HR information extraction system.

Extract skills, projects, experience, and education information from the CV text provided below. Follow every rule exactly.

CURRENT_DATE: Date of today
CV_TEXT: {text} 
=== SKILLS RULES ===
- Extract technical skills (tools, languages, frameworks, platforms) into "technical_skills". Deduplicate. Max 15 items, most relevant/prominent first.
- Extract soft skills into "soft_skills". Deduplicate. Max 8 items.
- Each skill is a short label only (1-4 words). No descriptions, no explanations.
- Do not invent skills that are not stated or clearly implied by the CV content.

=== PROJECT RULES ===
- Include at most the 5 most significant projects mentioned anywhere in the CV (including inside job/work-experience descriptions).
- "project_details" = ONE sentence, max 20 words, covering what the project was and the person's role.
- "keywords" = max 6 technical terms relevant to that specific project.
- If a project was built as part of a specific job, name the job title in ≤5 words inside "project_details" — do not restate full job description.

=== EXPERIENCE RULES ===
- Identify every job/work-experience entry in the CV, in the order they appear. Include only: title, dates, duration_month. Do not include job description text.
- If end_date is "Present"/"Current"/"Till date", use CURRENT_DATE as the end date.
- "duration_month" = whole number of months between start_date and end_date. Always a number, never a string.
- "total_experience_years" = number, one decimal place, summed duration_month / 12. Do not overlap-adjust unless CV explicitly indicates concurrent jobs.
- If no work experience is found, set "total_experience_years" to 0 and "jobs" to [].
- Never guess dates not stated or clearly inferable (e.g. "3 years at X" is inferable). If exact months are unavailable, estimate duration_month only from what's stated — no extra commentary.

=== EDUCATION RULES ===
- Extract O/L, A/L, degree(s), certificate(s) if present.
- "highest_qualification" = exactly one of: "ol", "al", "hnd", "diploma", "degree", "masters", "phd", or null.
- Do not include institution names anywhere in the output.
- If subject-level grades aren't listed individually, "subjects" = [] (not null).

=== GENERAL OUTPUT RULES ===
- Output ONLY the JSON object below — no markdown, no code fences, no explanations, no extra text before or after.
- Output compact JSON: no indentation, no line breaks, no extra whitespace between keys/values.
- Do not add or remove any fields from the structure.
- Use null for missing single values (strings/numbers/objects). Use [] for missing lists — never null for array fields.
- All numeric fields (duration_month, total_experience_years, year) must be numbers, not strings.


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
"""
    output = ""
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",  # confirm exact model name before deploying
                contents=prompt,
            )

        except errors.ClientError as e:
            if e.code == 429:
                wait = 60
                logger.exception(f"LLM: RATE LIMITED (429), BACKING OFF SECOND: {wait}")
                print(wait)
                time.sleep(wait)
                continue
            elif e.code == 400:
                logger.exception(f"LLM BAD REQUEST / INVALID JSON. CHECK MAX_OUTPUT_TOKENS.")
                break
            elif e.code == 401:
                logger.exception(f"LLM API KEY IS INVALID OR MISSING!")
                break
            elif e.code == 403:
                logger.exception(f"ACCESS TO LLM API DENIED!")
                break
            elif e.code == 404:
                logger.exception(f"LLM MODEL NAME IS WRONG!")
                break
            elif e.code == 413:
                logger.exception(f"PROMPT EXCEEDED SIZE LIMIT. REDUCE IT.")
                break
            else:
                logger.exception(f"LLM CLIENT ERROR")
                print("4")
                time.sleep(4)
                continue

        except errors.ServerError as e:
            logger.exception(f"LLM SERVER ERROR (5xx)")
            print("4")
            time.sleep(4)
            continue

        except Exception as e:
            logger.exception(f"LLM CALL FAILED UNEXPECTEDLY \n{type(e).__name__}")
            print("4")
            time.sleep(4)
            continue

        candidate = response.candidates[0] if response.candidates else None
        finish_reason = getattr(candidate, "finish_reason", None)
        completion_tokens = (
            response.usage_metadata.candidates_token_count
            if getattr(response, "usage_metadata", None) else None
        )
        output = (response.text or "").strip() if response.text else ""

        logger.info(f"OUTPUT_TOKEN = {completion_tokens}")

        if finish_reason == "SAFETY":
            logger.warning("LLM: response blocked by safety filter, retrying...")
            continue

        if finish_reason == "MAX_TOKENS":
            logger.warning("LLM: response truncated at MAX_TOKENS — consider raising max_output_tokens")

        if output:
            break

    if not output:
        logger.error("LLM FUNCTION FAILED: EMPTY OUTPUT AFTER ALL RETRIES...")
        return {}

    output_clean = output.strip().encode("ascii", "ignore").decode()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_clean)
    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.exception(f"JSON PARSE FAILED\n{type(e).__name__} - {e}\nRAW OUTPUT: {output!r}")
        data = {}
    return data