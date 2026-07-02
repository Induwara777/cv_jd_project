from openai import OpenAI
import json
import re
import os


os.environ['OPENAI_API_KEY'] = "W6geiBn0D35nP260rHbCWGdyb3FY9tblZ4PnXIjCx2ceAfBrYVga"
client = OpenAI(
    base_url="https://api.groq.com/openai/v1"
)

# 1. Score : Education prompt
system_prompt = """You are an expert technical recruiter AI. You evaluate how appropriate a candidate's degree is for a job posting, by strictly 
following the decision rules given."""

user_prompt = """Job Title:{job_title}
Job Post Required Degree:{job_post_requirement}
Candidate's Degree (from CV):{cv_qualification}

Decision Rules (follow in this exact order, stop at first match):
STEP 1 - Exact/Equivalent Match Check:
Is the candidate's degree the same field, or an approximately equivalent field, as the job post's required degree (at the same degree level)?
-> If YES: final_score = 90

STEP 2 - Overqualification Check (only if Step 1 is NO):
Does the candidate hold a HIGHER degree level (e.g., Master's when Bachelor's is required) in the SAME or a CLOSELY RELATED field to the job post requirement?
-> If YES: final_score = 95

STEP 3 - Relevance Search (only if Steps 1 and 2 are NO):
The candidate's degree does not match the job post's required degree directly.Using the Job Title and the candidate's actual degree field, assess how 
appropriate this degree background typically is for someone working in this job title/role. Consider real-world hiring norms for this role.

Then classify into exactly one of these three outcomes:
  a) HIGH relevance to the job title -> final_score = 80
  b) LOW/SOME relevance to the job title -> final_score = 70 
  c) NOT relevant at all to the job title -> final_score = 50

### Output Format (strict JSON only, no extra text):
{{
  "final_score": <int: 90, 95, 80, 70, or 50>
}}"""

# 1. Score : Education
def score_cv_education(job_title, job_post_requirement, cv_qualification, client, model="llama-3.3-70b-versatile"):

    prompt = system_prompt + "\n\n" + user_prompt.format(
        job_title=job_title,
        job_post_requirement=job_post_requirement,
        cv_qualification=cv_qualification
    )

    messages = [{
        "role": "user",
        "content": prompt
    }]

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=messages
    )

    raw_output = response.choices[0].message.content

    # Defensive parsing in case Llama wraps JSON in markdown fences
    cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_output.strip())

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        result = {"final_score": None, "raw_output": raw_output}

    return result

# Example usage
if __name__ == "__main__":
    result = score_cv_education(
        job_title="Machine Learning Engineer",
        job_post_requirement="Bachelor's degree in Computer Science or Bachelor's degree in Data Science",
        cv_qualification="Bachelor of Science in Envirnment science",
        client=client
    )

    print(result)


