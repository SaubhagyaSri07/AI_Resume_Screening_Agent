import os

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

from app.utils.linkedin_parser import (
    LinkedInParser
)


class ScreeningPipeline:

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    @staticmethod
    def process_candidates(

        jd_text,

        uploaded_files
    ):

        # =================================================
        # ENSURE TEMP DIRECTORY EXISTS
        # =================================================

        os.makedirs(
            "temp",
            exist_ok=True
        )

        # =================================================
        # PARSE JOB DESCRIPTION
        # =================================================

        jd_profile = JDAgent.parse_jd(
            jd_text
        )

        results = []

        # =================================================
        # PROCESS EACH UPLOADED FILE
        # =================================================

        for uploaded_file in uploaded_files:

            # ---------------------------------------------
            # SAVE FILE TEMPORARILY
            # ---------------------------------------------

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

            # ---------------------------------------------
            # DETECT FILE TYPE
            # ---------------------------------------------

            extension = os.path.splitext(
                temp_file_path
            )[1].lower()

            # ---------------------------------------------
            # LINKEDIN JSON INGESTION
            # ---------------------------------------------

            if extension == ".json":

                candidate_profile = (

                    LinkedInParser
                    .parse_linkedin_json(

                        temp_file_path
                    )
                )

            # ---------------------------------------------
            # RESUME INGESTION
            # ---------------------------------------------

            else:

                parsed_resume = (

                    ProfileAgent.parse_resume(

                        temp_file_path
                    )
                )

                candidate_profile = (

                    ProfileAgent
                    .extract_candidate_profile(

                        parsed_resume[
                            "raw_text"
                        ]
                    )
                )

            # ---------------------------------------------
            # SEMANTIC MATCHING
            # ---------------------------------------------

            match_result = (

                MatchAgent.match_skills(

                    jd_profile[
                        "required_skills"
                    ],

                    candidate_profile[
                        "skills"
                    ]
                )
            )

            # ---------------------------------------------
            # AI SCORING
            # ---------------------------------------------

            final_result = (

                ScoreAgent.evaluate_candidate(

                    candidate_profile=
                        candidate_profile,

                    match_result=
                        match_result,

                    jd_profile=
                        jd_profile
                )
            )

            # ---------------------------------------------
            # STORE RESULT
            # ---------------------------------------------

            results.append(
                final_result
            )

        # =================================================
        # SORT CANDIDATES BY SCORE
        # =================================================

        ranked_results = sorted(

            results,

            key=lambda candidate:
                candidate[
                    "weighted_total_score"
                ],

            reverse=True
        )

        return ranked_results