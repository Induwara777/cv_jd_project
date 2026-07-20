from sqlalchemy import create_engine, text
import logging
logger = logging.getLogger(__name__)

DB_USER = "root"
DB_PASS = "masked"
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

def getting_details_from_db():
    query = text("""
                 SELECT Index_No, cv_files, full_score FROM scores
                 ORDER BY full_score DESC;
                 """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    leaderboard = []

    for rank, row in enumerate(rows, start=1):

        row = dict(row._mapping)

        leaderboard.append({
            "id": row["Index_No"],
            "rank": rank,
            "cv_file": row["cv_files"],
            "score": row["full_score"]
        })

    return leaderboard

def get_candidate_details(candidate_id):

    query = text("""
        SELECT
            Index_No,
            cv_files,
            Education_score,
            Technical_score,
            Soft_score,
            Experience_score,
            Impact_score,
            full_score,
            validation_status
        FROM scores
        WHERE Index_No = :id;
    """)

    with engine.connect() as conn:

        row = conn.execute(query, {"id": candidate_id}).first()

    if row is None:
        return None

    row = dict(row._mapping)

    return {
        "id": row["Index_No"],
        "cv_file": row["cv_files"],

        "scores": {
            "education": row["Education_score"],
            "technical": row["Technical_score"],
            "soft": row["Soft_score"],
            "experience": row["Experience_score"],
            "impact": row["Impact_score"],
            "full": row["full_score"]
        },

        "validation_status": row["validation_status"]
    }










































# def database(score_detail:list[dict]):
#     for score in score_detail:
#         try:
#             LoadToDB(score)
#         except Exception as e:
#             logger.exception(f"DB WRITE FAILED for {score.get('cv_file')}: \n{type(e).__name__} \nError - {e}")