# Library
import ollama
import time
import re
import json
import spacy
import logging
logger = logging.getLogger(__name__)


# Regex Function
# Email extraction
def emails(text):
    try:
        email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    except Exception as e:
        logger.exception(f"{type(e).__name__} \nERROR - {e}")
        text = ""
    return re.findall(email,text)

# Email Masked
def emails_masked(text):
    try:
        email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    except Exception as e:
        logger.exception(f"{type(e).__name__} \nERROR - {e}")
        text = ""
    return re.sub(email,"[MASKED]",text)

# Phone number extraction
def ph_num(text):
    try:
        phone = r'(?:\+?94|0)?\s*\d[\d\s\-]{7,}\d'
    except Exception as e:
        logger.exception(f"{type(e).__name__} \nERROR - {e}")
        text = ""
    return re.findall(phone,text)

# Phone number Masked
def ph_num_masked(text):
    try:
        phone = r'(?:\+?94|0)?\s*\d[\d\s\-]{7,}\d'
    except Exception as e:
        logger.exception(f"{type(e).__name__} \nERROR - {e}")
        text = ""
    return re.sub(phone,"[MASKED]",text)


# name extraction : ollama fn
def all(text):
    system_prompt = "You are a CV data extraction assistant. Extract information from CV text." \
    "No explanations, no markdown, no extra text."
    user_prompt = f"""Extract the candidate_name and candidate_location from this CV text.

Rules for candidate_name:
- Most of cases, candidate_name may be there in 1
- The name may appear in ALL CAPS (e.g., JOHN DAVID SMITH)
- Or in Title Case (e.g., John David Smith)
- Ignore emails, phone numbers, locations, skills, and job titles
- Return ONLY the person's full name in one line
- Do NOT guess or invent a name

Rules for candidate_location:
- Current city, country, or address where the candidate lives or is based
- OR the location mentioned under contact details or header section of CV

OUTPUT JSON FILE:
{{
  "candidate_name": "",
  "candidate_location": ""
}}

CV TEXT:
{text}"""
    for attemp in range(3):
        try:        
            response = ollama.chat(
                model="qwen2.5:3b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},  
                ],
                options={
                    "temperature": 0,
                    "num_predict":50
                }
            )
            output = response["message"]["content"].strip()
            data = json.loads(output) if output else {"name":"NO","loc":"No"}
            if len(list(data.values())[0]) > 4 and len(list(data.values())[1]) > 4:
                dataset = data
                break
            else:
                continue
        except Exception as e:
            status_code = getattr(e,"status_code",None)
            logger.exception(f"STATUS CODE :{status_code} \n{type(e).__name__} \nError - {e}")
            dataset = {}
            time.sleep(2)
            continue

    return dataset

# load nlp library
nlp = spacy.load("en_core_web_sm")

# Name  Masked (spacy)
def person(text):
    doc = nlp(text)
    entities = [ent for ent in doc.ents if ent.label_ == "PERSON"]
    for ent in sorted(entities, key=lambda x: x.start_char, reverse=True):
        text = text[:ent.start_char] + "[MASKED]" + text[ent.end_char:]

    return text
