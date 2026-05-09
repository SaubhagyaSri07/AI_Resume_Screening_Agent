from app.agents.jd_agent import (
    JDAgent
)

from app.agents.profile_agent import (
    ProfileAgent
)

from app.agents.match_agent import (
    MatchAgent
)


# ---------------------------------------------------
# SAMPLE JD
# ---------------------------------------------------

sample_jd = """
We are looking for a Python AI Engineer
with experience in NLP, FastAPI,
LangChain, React, and Machine Learning.

Requirements:
- 2+ years experience
- Strong Python skills
- Experience with LLMs
- Familiarity with vector databases
- Good communication skills

Preferred:
- LangGraph
- RAG systems

Education:
Bachelor's degree in Computer Science.
"""


# ---------------------------------------------------
# PARSE JD
# ---------------------------------------------------

jd_profile = JDAgent.parse_jd(
    sample_jd
)


# ---------------------------------------------------
# PARSE RESUME
# ---------------------------------------------------

resume_data = ProfileAgent.parse_resume(
    "app/sample_resumes/sample_resume.pdf"
)

candidate_profile = (
    ProfileAgent.extract_candidate_profile(
        resume_data["raw_text"]
    )
)


# ---------------------------------------------------
# MATCH SKILLS
# ---------------------------------------------------

match_result = MatchAgent.match_skills(
    jd_profile["required_skills"],
    candidate_profile["skills"]
)


print(match_result)