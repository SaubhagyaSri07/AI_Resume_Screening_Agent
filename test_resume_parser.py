from app.agents.profile_agent import ResumeParser

resume_data = ResumeParser.parse_resume(
    "app/sample_resumes/sample_resume.pdf"
)

print("\nFILE NAME:\n")
print(resume_data["file_name"])

print("\nRESUME TEXT:\n")
print(resume_data["raw_text"][:3000])