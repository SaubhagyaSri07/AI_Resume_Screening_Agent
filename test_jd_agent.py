from app.agents.jd_agent import JDAgent

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

result = JDAgent.parse_jd(
    sample_jd
)

print(result)