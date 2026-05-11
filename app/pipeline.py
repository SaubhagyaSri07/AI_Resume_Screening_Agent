import os
import traceback

from app.agents.jd_agent import (
    JDAgent
)

from app.agents.profile_agent import (
    ProfileAgent
)

from app.agents.match_agent import (
    MatchAgent
)

from app.agents.score_agent import (
    ScoreAgent
)


# =========================================================
# SCREENING PIPELINE
# =========================================================

class ScreeningPipeline:

    # -----------------------------------------------------
    # ENSURE DIRECTORIES
    # -----------------------------------------------------

    @staticmethod
    def ensure_directories():

        os.makedirs(
            "temp",
            exist_ok=True
        )

        os.makedirs(
            "outputs",
            exist_ok=True
        )

    # -----------------------------------------------------
    # SAVE TEMP FILE
    # -----------------------------------------------------

    @staticmethod
    def save_temp_file(
        uploaded_file
    ):

        temp_file_path = os.path.join(

            "temp",

            uploaded_file.name
        )

        with open(
            temp_file_path,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )

        return temp_file_path

    # -----------------------------------------------------
    # PARSE CANDIDATE FILE
    # -----------------------------------------------------

    @classmethod
    def parse_candidate_file(

        cls,

        file_path
    ):

        parsed_data = (
            ProfileAgent.parse_resume(
                file_path
            )
        )

        # =================================================
        # LINKEDIN JSON
        # =================================================

        if "linkedin_profile" in parsed_data:

            return parsed_data[
                "linkedin_profile"
            ]

        # =================================================
        # PDF / DOCX
        # =================================================

        return (
            ProfileAgent
            .extract_candidate_profile(

                parsed_data[
                    "raw_text"
                ]
            )
        )

    # -----------------------------------------------------
    # MATCH CANDIDATE
    # -----------------------------------------------------

    @staticmethod
    def generate_match_result(

        jd_profile,

        candidate_profile
    ):

        return MatchAgent.match_skills(

            jd_profile.get(
                "required_skills",
                []
            ),

            candidate_profile.get(
                "skills",
                []
            )
        )

    # -----------------------------------------------------
    # SCORE CANDIDATE
    # -----------------------------------------------------

    @staticmethod
    def score_candidate(

        candidate_profile,

        match_result,

        jd_profile
    ):

        return ScoreAgent.evaluate_candidate(

            candidate_profile=
                candidate_profile,

            match_result=
                match_result,

            jd_profile=
                jd_profile
        )

    # -----------------------------------------------------
    # MAIN PIPELINE
    # -----------------------------------------------------

    @classmethod
    def process_candidates(

        cls,

        jd_text,

        uploaded_files
    ):

        # =================================================
        # ENSURE REQUIRED DIRECTORIES
        # =================================================

        cls.ensure_directories()

        # =================================================
        # VALIDATE INPUTS
        # =================================================

        if not jd_text.strip():

            raise ValueError(
                "Job Description cannot be empty."
            )

        if not uploaded_files:

            raise ValueError(
                "No candidate files uploaded."
            )

        # =================================================
        # PARSE JOB DESCRIPTION
        # =================================================

        jd_profile = JDAgent.parse_jd(
            jd_text
        )

        results = []

        # =================================================
        # PROCESS EACH CANDIDATE
        # =================================================

        for uploaded_file in uploaded_files:

            try:

                # -----------------------------------------
                # SAVE TEMP FILE
                # -----------------------------------------

                temp_file_path = (
                    cls.save_temp_file(
                        uploaded_file
                    )
                )

                # -----------------------------------------
                # PARSE PROFILE
                # -----------------------------------------

                candidate_profile = (
                    cls.parse_candidate_file(
                        temp_file_path
                    )
                )

                # -----------------------------------------
                # MATCHING
                # -----------------------------------------

                match_result = (
                    cls.generate_match_result(

                        jd_profile,

                        candidate_profile
                    )
                )

                # -----------------------------------------
                # SCORING
                # -----------------------------------------

                final_result = (
                    cls.score_candidate(

                        candidate_profile=
                            candidate_profile,

                        match_result=
                            match_result,

                        jd_profile=
                            jd_profile
                    )
                )

                # -----------------------------------------
                # SOURCE FILE INFO
                # -----------------------------------------

                final_result[
                    "source_file"
                ] = uploaded_file.name

                final_result[
                    "source_type"
                ] = os.path.splitext(
                    uploaded_file.name
                )[1].replace(
                    ".",
                    ""
                ).upper()

                # -----------------------------------------
                # STORE RESULT
                # -----------------------------------------

                results.append(
                    final_result
                )

            # =================================================
            # FILE-LEVEL ERROR HANDLING
            # =================================================

            except Exception as e:

                error_result = {

                    "candidate_name":
                        uploaded_file.name,

                    "weighted_total_score":
                        0,

                    "recommendation":
                        "Parsing Failed",

                    "final_summary":
                        str(e),

                    "source_file":
                        uploaded_file.name,

                    "source_type":
                        os.path.splitext(
                            uploaded_file.name
                        )[1].replace(
                            ".",
                            ""
                        ).upper(),

                    "error":
                        traceback.format_exc()
                }

                results.append(
                    error_result
                )

        # =================================================
        # SORT CANDIDATES
        # =================================================

        ranked_results = sorted(

            results,

            key=lambda candidate:

                candidate.get(
                    "weighted_total_score",
                    0
                ),

            reverse=True
        )

        # =================================================
        # ASSIGN RANKS
        # =================================================

        for idx, candidate in enumerate(

            ranked_results,

            start=1
        ):

            candidate["rank"] = idx

        return ranked_results