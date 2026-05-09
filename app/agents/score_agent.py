from pydantic import (
    BaseModel,
    ValidationError
)

from typing import Dict

import json

from langchain_core.prompts import (
    PromptTemplate
)

from app.agents.utils import (
    generate_response,
    PRO_MODEL
)


# =========================================================
# PYDANTIC SCHEMAS
# =========================================================

class DimensionScore(BaseModel):

    score: float

    weight: int

    justification: str


class CandidateScore(BaseModel):

    candidate_name: str

    dimension_scores: Dict[
        str,
        DimensionScore
    ]

    weighted_total_score: float

    recommendation: str

    final_summary: str


# =========================================================
# SCORE AGENT
# =========================================================

class ScoreAgent:

    # -----------------------------------------------------
    # CLEAN JSON RESPONSE
    # -----------------------------------------------------

    @staticmethod
    def clean_json_response(response_text):

        cleaned = response_text.strip()

        # ---------------------------------------------
        # REMOVE MARKDOWN WRAPPERS
        # ---------------------------------------------

        if cleaned.startswith("```json"):

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
    # SKILLS SCORE
    # -----------------------------------------------------

    @staticmethod
    def calculate_skills_score(
        match_result
    ):

        semantic_score = match_result.get(
            "semantic_match_score",
            0
        )

        score = min(
            round(float(semantic_score), 1),
            10
        )

        matched_skills = len(
            match_result.get(
                "matched_skills",
                []
            )
        )

        missing_skills = len(
            match_result.get(
                "missing_skills",
                []
            )
        )

        justification = (
            f"Matched {matched_skills} required skills "
            f"with {missing_skills} missing skills."
        )

        return {

            "score": score,

            "weight": 30,

            "justification":
                justification
        }

    # -----------------------------------------------------
    # EXPERIENCE SCORE
    # -----------------------------------------------------

    @staticmethod
    def calculate_experience_score(
        candidate_profile
    ):

        projects = candidate_profile.get(
            "projects",
            []
        )

        project_count = len(projects)

        if project_count >= 3:

            score = 8.5

            justification = (
                "Candidate has multiple strong technical projects."
            )

        elif project_count >= 1:

            score = 6.5

            justification = (
                "Candidate has some relevant project exposure."
            )

        else:

            score = 3.0

            justification = (
                "Limited relevant experience/projects."
            )

        return {

            "score": score,

            "weight": 25,

            "justification":
                justification
        }

    # -----------------------------------------------------
    # EDUCATION SCORE
    # -----------------------------------------------------

    @staticmethod
    def calculate_education_score(
        candidate_profile
    ):

        education = candidate_profile.get(
            "education",
            []
        )

        certifications = candidate_profile.get(
            "certifications",
            []
        )

        score = 5.0

        if education:

            score += 2.0

        if len(certifications) >= 2:

            score += 1.5

        score = min(score, 10)

        justification = (
            "Relevant education background "
            "with additional certifications."
        )

        return {

            "score": score,

            "weight": 15,

            "justification":
                justification
        }

    # -----------------------------------------------------
    # PROJECT PORTFOLIO SCORE (LLM-BASED)
    # -----------------------------------------------------

    @staticmethod
    def calculate_project_score(
        candidate_profile,
        jd_profile
    ):

        projects = candidate_profile.get(
            "projects",
            []
        )

        if not projects:

            return {

                "score": 3.0,

                "weight": 20,

                "justification":
                    "No significant projects found."
            }

        prompt_template = """
You are an expert AI hiring evaluator.

Evaluate the candidate's projects based on:

1. Technical complexity
2. Relevance to job role
3. AI/ML depth
4. Production readiness
5. Modern frameworks/tools usage

Candidate Projects:
{projects}

Job Description:
{jd_profile}

IMPORTANT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations outside JSON
- Score must be between 0 and 10

Required JSON format:
{{
    "score": 0,
    "justification": ""
}}
"""

        prompt = PromptTemplate(

            input_variables=[
                "projects",
                "jd_profile"
            ],

            template=prompt_template
        )

        formatted_prompt = prompt.format(

            projects=json.dumps(
                projects,
                indent=2
            ),

            jd_profile=json.dumps(
                jd_profile,
                indent=2
            )
        )

        response = generate_response(

            formatted_prompt,

            model=PRO_MODEL
        )

        cleaned_response = (
            ScoreAgent.clean_json_response(
                response
            )
        )

        try:

            parsed = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError:

            return {

                "score": 6.0,

                "weight": 20,

                "justification":
                    "Unable to fully evaluate project quality."
            }

        raw_score = float(
            parsed.get(
                "score",
                6.0
            )
        )
        # -------------------------------------------------
        # CALIBRATION
        # -------------------------------------------------

        calibrated_score = raw_score * 0.9

        score = round(
            min(
                max(
                    calibrated_score,
                    0
                ),
                10
            ),

            1
        )

        justification = parsed.get(
            "justification",
            "Project evaluation completed."
        )

        return {

            "score": score,

            "weight": 20,

            "justification":
                justification
        }

    # -----------------------------------------------------
    # COMMUNICATION SCORE
    # -----------------------------------------------------

    @staticmethod
    def calculate_communication_score(
        candidate_profile
    ):

        summary = candidate_profile.get(
            "summary",
            ""
        )

        word_count = len(
            summary.split()
        )

        if word_count >= 25:

            score = 8.0

            justification = (
                "Resume content is clear and well-structured."
            )

        else:

            score = 5.5

            justification = (
                "Resume communication could be improved."
            )

        return {

            "score": score,

            "weight": 10,

            "justification":
                justification
        }

    # -----------------------------------------------------
    # TOTAL WEIGHTED SCORE
    # -----------------------------------------------------

    @classmethod
    def calculate_total_score(
        cls,
        dimension_scores
    ):

        total = 0

        for dimension in (
            dimension_scores.values()
        ):

            weighted = (

                dimension["score"]

                * dimension["weight"]

            ) / 100

            total += weighted

        return round(total, 2)

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    @staticmethod
    def generate_recommendation(
        total_score
    ):

        if total_score >= 8:

            return "Strong Hire"

        elif total_score >= 6.5:

            return "Hire"

        elif total_score >= 5:

            return "Consider"

        else:

            return "Reject"

    # -----------------------------------------------------
    # MAIN EVALUATION PIPELINE
    # -----------------------------------------------------

    @classmethod
    def evaluate_candidate(
        cls,
        candidate_profile,
        match_result,
        jd_profile
    ):

        dimension_scores = {

            "skills_match":
                cls.calculate_skills_score(
                    match_result
                ),

            "experience_relevance":
                cls.calculate_experience_score(
                    candidate_profile
                ),

            "education_certs":
                cls.calculate_education_score(
                    candidate_profile
                ),

            "project_portfolio":
                cls.calculate_project_score(
                    candidate_profile,
                    jd_profile
                ),

            "communication_quality":
                cls.calculate_communication_score(
                    candidate_profile
                )
        }

        total_score = (
            cls.calculate_total_score(
                dimension_scores
            )
        )

        recommendation = (
            cls.generate_recommendation(
                total_score
            )
        )

        final_summary = (

            f"Candidate received a weighted score "
            f"of {total_score}/10 with recommendation: "
            f"{recommendation}."
        )

        result = {

            "candidate_name":
                candidate_profile.get(
                    "candidate_name",
                    "Unknown Candidate"
                ),

            "dimension_scores":
                dimension_scores,

            "weighted_total_score":
                total_score,

            "recommendation":
                recommendation,

            "final_summary":
                final_summary
        }

        try:

            validated = CandidateScore(
                **result
            )

        except ValidationError as e:

            raise ValueError(
                f"Score validation failed:\n{e}"
            )

        return validated.model_dump()