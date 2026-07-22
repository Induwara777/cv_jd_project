import os
from sqlalchemy import create_engine, text
import logging
logger = logging.getLogger(__name__)

DB_USER = "root"
DB_PASS = "masked"
DB_HOST = "localhost"
DB_NAME = "cv_score"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}")
INT_FIELDS = ["Education_score", "Soft_score", "Technical_score", "Impact_score", "Experience_score"]

VALID_DECISIONS = {"pending", "accepted", "rejected"}

# --- One-time migration needed before this file works ---
# ALTER TABLE scores ADD COLUMN decision_status VARCHAR(20) NOT NULL DEFAULT 'pending';

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
    cleaned.setdefault("decision_status", "pending")
    return cleaned


def _name_from_cv_file(cv_file: str) -> str:
    """
    Display name = CV filename with extension stripped.
    Deliberately does NOT read from personal_data output — no real names,
    emails, or phone numbers are ever exposed to the leaderboard/detail API.
    """
    if not cv_file:
        return "Unknown"
    return os.path.splitext(cv_file)[0]


def LoadPersonalDetails(cv_files: str, name: str = "", phone: str = "", email: str = "", location: str = ""):
    """
    Upserts one candidate's personal details, keyed by the CV filename stem
    (extension stripped) so it lines up with scores.cv_files regardless of
    which pipeline stage produced each filename (raw upload vs extracted .json).
    """
    stem = _name_from_cv_file(cv_files)
    query = text("""
                 INSERT INTO personal_details (cv_files, name, phone, email, location)
                 VALUES (:cv_files, :name, :phone, :email, :location)
                 ON DUPLICATE KEY UPDATE
                     name = VALUES(name),
                     phone = VALUES(phone),
                     email = VALUES(email),
                     location = VALUES(location);
                 """)
    with engine.begin() as conn:
        conn.execute(query, {
            "cv_files": stem,
            "name": name or "",
            "phone": phone or "",
            "email": email or "",
            "location": location or "",
        })


def LoadToDB(score: dict):
    cleaned = _clean_score(score)
    query = text("""
                 INSERT INTO scores (cv_files,Education_score,Soft_score,Technical_score,Impact_score,Experience_score,validation_status,Total_experience,decision_status,summary_details)
                 VALUES (:cv_files,:Education_score,:Soft_score,:Technical_score,:Impact_score,:Experience_score,:validation_status,:Total_experience,:decision_status,:summary_details)
""")

    with engine.begin() as conn:
        conn.execute(query, cleaned)


def getting_details_from_db():
    # Added validation_status here (previously only selected on the detail
    # endpoint) so the frontend can compute pass/fail counts across the
    # whole leaderboard without an extra request per candidate.
    query = text("""
                 SELECT Index_No, cv_files, full_score, decision_status, validation_status,
                        Total_experience, Skill_percentage
                 FROM scores
                 ORDER BY full_score IS NULL, full_score DESC;
                 """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    # Bulk-fetch personal details once, keyed by filename stem, instead of
    # querying per row.
    personal_query = text("SELECT cv_files, name FROM personal_details;")
    with engine.connect() as conn:
        personal_rows = conn.execute(personal_query).fetchall()
    name_by_stem = {r.cv_files: r.name for r in personal_rows if r.name}

    leaderboard = []

    for rank, row in enumerate(rows, start=1):
        row = dict(row._mapping)
        stem = _name_from_cv_file(row["cv_files"])

        leaderboard.append({
            "id": str(row["Index_No"]),
            "rank": rank,
            "name": name_by_stem.get(stem) or stem,
            "score": row["full_score"],
            "status": row["decision_status"] or "pending",
            "validation_status": row["validation_status"] or "unknown",
            "experience": row["Total_experience"],
            "skill_match": row["Skill_percentage"],
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
            validation_status,
            decision_status,
            summary_details
        FROM scores
        WHERE Index_No = :id;
    """)

    with engine.connect() as conn:
        row = conn.execute(query, {"id": candidate_id}).first()

    if row is None:
        return None

    row = dict(row._mapping)
    stem = _name_from_cv_file(row["cv_files"])

    personal_query = text("""
                 SELECT name, phone, email, location FROM personal_details WHERE cv_files = :stem;
                 """)
    with engine.connect() as conn:
        personal_row = conn.execute(personal_query, {"stem": stem}).first()
    personal = dict(personal_row._mapping) if personal_row else {}

    return {
        "id": str(row["Index_No"]),
        "name": personal.get("name") or stem,
        "email": personal.get("email") or None,
        "phone": personal.get("phone") or None,
        "location": personal.get("location") or None,
        "score": row["full_score"],
        "status": row["decision_status"] or "pending",
        "summary": row["summary_details"],
        # Keys renamed here (Technical_score -> tech, Soft_score -> softSkills)
        # so they match CandidateScores in the frontend with no extra mapping layer.
        "scores": {
            "education": row["Education_score"],
            "tech": row["Technical_score"],
            "softSkills": row["Soft_score"],
            "experience": row["Experience_score"],
            "impact": row["Impact_score"],
        },
        "validation_status": row["validation_status"],
    }


def update_candidate_decision(candidate_id, decision: str) -> bool:
    """Set the reviewer's accept/reject decision. Returns True if a row was updated."""
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision '{decision}'. Must be one of {VALID_DECISIONS}")

    query = text("""
                 UPDATE scores
                 SET decision_status = :decision
                 WHERE Index_No = :id;
                 """)

    with engine.begin() as conn:
        result = conn.execute(query, {"decision": decision, "id": candidate_id})

    return result.rowcount > 0


# ========== NEW CLEANUP FUNCTIONS ==========

def clear_all_candidates():
    """Delete all scores (used when starting a new analysis session)."""
    query = text("DELETE FROM scores;")
    with engine.begin() as conn:
        conn.execute(query)
    logger.info("Cleared all candidate scores")


def clear_personal_details():
    """Delete all personal details (used when starting a new analysis session)."""
    query = text("DELETE FROM personal_details;")
    with engine.begin() as conn:
        conn.execute(query)
    logger.info("Cleared all personal details")


def reset_auto_increment():
    """Reset the Index_No auto-increment counter."""
    query = text("ALTER TABLE scores AUTO_INCREMENT = 1;")
    with engine.begin() as conn:
        conn.execute(query)
    logger.info("Reset auto-increment counter")


def clear_old_sessions():
    """Combined cleanup function."""
    clear_all_candidates()
    clear_personal_details()
    reset_auto_increment()