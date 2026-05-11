from pydantic import (
    BaseModel,
    ValidationError
)

from typing import Dict

import json
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

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

    # =====================================================
    # EMBEDDING MODEL
    # =====================================================

    embedding_model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )

    # -----------------------------------------------------
    # CLEAN JSON RESPONSE
    # -----------------------------------------------------

    @staticmethod
    def clean_json_response(
        response_text
    ):

        cleaned = response_text.strip()

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
                .strip()
            )

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
    # SAFE TEXT NORMALIZATION
    # -----------------------------------------------------

    @staticmethod
    def normalize_text(
        value
    ):

        # =============================================
        # STRING
        # =============================================

        if isinstance(
            value,
            str
        ):

            return value.strip()

        # =============================================
        # LIST
        # =============================================

        elif isinstance(
            value,
            list
        ):

            normalized_items = []

            for item in value:

                if isinstance(
                    item,
                    list
                ):

                    normalized_items.extend(

                        str(sub_item)

                        for sub_item in item
                    )

                else:

                    normalized_items.append(
                        str(item)
                    )

            return " ".join(
                normalized_items
            ).strip()

        # =============================================
        # NONE
        # =============================================

        elif value is None:

            return ""

        # =============================================
        # FALLBACK
        # =============================================

        return str(value).strip()

    # -----------------------------------------------------
    # EMBEDDINGS
    # -----------------------------------------------------

    @classmethod
    def get_embedding(

        cls,

        text
    ):

        normalized_text = (
            cls.normalize_text(text)
        )

        if not normalized_text:

            normalized_text = "empty"

        embedding = cls.embedding_model.encode(

            [normalized_text],

            convert_to_numpy=True
        )[0]

        return embedding

    # -----------------------------------------------------
    # COSINE SIMILARITY
    # -----------------------------------------------------

    @staticmethod
    def compute_similarity(

        embedding1,

        embedding2
    ):

        similarity = cosine_similarity(

            [embedding1],

            [embedding2]

        )[0][0]

        return float(similarity)

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

        score = min(
            round(float(semantic_score), 1),
            10
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

    @classmethod
    def calculate_experience_score(

        cls,

        candidate_profile,

        jd_profile
    ):

        # =================================================
        # JD CONTEXT
        # =================================================

        jd_context = " ".join([

            cls.normalize_text(
                jd_profile.get(
                    "required_skills",
                    []
                )
            ),

            cls.normalize_text(
                jd_profile.get(
                    "preferred_skills",
                    []
                )
            ),

            cls.normalize_text(
                jd_profile.get(
                    "responsibilities",
                    []
                )
            )
        ])

        # =================================================
        # CANDIDATE PROJECTS
        # =================================================

        projects = candidate_profile.get(
            "projects",
            []
        )

        experience = candidate_profile.get(
            "experience",
            []
        )

        if not projects and not experience:

            return {

                "score": 3.0,

                "weight": 25,

                "justification":
                    "Limited relevant experience or project evidence."
            }

        project_texts = []

        # =================================================
        # PROJECT NORMALIZATION
        # =================================================

        for project in projects:

            if not isinstance(
                project,
                dict
            ):

                continue

            title = cls.normalize_text(

                project.get(
                    "title",
                    ""
                )
            )

            description = cls.normalize_text(

                project.get(
                    "description",
                    []
                )
            )

            technologies = cls.normalize_text(

                project.get(
                    "technologies",
                    []
                )
            )

            combined_text = " ".join([

                title,

                description,

                technologies
            ]).strip()

            if combined_text:

                project_texts.append(
                    combined_text
                )

        # =================================================
        # EXPERIENCE NORMALIZATION
        # =================================================

        if isinstance(
            experience,
            list
        ):

            for exp in experience:

                if isinstance(
                    exp,
                    dict
                ):

                    combined_exp = " ".join([

                        cls.normalize_text(
                            exp.get(
                                "job_title",
                                ""
                            )
                        ),

                        cls.normalize_text(
                            exp.get(
                                "company",
                                ""
                            )
                        ),

                        cls.normalize_text(
                            exp.get(
                                "description",
                                ""
                            )
                        )
                    ])

                    if combined_exp.strip():

                        project_texts.append(
                            combined_exp
                        )

                else:

                    normalized_exp = (
                        cls.normalize_text(
                            exp
                        )
                    )

                    if normalized_exp:

                        project_texts.append(
                            normalized_exp
                        )

        # =================================================
        # NO VALID EXPERIENCE
        # =================================================

        if not project_texts:

            return {

                "score": 3.0,

                "weight": 25,

                "justification":
                    "No usable project or experience data found."
            }

        # =================================================
        # EMBEDDINGS
        # =================================================

        jd_embedding = cls.get_embedding(
            jd_context
        )

        similarity_scores = []

        for text in project_texts:

            if not text.strip():

                continue

            project_embedding = (
                cls.get_embedding(
                    text
                )
            )

            similarity = cls.compute_similarity(

                jd_embedding,

                project_embedding
            )

            similarity_scores.append(
                similarity
            )

        # =================================================
        # NO VALID SIMILARITIES
        # =================================================

        if not similarity_scores:

            return {

                "score": 3.0,

                "weight": 25,

                "justification":
                    "Unable to determine relevant experience alignment."
            }

        # =================================================
        # USE TOP PROJECTS
        # =================================================

        top_scores = sorted(

            similarity_scores,

            reverse=True

        )[:3]

        average_similarity = float(
            np.mean(top_scores)
        )

        # =================================================
        # CALIBRATION
        # =================================================

        calibrated_score = round(
            average_similarity * 10,
            1
        )

        calibrated_score = min(
            max(
                calibrated_score,
                0
            ),
            10
        )

        # =================================================
        # JUSTIFICATION
        # =================================================

        if calibrated_score >= 8:

            justification = (
                "Candidate demonstrates highly relevant "
                "project and experience alignment with the target role."
            )

        elif calibrated_score >= 6:

            justification = (
                "Candidate shows moderately relevant "
                "experience and project alignment."
            )

        elif calibrated_score >= 4:

            justification = (
                "Candidate has partially relevant "
                "experience but limited direct alignment."
            )

        else:

            justification = (
                "Candidate experience shows weak "
                "alignment with the target role."
            )

        return {

            "score":
                calibrated_score,

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

        return {

            "score": score,

            "weight": 15,

            "justification":
                "Relevant education background with additional certifications."
        }

    # -----------------------------------------------------
    # PROJECT PORTFOLIO SCORE
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
You are an expert hiring evaluator.

Evaluate the candidate's projects based on:

1. Technical complexity
2. Relevance to the job role
3. Production readiness
4. Modern frameworks/tools
5. Practical implementation capability

Candidate Projects:
{projects}

Job Description:
{jd_profile}

IMPORTANT:
- Return ONLY valid JSON
- No markdown
- Score must be between 0 and 10

Required JSON:
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

        calibrated_score = round(
            min(
                max(
                    raw_score * 0.9,
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

            "score":
                calibrated_score,

            "weight": 20,

            "justification":
                justification
        }

    # -----------------------------------------------------
    # COMMUNICATION SCORE
    # -----------------------------------------------------

    @classmethod
    def calculate_communication_score(

        cls,

        candidate_profile
    ):

        summary = cls.normalize_text(

            candidate_profile.get(
                "summary",
                ""
            )
        )

        word_count = len(
            summary.split()
        )

        if word_count >= 25:

            score = 8.0

            justification = (
                "Resume content is clear and professionally structured."
            )

        elif word_count >= 10:

            score = 6.5

            justification = (
                "Resume communication quality is acceptable."
            )

        else:

            score = 5.0

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
    # TOTAL SCORE
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

        return "Reject"

    # -----------------------------------------------------
    # FINAL EVALUATION
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

                    candidate_profile,

                    jd_profile
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
                final_summary,

            "match_result":
                match_result
        }

        try:

            CandidateScore(
                **{
                    k: v
                    for k, v in result.items()
                    if k != "match_result"
                }
            )

        except ValidationError as e:

            raise ValueError(
                f"Score validation failed:\n{e}"
            )

        return result