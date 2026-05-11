import pdfplumber
import json
import os
import re

from docx import Document

from typing import List

from pydantic import (
    BaseModel,
    ValidationError,
    Field
)

from langchain_core.prompts import (
    PromptTemplate
)

from app.agents.utils import (
    generate_response,
    FLASH_MODEL
)

from app.utils.linkedin_parser import (
    LinkedInParser
)

# =========================================================
# PYDANTIC SCHEMAS
# =========================================================

class Project(BaseModel):

    title: str = ""

    description: List[str] = Field(
        default_factory=list
    )

    technologies: List[str] = Field(
        default_factory=list
    )


class Education(BaseModel):

    degree: str = ""

    institution: str = ""

    year: str = ""

    details: str = ""


class Certification(BaseModel):

    name: str = ""

    issuer: str = ""

    date: str = ""


class CandidateProfile(BaseModel):

    candidate_name: str = ""

    skills: List[str] = Field(
        default_factory=list
    )

    projects: List[Project] = Field(
        default_factory=list
    )

    experience: List[str] = Field(
        default_factory=list
    )

    education: List[Education] = Field(
        default_factory=list
    )

    certifications: List[
        Certification
    ] = Field(
        default_factory=list
    )

    tools_frameworks: List[str] = Field(
        default_factory=list
    )

    summary: str = ""


# =========================================================
# PROFILE AGENT
# =========================================================

class ProfileAgent:

    # -----------------------------------------------------
    # PDF PARSER
    # -----------------------------------------------------

    @staticmethod
    def extract_pdf_text(
        file_path
    ):

        text = ""

        with pdfplumber.open(
            file_path
        ) as pdf:

            for page in pdf.pages:

                page_text = (
                    page.extract_text()
                )

                if page_text:

                    text += (
                        page_text + "\n"
                    )

        return text.strip()

    # -----------------------------------------------------
    # DOCX PARSER
    # -----------------------------------------------------

    @staticmethod
    def extract_docx_text(
        file_path
    ):

        doc = Document(file_path)

        text = "\n".join(

            para.text

            for para in doc.paragraphs
        )

        return text.strip()

    # -----------------------------------------------------
    # TEXT CLEANING
    # -----------------------------------------------------

    @staticmethod
    def clean_text(text):

        text = text.replace(
            "\t",
            " "
        )

        text = re.sub(
            r"\n+",
            "\n",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # -----------------------------------------------------
    # RESUME / LINKEDIN INGESTION
    # -----------------------------------------------------

    @classmethod
    def parse_resume(

        cls,

        file_path
    ):

        extension = os.path.splitext(
            file_path
        )[1].lower()

        # =================================================
        # PDF
        # =================================================

        if extension == ".pdf":

            raw_text = cls.extract_pdf_text(
                file_path
            )

            cleaned_text = cls.clean_text(
                raw_text
            )

            return {

                "file_name":
                    os.path.basename(
                        file_path
                    ),

                "raw_text":
                    cleaned_text
            }

        # =================================================
        # DOCX
        # =================================================

        elif extension == ".docx":

            raw_text = cls.extract_docx_text(
                file_path
            )

            cleaned_text = cls.clean_text(
                raw_text
            )

            return {

                "file_name":
                    os.path.basename(
                        file_path
                    ),

                "raw_text":
                    cleaned_text
            }

        # =================================================
        # LINKEDIN JSON
        # =================================================

        elif extension == ".json":

            linkedin_profile = (

                LinkedInParser
                .parse_linkedin_json(
                    file_path
                )
            )

            validated = CandidateProfile(
                **linkedin_profile
            )

            return {

                "file_name":
                    os.path.basename(
                        file_path
                    ),

                "linkedin_profile":
                    validated.model_dump()
            }

        # =================================================
        # INVALID FORMAT
        # =================================================

        else:

            raise ValueError(
                "Unsupported file format."
            )

    # -----------------------------------------------------
    # PROMPT BUILDER
    # -----------------------------------------------------

    @staticmethod
    def build_prompt(
        resume_text
    ):

        template = """
You are an expert AI recruitment agent.

Extract structured candidate information
from the following resume text.

IMPORTANT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- No hallucinations
- Use empty arrays if data missing
- Use double quotes
- No trailing commas
- Keep responses concise and structured

Resume:
{resume_text}

Required JSON format:
{{
    "candidate_name": "",

    "skills": [],

    "projects": [
        {{
            "title": "",
            "description": [],
            "technologies": []
        }}
    ],

    "experience": [],

    "education": [
        {{
            "degree": "",
            "institution": "",
            "year": "",
            "details": ""
        }}
    ],

    "certifications": [
        {{
            "name": "",
            "issuer": "",
            "date": ""
        }}
    ],

    "tools_frameworks": [],

    "summary": ""
}}
"""

        prompt = PromptTemplate(

            input_variables=[
                "resume_text"
            ],

            template=template
        )

        return prompt.format(
            resume_text=resume_text
        )

    # -----------------------------------------------------
    # JSON CLEANER
    # -----------------------------------------------------

    @staticmethod
    def clean_json_response(
        response_text
    ):

        cleaned = response_text.strip()

        # =================================================
        # REMOVE MARKDOWN
        # =================================================

        if cleaned.startswith(
            "```json"
        ):

            cleaned = (
                cleaned
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
            )

        cleaned = cleaned.strip()

        # =================================================
        # EXTRACT JSON OBJECT
        # =================================================

        start_index = cleaned.find("{")

        end_index = cleaned.rfind("}")

        if (
            start_index != -1
            and
            end_index != -1
        ):

            cleaned = cleaned[
                start_index:end_index + 1
            ]

        # =================================================
        # REMOVE TRAILING COMMAS
        # =================================================

        cleaned = re.sub(
            r",\s*}",
            "}",
            cleaned
        )

        cleaned = re.sub(
            r",\s*]",
            "]",
            cleaned
        )

        return cleaned.strip()

    # -----------------------------------------------------
    # PROFILE EXTRACTION
    # -----------------------------------------------------

    @classmethod
    def extract_candidate_profile(

        cls,

        resume_text
    ):

        prompt = cls.build_prompt(
            resume_text
        )

        response = generate_response(

            prompt,

            model=FLASH_MODEL
        )

        cleaned_response = (

            cls.clean_json_response(
                response
            )
        )

        # =================================================
        # JSON PARSING
        # =================================================

        try:

            parsed_json = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError as e:

            raise ValueError(

                f"Invalid JSON returned by model:\n{e}"
            )

        # =================================================
        # SAFETY DEFAULTS
        # =================================================

        parsed_json.setdefault(
            "candidate_name",
            ""
        )

        parsed_json.setdefault(
            "skills",
            []
        )

        parsed_json.setdefault(
            "projects",
            []
        )

        parsed_json.setdefault(
            "experience",
            []
        )

        parsed_json.setdefault(
            "education",
            []
        )

        parsed_json.setdefault(
            "certifications",
            []
        )

        parsed_json.setdefault(
            "tools_frameworks",
            []
        )

        parsed_json.setdefault(
            "summary",
            ""
        )

        # =================================================
        # PYDANTIC VALIDATION
        # =================================================

        try:

            validated_output = (
                CandidateProfile(
                    **parsed_json
                )
            )

        except ValidationError as e:

            raise ValueError(

                f"Pydantic validation failed:\n{e}"
            )

        return validated_output.model_dump()