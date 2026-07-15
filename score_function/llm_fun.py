import json
from pydantic import BaseModel
import logging
import time
import random
import os
from google import genai
from google.genai import types,errors
import threading



logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

try:
    os.environ["GEMINI_API_KEY"] = "masked"
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    logger.error(f"THERE IS A PROBLEM IN GEMINI FLASH API KEY {type(e).__name__}")

# API Errors
class LLMFatalError(Exception):
    """Non-retryable failure — caller should stop the program."""
    pass

class LLMRetriesExhaustedError(Exception):
        """Retryable errors kept happening until retries ran out."""
        pass

# DAILY_REQUEST_BUDGET = 150
# MIN_SECOND_BETWEEN_CALLS = 10
# _lock = threading.Lock()
# _request_count = 0
# _budget_date = time.strftime("%Y-%m-%d", time.gmtime())
# _last_call_ts = 0.0


# def _reset_budget_if_new_day():
#     global _request_count, _budget_date
#     today = time.strftime("%Y-%m-%d", time.gmtime())
#     if today != _budget_date:
#         logger.info(f"NEW DAY DETECTED ({today}) — RESETTING REQUEST BUDGET COUNTER")
#         _request_count = 0
#         _budget_date = today
 
 
# def _check_and_reserve_budget():
#     """Raise LLMFatalError BEFORE making a call if we're out of daily budget."""
#     global _request_count
#     with _lock:
#         _reset_budget_if_new_day()
#         if _request_count >= DAILY_REQUEST_BUDGET:
#             raise LLMFatalError(
#                 f"DAILY REQUEST BUDGET ({DAILY_REQUEST_BUDGET}) REACHED — "
#                 f"STOPPING BEFORE CALLING API TO AVOID A HARD QUOTA ERROR"
#             )
#         _request_count += 1
#         if _request_count % 10 == 0:
#             logger.info(f"REQUEST BUDGET USED: {_request_count}/{DAILY_REQUEST_BUDGET} TODAY")
 
 
# def _pace_calls():
#     """Enforce a minimum gap between successive API calls (crude RPM limiter)."""
#     global _last_call_ts
#     with _lock:
#         now = time.monotonic()
#         wait = MIN_SECOND_BETWEEN_CALLS - (now - _last_call_ts)
#         if wait > 0:
#             _last_call_ts = now + wait
#         else:
#             _last_call_ts = now
#     if wait > 0:
#         time.sleep(wait)
 
 

# LLM function
def main_fun(prompt:str,jd_json: dict, cv_json: dict, validation_method: type[BaseModel],retries: int = 2 )-> dict | None:
    prompt = prompt.format(
        jd_json=json.dumps(jd_json, indent=4),
        cv_json=json.dumps(cv_json, indent=4)
    )

    for attempt in range(retries):
        # _check_and_reserve_budget()
        # _pace_calls()
        print(attempt)

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema= validation_method,
                    http_options=types.HttpOptions(timeout=60_000),
                ),
            )
            parsed = response.parsed
            print("llm reponse are done")
            return parsed.model_dump()
            
        

        except errors.APIError as e:
            print("ERROR API")
            stat_code = getattr(e,"code",None)

            if stat_code == 429:
                print("ERROR 429")
                msg = str(e)
                if "PerDay" in msg or "generate_content_free_tier_requests" in msg:
                    logger.info(f"DAILY QUOTA EXHAUSTED (SERVER-CONFIRMED) — STOPPING BATCH")                  
                    raise LLMFatalError("DAILY QUOTA EXHASTED") from e
                print("60 secodn waiting adn continoue")
                wait = time.sleep(60)
                logger.info(f"RATE LIMIT HIT (ATTEMPT {attempt+1}/{retries}). WAITING {wait:.1f}s: {e}")
                time.sleep(wait)
                continue
            
            elif stat_code in (401,403,404,405,422):
                logger.error(f"AUTHENTICATION/ PERMISSION ERROR")
                break
            
            elif stat_code in (500,502,503,504):
                logger.error(f"SERVER-SIDE ERROR (ATTEMPT {attempt + 1}/{retries})")
                time.sleep(60)
                continue 


            else:
                logger.error(f"UNHANDLED API ERROR: {type(e).__name__}")
                break               
        
        except TimeoutError as e:
            logger.error(f"REQUEST TIME OUT( ATTEMPT {attempt + 1}/{retries})")
            time.sleep(60)
            continue

        except Exception as e:
            logging.error(f"ATTEMPT {attempt + 1} FAILED: {type(e).__name__}")
            break
    logger.error(f"ALL {retries} RETRIES FAILED FOR THIS REQUEST...")
    return None