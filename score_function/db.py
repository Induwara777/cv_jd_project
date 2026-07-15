from sqlalchemy import create_engine, text
import logging
logger = logging.getLogger(__name__)

DB_USER = "root"
  
DB_HOST = "localhost"
DB_NAME = "cv_score"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}")
INT_FIELDS = ["Education_score", "Soft_score", "Technical_score", "Impact_score", "Experience_score"]

def _clean_score(score: dict) -> dict:
    """Convert '' or missing values to None so INT columns get NULL, not 0 or an error."""
    cleaned = dict(score)
    for field in INT_FIELDS:
        val = cleaned.get(field)
        if val == "" or val is None:
            cleaned[field] = None
        else:
            try:
                cleaned[field] = int(val)
            except (ValueError, TypeError):
                logger.warning(f"NON-INT VALUE FOR {field} IN {cleaned.get('cv_files')}: {val!r} — SETTING NULL")
                cleaned[field] = None

    cleaned.setdefault("validation_status", "unknown")
    return cleaned

def LoadToDB(score:dict):
    cleaned = _clean_score(score)
    query = text("""
                 INSERT INTO scores (cv_files,Education_score,Soft_score,Technical_score,Impact_score,Experience_score,validation_status)
                 VALUES (:cv_files,:Education_score,:Soft_score,:Technical_score,:Impact_score,:Experience_score,:validation_status)                
""")
    
    with engine.begin() as conn:
        conn.execute(query,cleaned)

def database(score_detail:list[dict]):
    for score in score_detail:
        try:
            LoadToDB(score)
        except Exception as e:
            logger.exception(f"DB WRITE FAILED for {score.get('cv_file')}: \n{type(e).__name__} \nError - {e}")