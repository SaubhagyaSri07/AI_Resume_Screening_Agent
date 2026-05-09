from app.agents.jd_agent import (
    JDAgent
)

from app.agents.profile_agent import (
    ProfileAgent
)

from app.agents.match_agent import (
    MatchAgent
)

from app.agents.score_agent import (
    ScoreAgent
)


# =====================================================
# SAMPLE JOB DESCRIPTION
# =====================================================

sample_jd = """
We are hiring a Python AI Engineer.

Requirements:
- Strong Python skills
- Experience with NLP
- Experience with Machine Learning
- Experience with LLMs
- Knowledge of vector databases
- FastAPI experience preferred
"""

# =====================================================
# PARSE JD
# =====================================================

jd_profile = JDAgent.parse_jd(
    sample_jd
)

# =====================================================
# PARSE RESUME
# =====================================================

resume_data = ProfileAgent.parse_resume(
    "app/sample_resumes/sample_resume.pdf"
)

candidate_profile = (
    ProfileAgent.extract_candidate_profile(
        resume_data["raw_text"]
    )
)

# =====================================================
# SEMANTIC MATCHING
# =====================================================

match_result = MatchAgent.match_skills(

    jd_profile["required_skills"],

    candidate_profile["skills"]
)

# =====================================================
# FINAL SCORING
# =====================================================

final_result = (
    ScoreAgent.evaluate_candidate(

        candidate_profile=
            candidate_profile,

        match_result=
            match_result,

        jd_profile=
            jd_profile
    )
)

# =====================================================
# OUTPUT
# =====================================================

print(final_result)