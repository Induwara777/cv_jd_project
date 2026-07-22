from pydantic import BaseModel

class FULLSCORE(BaseModel):
    education_score: int
    soft_skill_score: int
    experience_score: int
    technical_score: int
    impact_score :int
    Total_experience: str
    summary_details: str



