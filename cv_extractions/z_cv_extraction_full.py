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
- Total response must stay under 2000 output tokens. If a CV has more projects/skills/jobs than the caps above allow, keep only the most relevant and drop the rest — do not summarize everything into a shorter form that still lists all items.

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
    for attempt in range(4): 
      try: 
        response = client.chat.completions.create(
            model = "openai/gpt-oss-120b",
            messages = [{
                "role":"user",
                "content" : prompt
            }],
            temperature=0.0,
            max_tokens = 3000,
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

      logger.info(f"OUTPUT_TOKEN = {completion_tokens}")

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