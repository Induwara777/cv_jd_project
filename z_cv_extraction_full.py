import json
from openai import OpenAI
import requests
import os
from ocr.z_ocr_fun import extraction

# LLM API KEY
os.environ['OPENAI_API_KEY'] = "masked"
client = OpenAI(
    base_url="https://api.groq.com/openai/v1"
)


# Full fucntion
def final_CV_details(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

Rules for extracting skills:
- Return all technical and soft skills in the CV in profile_summary and soft_skills section.

Rules for education:
- Extract O/L, A/L, degree, and certificate information if available.
- Set "highest_qualification" to the highest completed qualification (ol, al,degree).

Rules for experiences:
- Calculate duration_months for each job.
- total_experience_years = (Adding all duration_months/ 12 )

Rules for project:
- Return summary of each projects mentioned in the CV in project_details section.
- Must Return technical or related keywords mentioned in the CV in keywords section.

Common rules for every section:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Use null for missing values.

JSON STRUCTURE:
{{
  "technical_skills": [],
  "soft_skills": [],

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
  }},

  "experience": {{
    "total_experience_years": null,
    "jobs": [
      {{
        "job_title": "",
        "duration_month": ""
      }}
    ]
  }},

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
        model = "llama-3.3-70b-versatile",
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
    except json.JSONDecodeError:
        print("JSON Error!!!")
        data = {}

    return data

if __name__ == "__main__":
    data = extraction("Associate Data Scientist Induwara Dilshan.pdf")
    datafile = final_CV_details(data)
    with open("one_cv_extraction.json","w", encoding = "utf-8") as f:
        json.dump(datafile,f,indent= 4)