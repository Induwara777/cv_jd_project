from sqlalchemy import create_engine, text
import logging
logger = logging.getLogger(__name__)

DB_USER = "root"
DB_PASS = "MASKED"     
DB_HOST = "localhost"
DB_NAME = "cv_score"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}")

def LoadToDB(score:dict):
    query = text("""
                 INSERT INTO scores (cv_files,Education_score,Soft_score,Technical_score,Impact_score,Experience_score)
                 VALUES (:cv_files,:Education_score,:Soft_score,:Technical_score,:Impact_score,:Experience_score)                
""")
    
    with engine.begin() as conn:
        conn.execute(query,score)

def database(score_detail:list[dict]):
    for score in score_detail:
        try:
            LoadToDB(score)
        except Exception as e:
            logger.exception(f"DB WRITE FAILED for {score.get('cv_file')}: \n{type(e).__name__} \nError - {e}")