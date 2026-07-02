import os
import json
from openai import OpenAI
import requests

# LLM API KEY
os.environ['OPENAI_API_KEY'] = "MASKED"
client = OpenAI(
    base_url="https://api.groq.com/openai/v1"
)

# Profile fun
def profile(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

Rules:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Return summary of profile in the CV in profile_summary section.


JSON STRUCTURE:
{{
  "candidate_name": "",
  "candidate_contact": {{
    "email": "",
    "phone": "",
    "location": ""
  }},

  "profile_summary": ""
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
        max_tokens = 800,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()

    try:
        data =  json.loads(output)
    except json.JSONDecodeError:
        print("JSON Error!!!")
        data = {}

    return data



# education fun
def education(text):
    prompt = f"""You are an expert HR information extraction system.

Extract structured information from the CV text.

Rules:
- Return ONLY valid JSON.
- Do not add or remove fields.
- Use null for missing values.
- Extract O/L, A/L, degree, and certificate information if available.
- Set "highest_qualification" to the highest completed qualification (ol, al, diploma, hnd, degree, masters, phd).


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
        model = "llama-3.3-70b-versatile",
        messages = [{
            "role":"user",
            "content" : prompt
        }],
        temperature=0.0,
        max_tokens = 200,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()

    try:
        data =  json.loads(output)
    except json.JSONDecodeError:
        print("JSON Error!!!")
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
        model = "llama-3.3-70b-versatile",
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
    except json.JSONDecodeError:
        print("JSON Error!!!")
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
        model = "llama-3.3-70b-versatile",
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
    except json.JSONDecodeError:
        print("JSON Error!!!")
        data = {}

    return data

# Final set 
def collection(text_data):
    main_file = {}
    # main_file.update(profile(text_data))
    main_file.update(education(text_data))
    main_file.update(skills(text_data))
    main_file.update(project(text_data))
    main_file.update(experience(text_data))

    with open("Induwara.json","w",encoding="utf-8") as f:
        json.dump(main_file,f,indent=4)

    return main_file

