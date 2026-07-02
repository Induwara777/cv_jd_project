# Library
import ollama
import re
from z_ocr_fun import extraction
import json
import spacy


# Regex Function
# Email extraction
def emails(text):
    email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return re.findall(email,text)

# Email Masked
def emails_masked(text):
    email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return re.sub(email,"[MASKED]",text)

# Phone number extraction
def ph_num(text):
    phone = r'(?:\+?94|0)?\s*\d[\d\s\-]{7,}\d'
    return re.findall(phone,text)

# Phone number Masked
def ph_num_masked(text):
    phone = r'(?:\+?94|0)?\s*\d[\d\s\-]{7,}\d'
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

    try:
        data = json.loads(output)

    except:
        print("Error")

    return data

#name extrcation
def all_fn(x):
    text = re.sub('\n'," ",extraction(f"{x}").strip()[:1000])
    name = all(text)
    return name


# Final personal dataset
def preprocess(y):
    text = extraction(f"{y}")[:1000].strip()
    name = all_fn(f"{y}")

    data = {
        "name":list(name.values())[0],
        "phone": ph_num(text)[0],
        "email":emails(text)[0],
        "location":list(name.values())[1]
    }
    return data

#load nlp library
nlp = spacy.load("en_core_web_sm")

# Name  Masked (spacy)
def person(text):
    doc = nlp(text)
    entities = [ent for ent in doc.ents if ent.label_ == "PERSON"]
    for ent in sorted(entities, key=lambda x: x.start_char, reverse=True):
        text = text[:ent.start_char] + "[MASKED]" + text[ent.end_char:]

    return text

# Final llm text output
def llm_text(text,y):
    pattern = "|".join(map(re.escape, list(preprocess(y).values())))
    masked = re.sub(pattern, "[MASKED]", text)
    masked1 = emails_masked(masked)
    masked2 = ph_num_masked(masked1)
    masked3 = person(masked2)
    return masked3

# Run script
if __name__ == "__main__":
    text_data = extraction("y_Associate Data Scientist Induwara Dilshan.pdf")
    final_data = llm_text(text=text_data,y="y_Associate Data Scientist Induwara Dilshan.pdf")
    # personal_data = preprocess("y_Associate Data Scientist Induwara Dilshan.pdf")
    print(final_data.strip())
    # print(personal_data)