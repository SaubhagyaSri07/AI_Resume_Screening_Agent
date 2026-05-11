from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

import numpy as np


class MatchAgent:

    # =====================================================
    # LOAD EMBEDDING MODEL
    # =====================================================

    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )

    # =====================================================
    # INFERRED SKILL MAP
    # RECRUITER-STYLE SKILL INFERENCE
    # =====================================================

    INFERRED_SKILL_MAP = {

        # -------------------------------------------------
        # RAG ECOSYSTEM
        # -------------------------------------------------

        "retrieval augmented generation": [

            "semantic search",

            "vector databases",

            "vector retrieval",

            "retrieval systems",

            "knowledge retrieval"
        ],

        # -------------------------------------------------
        # LANGCHAIN / AGENTS
        # -------------------------------------------------

        "langchain": [

            "large language models",

            "generative ai",

            "ai agents"
        ],

        "langgraph": [

            "agentic ai",

            "workflow orchestration",

            "multi-agent systems",

            "ai agents"
        ],

        # -------------------------------------------------
        # TRANSFORMERS
        # -------------------------------------------------

        "huggingface transformers": [

            "natural language processing",

            "transformer models",

            "large language models"
        ],

        # -------------------------------------------------
        # FASTAPI
        # -------------------------------------------------

        "fastapi": [

            "rest apis",

            "backend apis",

            "api integration"
        ],

        # -------------------------------------------------
        # PYTORCH
        # -------------------------------------------------

        "pytorch": [

            "deep learning",

            "machine learning"
        ],

        # -------------------------------------------------
        # GEMINI API
        # -------------------------------------------------

        "gemini api": [

            "large language models",

            "generative ai"
        ]
    }

    # =====================================================
    # SKILL NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_skill(skill):

        normalized = (
            skill
            .strip()
            .lower()
        )

        skill_patterns = {

            # -------------------------------------------------
            # AI / ML
            # -------------------------------------------------

            "ml":
                "machine learning",

            "machine learning":
                "machine learning",

            "deep learning":
                "deep learning",

            "dl":
                "deep learning",

            "nlp":
                "natural language processing",

            "natural language processing":
                "natural language processing",

            "llm":
                "large language models",

            "llms":
                "large language models",

            "large language model":
                "large language models",

            "large language models":
                "large language models",

            "generative ai":
                "generative ai",

            "rag":
                "retrieval augmented generation",

            "retrieval augmented generation":
                "retrieval augmented generation",

            "agentic ai":
                "agentic ai",

            "transformers":
                "huggingface transformers",

            # -------------------------------------------------
            # APIs
            # -------------------------------------------------

            "api":
                "application programming interface",

            "apis":
                "application programming interfaces",

            "rest api":
                "rest apis",

            "rest apis":
                "rest apis",

            # -------------------------------------------------
            # DATABASES
            # -------------------------------------------------

            "vector database":
                "vector databases",

            "vector databases":
                "vector databases",

            # -------------------------------------------------
            # FRONTEND
            # -------------------------------------------------

            "react":
                "react.js",

            "reactjs":
                "react.js",

            "react.js":
                "react.js"
        }

        # -------------------------------------------------
        # SUBSTRING NORMALIZATION
        # -------------------------------------------------

        for (
            pattern,
            canonical_skill
        ) in skill_patterns.items():

            if pattern in normalized:

                return canonical_skill

        return normalized

    # =====================================================
    # GENERATE EMBEDDINGS
    # =====================================================

    @classmethod
    def get_embeddings(
        cls,
        texts
    ):

        return cls.model.encode(

            texts,

            convert_to_numpy=True
        )

    # =====================================================
    # COSINE SIMILARITY
    # =====================================================

    @staticmethod
    def compute_similarity(

        embedding1,

        embedding2
    ):

        similarity = cosine_similarity(

            [embedding1],

            [embedding2]

        )[0][0]

        return float(
            similarity
        )

    # =====================================================
    # INFERRED SKILL MATCHING
    # =====================================================

    @classmethod
    def inferred_skill_match(

        cls,

        jd_skill,

        candidate_skills
    ):

        jd_skill = (
            jd_skill
            .lower()
            .strip()
        )

        candidate_skills_lower = [

            skill.lower().strip()

            for skill in candidate_skills
        ]

        # -------------------------------------------------
        # CHECK INFERENCE MAP
        # -------------------------------------------------

        for (
            candidate_skill,
            inferred_skills
        ) in cls.INFERRED_SKILL_MAP.items():

            if candidate_skill in candidate_skills_lower:

                if jd_skill in inferred_skills:

                    return True

        return False

    # =====================================================
    # MATCH SKILLS
    # =====================================================

    @classmethod
    def match_skills(

        cls,

        jd_skills,

        candidate_skills
    ):

        matched_skills = []

        missing_skills = []

        similarity_scores = []

        detailed_matches = []

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if not jd_skills or not candidate_skills:

            return {

                "skills_similarity": 0.0,

                "matched_skills": [],

                "missing_skills": jd_skills,

                "semantic_match_score": 0.0,

                "detailed_matches": []
            }

        # -------------------------------------------------
        # NORMALIZE CANDIDATE SKILLS
        # -------------------------------------------------

        normalized_candidate_skills = [

            cls.normalize_skill(skill)

            for skill in candidate_skills
        ]

        # -------------------------------------------------
        # GENERATE EMBEDDINGS
        # -------------------------------------------------

        candidate_embeddings = cls.get_embeddings(
            normalized_candidate_skills
        )

        # =================================================
        # PROCESS JD SKILLS
        # =================================================

        for jd_skill in jd_skills:

            normalized_jd_skill = (
                cls.normalize_skill(jd_skill)
            )

            # ---------------------------------------------
            # DIRECT EXACT MATCH
            # ---------------------------------------------

            if normalized_jd_skill in normalized_candidate_skills:

                best_similarity = 1.0

                best_candidate_skill = (
                    candidate_skills[
                        normalized_candidate_skills.index(
                            normalized_jd_skill
                        )
                    ]
                )

            else:

                # -----------------------------------------
                # EMBEDDING MATCH
                # -----------------------------------------

                jd_embedding = cls.get_embeddings(
                    [normalized_jd_skill]
                )[0]

                best_similarity = 0.0

                best_candidate_skill = None

                for idx, candidate_embedding in enumerate(
                    candidate_embeddings
                ):

                    similarity = cls.compute_similarity(

                        jd_embedding,

                        candidate_embedding
                    )

                    if similarity > best_similarity:

                        best_similarity = similarity

                        best_candidate_skill = (
                            candidate_skills[idx]
                        )

                # -----------------------------------------
                # INFERRED MATCH
                # -----------------------------------------

                inferred_match = (
                    cls.inferred_skill_match(

                        normalized_jd_skill,

                        normalized_candidate_skills
                    )
                )

                if inferred_match:

                    best_similarity = max(
                        best_similarity,
                        0.82
                    )

                    if not best_candidate_skill:

                        best_candidate_skill = (
                            "Inferred Skill Match"
                        )

            # -------------------------------------------------
            # STORE SCORE
            # -------------------------------------------------

            similarity_scores.append(
                best_similarity
            )

            # -------------------------------------------------
            # DISPLAY FILTER
            # -------------------------------------------------

            display_match = (

                best_candidate_skill

                if best_similarity >= 0.50

                else None
            )

            # -------------------------------------------------
            # STORE EXPLAINABILITY
            # -------------------------------------------------

            detailed_matches.append({

                "jd_skill":
                    jd_skill,

                "normalized_jd_skill":
                    normalized_jd_skill,

                "best_match":
                    display_match,

                "similarity":
                    round(
                        float(best_similarity),
                        4
                    ),

                "match_type":

                    "direct"

                    if best_similarity == 1.0

                    else (

                        "inferred"

                        if best_similarity >= 0.82

                        else "semantic"
                    )
            })

            # -------------------------------------------------
            # FINAL MATCH THRESHOLD
            # -------------------------------------------------

            if best_similarity >= 0.55:

                matched_skills.append(
                    jd_skill
                )

            else:

                missing_skills.append(
                    jd_skill
                )

        # =================================================
        # FINAL SCORE
        # =================================================

        average_similarity = float(
            np.mean(similarity_scores)
        )

        semantic_match_score = round(

            average_similarity * 10,

            2
        )

        return {

            "skills_similarity":
                round(
                    average_similarity,
                    4
                ),

            "matched_skills":
                matched_skills,

            "missing_skills":
                missing_skills,

            "semantic_match_score":
                semantic_match_score,

            "detailed_matches":
                detailed_matches
        }