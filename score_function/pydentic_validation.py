from pydantic import BaseModel

class fullScore(BaseModel):
    education_score: int
    soft_skill_score: int

class ExpScore(BaseModel):
    experience_score: int

class skillScore(BaseModel):
    technical_score: int
    impact_score :int
