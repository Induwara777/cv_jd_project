import json
from pydantic import BaseModel
import logging
import time
import random
import os
from google import genai
from google.genai import types 

logger = logging.getLogger(__name__)
os.environ["GEMINI_API_KEY"] = "MASKED"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def main_fun(prompt:str,jd_json: dict, cv_json: dict, validation_method: type[BaseModel],retries: int = 5 ):
    prompt = prompt.format(
        jd_json=json.dumps(jd_json, indent=4),
        cv_json=json.dumps(cv_json, indent=4)
    )

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema= validation_method,
                ),
            )
            parsed = response.parsed
            return parsed.model_dump()
        
        except Exception as e:
            logging.exception(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(random.randint(30,40))
    return {"ERROR":"ALL RETRIES WERE FAILED"}