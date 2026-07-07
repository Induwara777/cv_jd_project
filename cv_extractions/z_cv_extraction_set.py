import os
import json
from openai import OpenAI
import requests
import logging
import time
import random

logger = logging.getLogger(__name__)

# LLM API KEY
try:
    os.environ['OPENAI_API_KEY'] = "masked"
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1"
    )
except Exception as e:
    logger.exception(f"THERE IS A PROBLEM IN LLAMA 70B API KEY {type(e).__name__} - {e}")


# education fun
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
      ],
      "z_score": null
    }},

    "degrees": [
      {{
        "degree_name": "",
        "university": "",
        "gpa": null
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
    response = client.chat.completions.create(
        model = "meta-llama/llama-3.3-70b-instruct",
        messages = [{
            "role":"user",
            "content" : prompt
        }],
        temperature=0.0,
        max_tokens = 1000,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()

    try:
        data =  json.loads(output)
    except Exception as e:
        logger.exception(f"EDUCAION FUNCTION IS FAILED \n{type(e).__name__} - {e}")
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
    response = client.chat.completions.create(
        model = "meta-llama/llama-3.3-70b-instruct",
        messages = [{
            "role":"user",
            "content" : prompt
        }],
        temperature=0.0,
        max_tokens = 1000,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()

    try:
        data =  json.loads(output)
    except Exception as e:
        logger.exception(f"SKILLS FUNCTION IS FAILED \n{type(e).__name__} - {e}")
        data = {}

    return data



# experience fun
def experience(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

RULES:
- Return ONLY valid JSON
- Calculate duration_months for each job: (end_year*12 + end_month) - (start_year*12 + start_month)
- If end_date="Present", use June 15, 2026 as end_date
- total_experience_years = sum(all duration_months) / 12, round to 1 decimal

JSON STRUCTURE:
{{
  "experience": [
    {{
    "total_experience_years": null,
    "jobs": [
      {{
        "job_title": "",
        "company": "",
        "Duration: null
      }}
    ]
    }}
]
}}

TEXT:
{text}
"""
    response = client.chat.completions.create(
        model = "meta-llama/llama-3.3-70b-instruct",
        messages = [{
            "role":"user",
            "content" : prompt
        }],
        temperature=0.0,
        max_tokens = 1500,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()
    
    try:
        data =  json.loads(output)
    except Exception as e:
        logger.exception(f"EXPERIENCE FUNCTION IS FAILED \n{type(e).__name__} - {e}")
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
    response = client.chat.completions.create(
        model = "meta-llama/llama-3.3-70b-instruct",
        messages = [{
            "role":"user",
            "content" : prompt
        }],
        temperature=0.0,
        max_tokens = 800,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()

    try:
        data =  json.loads(output)
    except Exception as e:
        logger.exception(f"PROJECT FUNCTION IS FAILED \n{type(e).__name__} - {e}")
        data = {}

    return data
    