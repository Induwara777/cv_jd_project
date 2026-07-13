import json
from pydantic import BaseModel
import logging
import time
import random
import os
from google import genai
from google.genai import types,errors

logger = logging.getLogger(__name__)

try:
    os.environ["GEMINI_API_KEY"] = "masked"
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    logger.exception(f"THERE IS A PROBLEM IN GEMINI FLASH API KEY {type(e).__name__} - {e}")

# API Errors
class LLMFatalError(Exception):
    """Non-retryable failure — caller should stop the program."""
    pass

class LLMRetriesExhaustedError(Exception):
        """Retryable errors kept happening until retries ran out."""
        pass

# LLM function
def main_fun(prompt:str,jd_json: dict, cv_json: dict, validation_method: type[BaseModel],retries: int = 5 )-> dict:
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

        except errors.APIError as e:
            stat_code = getattr(e,"code",None)

            if stat_code == 429:
                logger.error(f"API free limit/quota exhausted. Stopping program.: {e}")
                raise LLMFatalError(f"Quota exhausted: {e}") from e
            
            elif stat_code in (401,403,404,405,422):
                logger.error(f"Authentication/permission error: {e}")
                raise LLMFatalError(f"Non-retryable API error ({stat_code}): {e}") from e
            
            elif stat_code in (500,502,503,504):
                logger.warning(f"Server-side error (attempt {attempt}/{retries}): {e}")
                time.sleep(random.randint(10,15))
                continue 

            else:
                logger.exception(f"Unhandled API error: {type(e).__name__} - {e}")
                raise LLMFatalError(f"Unhandled API error: {e}") from e                
        
        except TimeoutError as e:
            logger.warning(f"Request timed out (attempt {attempt}/{retries}): {e}")
            time.sleep(random.randint(10,15))
            continue

        except LLMFatalError:
            raise

        except Exception as e:
            logging.exception(f"Attempt {attempt + 1} failed: {type(e).__name__} - {e}")
            raise LLMFatalError(f"Unexpected error: {type(e).__name__} - {e}") from e
    
    return {"ERROR":"ALL RETRIES WERE FAILED"}