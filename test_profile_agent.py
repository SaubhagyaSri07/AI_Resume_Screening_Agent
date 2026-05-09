from app.agents.profile_agent import (
    ProfileAgent
)

resume_data = ProfileAgent.parse_resume(
    "app/sample_resumes/sample_resume.pdf"
)

profile = ProfileAgent.extract_candidate_profile(
    resume_data["raw_text"]
)

print(profile)