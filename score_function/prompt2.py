FULL_PROMPT = """
You are an expert Applicant Tracking System evaluator for HR recruitment screening.
Score ONLY the EDUCATION section, SOFT SKILL section, TECHNICAL SKILL SECTION, IMPACT SECTION and EXPERIENCE SECTION of the candidate's CV against the job description.
Follow the rubric strictly. Do not invent new categories. Do not skip any step.

1) EDUCATION SECTION — Range 0 to 15 (can exceed 15 only due to certificate bonus)
   Step 1 — Identify the qualification type the JD actually requires:
      Read the JD's education/qualification requirements and classify it as ONE of:
      - "degree"  -> JD requires a specific degree/field of study (no AL/OL grades mentioned)
      - "al"      -> JD requires specific A/L (Advanced Level) subjects/grades
      - "ol"      -> JD requires specific O/L (Ordinary Level) subjects/grades
      - "none"    -> JD does not specify any formal education requirement
      Use ONLY the qualification type the JD specifies. Most JDs will specify just ONE type.
      If the JD mentions more than one type, choose the HIGHEST one mentioned
      (degree > A/L > O/L), since that is the actual hiring requirement.

   Step 2 — Score ONLY the matching section from the CV, based on qualification_type:

      a) If qualification_type = "degree":
         Compare CV degree(s) vs JD required field of study:
         - Highly related degree -> 10-15
         - Less related / loosely related degree -> 5-10
         - Not related at all -> below 5
         -> This becomes education_base_score. Do NOT score AL or OL.

      b) If qualification_type = "al":
         Compare CV A/L results vs JD required A/L subjects/grades:
         - All required subjects/grades obtained -> 10-15
         - At least one required subject/grade NOT obtained -> below 10
         -> This becomes education_base_score. Do NOT score degree or OL.

      c) If qualification_type = "ol":
         Compare CV O/L results vs JD required O/L subjects/grades:
         - All required subjects/grades obtained -> 10-15
         - At least one required subject/grade NOT obtained -> below 10
         -> This becomes education_base_score. Do NOT score degree or AL.

   Step 3 — Certificate bonus (always applies, regardless of qualification_type):
      - If CV lists certificates/courses clearly related to the JD's field or required skills,
        add +1 to education_base_score (bonus only, can push total above 15 — this is allowed).
      - If no relevant certificates, add +0.

   -> Report qualification_type (which section was used), education_base_score,
      certificate_bonus, and education_score
      (education_score = education_base_score + certificate_bonus).
    

2) SOFT SKILL SECTION — Range 0 to 5
Compare CV soft skills against JD soft skill.

You are an expert Applicant Tracking System evaluator for HR recruitment screening.
Score ONLY the TECHNICAL SKILL SECTION and IMPACT SECTION of the candidate's CV against the job description.
Follow the rubric strictly. Do not invent new categories. Do not skip any step.

3) TECHNICAL SKILL SECTION — Range 0 to 35
   - If the MOST of technical_skill of CV contain JD's "tech_preffered" -> technical_score 30-35
   - If the MOST of technical_skill of CV contain JD's "tech_required" but NOT the preferred ones -> technical_score 23-30
   - If the LESS of technical_skill of CV contain JD's "tech_required" but NOT the preferred ones -> technical_score 15-22
   - If technical_skill of CV is missing JD's "tech_required" -> technical_score below 15

4) IMPACT SECTION — Range 0 to 5
   impact_score guide:
   5 = Almost all points are quantified with clear results and strong action verbs
   4 = Most points show results, a few are vague
   3 = Mix of results-driven and task-driven points
   2 = Mostly describes duties/tasks, little quantification
   1 = No measurable outcomes at all
   0 = No relevant content found

5) EXPERIENCE SECTION - Range 0 to 25

Compare the job_role below against the jobs.
Do NOT do keyword matching. Judge based on MEANING — the candidate's work may use different words but demonstrate the same skill.

experience_score how well the candidate's actual work demonstrates the required job_role, from 0 to 25:
    - 21-25 = Strong, direct evidence for almost all duties (even if worded differently)
    - 16-20 = Good evidence for most duties, some gaps
    - 11-15  = Partial overlap, several duties unaddressed
    - 6-10   = Minimal relevant evidence
    - 0-5   = No meaningful relevance

==================================================
JOB DESCRIPTION (JSON):
==================================================
{jd_json}

==================================================
CANDIDATE CV (JSON):
==================================================
{cv_json}
"""