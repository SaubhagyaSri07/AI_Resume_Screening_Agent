import pdfplumber
from docx import Document

import os
import json
import re

from typing import List

from pydantic import BaseModel, ValidationError

from langchain_core.prompts import PromptTemplate

from app.agents.utils import (
    generate_response,
    FLASH_MODEL
)


# =========================================================
# PYDANTIC SCHEMAS
# =========================================================

class Project(BaseModel):
    title: str
    description: List[str]


class Education(BaseModel):
    degree: str
    institution: str
    year: str
    details: str


class Certification(BaseModel):
    name: str
    issuer: str
    date: str


class CandidateProfile(BaseModel):

    candidate_name: str

    skills: List[str]

    projects: List[Project]

    experience: List[str]

    education: List[Education]

    certifications: List[Certification]

    tools_frameworks: List[str]

    summary: str


# =========================================================
# PROFILE AGENT
# =========================================================

class ProfileAgent:

    # -----------------------------------------------------
    # PDF PARSER
    # -----------------------------------------------------

    @staticmethod
    def extract_pdf_text(file_path):

        text = ""

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text.strip()

    # -----------------------------------------------------
    # DOCX PARSER
    # -----------------------------------------------------

    @staticmethod
    def extract_docx_text(file_path):

        doc = Document(file_path)

        text = "\n".join(
            para.text for para in doc.paragraphs
        )

        return text.strip()

    # -----------------------------------------------------
    # TEXT CLEANING
    # -----------------------------------------------------

    @staticmethod
    def clean_text(text):

        text = text.replace("\t", " ")

        text = re.sub(r"\n+", "\n", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # -----------------------------------------------------
    # RESUME INGESTION
    # -----------------------------------------------------

    @classmethod
    def parse_resume(cls, file_path):

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension == ".pdf":

            raw_text = cls.extract_pdf_text(
                file_path
            )

        elif extension == ".docx":

            raw_text = cls.extract_docx_text(
                file_path
            )

        else:
            raise ValueError(
                "Unsupported file format. Use PDF or DOCX."
            )

        cleaned_text = cls.clean_text(
            raw_text
        )

        return {
            "file_name": os.path.basename(file_path),
            "raw_text": cleaned_text
        }

    # -----------------------------------------------------
    # PROMPT BUILDER
    # -----------------------------------------------------

    @staticmethod
    def build_prompt(resume_text):

        template = """
You are an expert AI recruitment agent.

Extract structured candidate information
from the following resume text.

IMPORTANT RULES:
- Return ONLY valid JSON
- Do not include markdown
- Do not include explanations
- Do not hallucinate missing data
- Use empty arrays if information is unavailable

Resume:
{resume_text}

Required JSON format:
{{
    "candidate_name": "",

    "skills": [],

    "projects": [
        {{
            "title": "",
            "description": []
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
            input_variables=["resume_text"],
            template=template
        )

        return prompt.format(
            resume_text=resume_text
        )

    # -----------------------------------------------------
    # JSON CLEANER
    # -----------------------------------------------------

    @staticmethod
    def clean_json_response(response_text):

        cleaned = response_text.strip()

        if cleaned.startswith("```json"):

            cleaned = cleaned.replace(
                "```json",
                ""
            )

            cleaned = cleaned.replace(
                "```",
                ""
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

        cleaned_response = cls.clean_json_response(
            response
        )

        try:

            parsed_json = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Invalid JSON returned by model:\n{e}"
            )

        try:

            validated_output = CandidateProfile(
                **parsed_json
            )

        except ValidationError as e:

            raise ValueError(
                f"Pydantic validation failed:\n{e}"
            )

        return validated_output.model_dump()