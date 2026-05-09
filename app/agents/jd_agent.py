from pydantic import BaseModel
from typing import List
import json

from langchain_core.prompts import PromptTemplate

from app.agents.utils import (
    generate_response,
    FLASH_MODEL
)


class JDStructure(BaseModel):
    job_title: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_required: str
    education_required: str
    responsibilities: List[str]
    tools_frameworks: List[str]
    soft_skills: List[str]


class JDAgent:

    @staticmethod
    def build_prompt(jd_text):

        template = """
You are an expert HR AI agent.

Extract structured information from the following
Job Description.

Return ONLY valid JSON.

Job Description:
{jd_text}

Required JSON format:
{{
    "job_title": "",
    "required_skills": [],
    "preferred_skills": [],
    "experience_required": "",
    "education_required": "",
    "responsibilities": [],
    "tools_frameworks": [],
    "soft_skills": []
}}
"""

        prompt = PromptTemplate(
            input_variables=["jd_text"],
            template=template
        )

        return prompt.format(
            jd_text=jd_text
        )

    @classmethod
    def parse_jd(cls, jd_text):

        prompt = cls.build_prompt(jd_text)

        response = generate_response(
            prompt,
            model=FLASH_MODEL
        )

        cleaned_response = response.strip()

        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.replace(
                "```json", ""
            ).replace("```", "").strip()

        parsed_json = json.loads(cleaned_response)

        validated_output = JDStructure(
            **parsed_json
        )

        return validated_output.dict()