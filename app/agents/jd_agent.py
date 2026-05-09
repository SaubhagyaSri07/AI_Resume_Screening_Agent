from pydantic import (
    BaseModel,
    ValidationError
)

from typing import List

import json

from langchain_core.prompts import (
    PromptTemplate
)

from app.agents.utils import (
    generate_response,
    FLASH_MODEL
)


# =========================================================
# PYDANTIC SCHEMA
# =========================================================

class JDStructure(BaseModel):

    job_title: str = ""

    required_skills: List[str] = []

    preferred_skills: List[str] = []

    experience_required: str = ""

    education_required: str = ""

    responsibilities: List[str] = []

    tools_frameworks: List[str] = []

    soft_skills: List[str] = []


# =========================================================
# JD AGENT
# =========================================================

class JDAgent:

    # -----------------------------------------------------
    # BUILD PROMPT
    # -----------------------------------------------------

    @staticmethod
    def build_prompt(
        jd_text
    ):

        template = """
You are an expert HR AI recruitment agent.

Extract structured information from the following
Job Description.

IMPORTANT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations outside JSON
- Ensure proper double quotes
- Ensure valid JSON syntax

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

            input_variables=[
                "jd_text"
            ],

            template=template
        )

        return prompt.format(
            jd_text=jd_text
        )

    # -----------------------------------------------------
    # CLEAN JSON RESPONSE
    # -----------------------------------------------------

    @staticmethod
    def clean_json_response(
        response_text
    ):

        cleaned = response_text.strip()

        # ---------------------------------------------
        # REMOVE MARKDOWN WRAPPERS
        # ---------------------------------------------

        if cleaned.startswith(
            "```json"
        ):

            cleaned = (
                cleaned
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # ---------------------------------------------
        # EXTRACT JSON OBJECT
        # ---------------------------------------------

        start_index = cleaned.find("{")

        end_index = cleaned.rfind("}")

        if start_index != -1 and end_index != -1:

            cleaned = cleaned[
                start_index:end_index + 1
            ]

        # ---------------------------------------------
        # REMOVE TRAILING COMMAS
        # ---------------------------------------------

        cleaned = cleaned.replace(
            ",}",
            "}"
        )

        cleaned = cleaned.replace(
            ",]",
            "]"
        )

        return cleaned.strip()

    # -----------------------------------------------------
    # PARSE JD
    # -----------------------------------------------------

    @classmethod
    def parse_jd(
        cls,
        jd_text
    ):

        # ---------------------------------------------
        # BUILD PROMPT
        # ---------------------------------------------

        prompt = cls.build_prompt(
            jd_text
        )

        # ---------------------------------------------
        # GENERATE RESPONSE
        # ---------------------------------------------

        response = generate_response(

            prompt,

            model=FLASH_MODEL
        )

        # ---------------------------------------------
        # CLEAN RESPONSE
        # ---------------------------------------------

        cleaned_response = (
            cls.clean_json_response(
                response
            )
        )

        # ---------------------------------------------
        # PARSE JSON SAFELY
        # ---------------------------------------------

        try:

            parsed_json = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError as e:

            raise ValueError(

                "Invalid JSON returned "
                f"by JD Agent.\n\n"

                f"Cleaned Response:\n"
                f"{cleaned_response}\n\n"

                f"Error:\n{e}"
            )

        # ---------------------------------------------
        # VALIDATE STRUCTURE
        # ---------------------------------------------

        try:

            validated_output = (
                JDStructure(
                    **parsed_json
                )
            )

        except ValidationError as e:

            raise ValueError(

                "JD validation failed.\n\n"
                f"{e}"
            )

        return validated_output.model_dump()