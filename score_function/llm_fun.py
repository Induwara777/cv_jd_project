import json
import logging
import os
import time

from pydantic import BaseModel
from groq import (
    Groq,
    APIError,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    UnprocessableEntityError,
    BadRequestError,
    InternalServerError,
)


logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

MODEL_NAME = "openai/gpt-oss-120b"

try:
    os.environ["GROQ_API_KEY"] = "masked"
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
except Exception as e:
    logger.error(f"THERE IS A PROBLEM IN GROQ API KEY {type(e).__name__}")


# API Errors
class LLMFatalError(Exception):
    """Non-retryable failure — caller should stop the program."""
    pass


class LLMRetriesExhaustedError(Exception):
    """Retryable errors kept happening until retries ran out."""
    pass


# LLM function
def main_fun(prompt: str, jd_json: dict, cv_json: dict, validation_method: type[BaseModel], retries: int = 3) -> dict | None:
    prompt = prompt.format(
        jd_json=json.dumps(jd_json, indent=4),
        cv_json=json.dumps(cv_json, indent=4)
    )

    # Groq's JSON mode needs the schema described to the model explicitly.
    schema = validation_method.model_json_schema()
    system_instruction = (
        "You are a strict JSON generator. Respond ONLY with a single valid JSON "
        "object that conforms exactly to the following JSON schema. Do not include "
        "any explanation, markdown formatting, or code fences — output raw JSON only.\n\n"
        f"JSON schema:\n{json.dumps(schema, indent=2)}"
    )

    for attempt in range(retries):
        # _check_and_reserve_budget()
        # _pace_calls()
        print(attempt)

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                timeout=60,
            )

            raw_content = response.choices[0].message.content
            parsed = validation_method.model_validate_json(raw_content)
            print("LLM RESPOSNE IS SUCCESSFULLY PASSED")
            return parsed.model_dump()

        except RateLimitError as e:
            print("ERROR CODE: 429")
            msg = str(e)
            if "daily" in msg.lower() or "per_day" in msg.lower() or "quota" in msg.lower():
                logger.info("DAILY QUOTA EXHAUSTED (SERVER-CONFIRMED) — STOPPING BATCH")
                raise LLMFatalError("DAILY QUOTA EXHASTED") from e
            print("WAITNG 60 SECOND")
            logger.info(f"RATE LIMIT HIT (ATTEMPT {attempt+1}/{retries}).")
            time.sleep(60)
            continue

        except (AuthenticationError, PermissionDeniedError, NotFoundError, UnprocessableEntityError, BadRequestError) as e:
            logger.error("AUTHENTICATION/ PERMISSION ERROR")
            break

        except InternalServerError as e:
            logger.error(f"SERVER-SIDE ERROR (ATTEMPT {attempt + 1}/{retries})")
            time.sleep(60)
            continue

        except (APITimeoutError, APIConnectionError) as e:
            logger.error(f"REQUEST TIME OUT/ CONNECTION ERROR (ATTEMPT {attempt + 1}/{retries})")
            time.sleep(60)
            continue

        except APIStatusError as e:
            stat_code = getattr(e, "status_code", None)

            if stat_code in (401, 403, 404, 405, 422):
                logger.error("AUTHENTICATION/ PERMISSION ERROR")
                break

            elif stat_code in (500, 502, 503, 504):
                logger.error(f"SERVER-SIDE ERROR (ATTEMPT {attempt + 1}/{retries})")
                time.sleep(60)
                continue

            else:
                logger.error(f"UNHANDLED API ERROR: {type(e).__name__}")
                break

        except APIError as e:
            logger.error(f"UNHANDLED API ERROR: {type(e).__name__}")
            break

        except Exception as e:
            logging.error(f"ATTEMPT {attempt + 1} FAILED: {type(e).__name__}")
            break

    logger.error(f"ALL {retries} RETRIES FAILED FOR THIS REQUEST...")
    return None