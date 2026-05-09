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


class ScreeningPipeline:

    @staticmethod
    def process_candidates(

        jd_text,

        uploaded_files
    ):

        # =============================================
        # PARSE JOB DESCRIPTION
        # =============================================

        jd_profile = JDAgent.parse_jd(
            jd_text
        )

        results = []

        # =============================================
        # PROCESS EACH RESUME
        # =============================================

        for uploaded_file in uploaded_files:

            # -----------------------------------------
            # SAVE TEMP FILE
            # -----------------------------------------

            temp_path = os.path.join(

                "temp",

                uploaded_file.name
            )

            with open(
                temp_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            # -----------------------------------------
            # PARSE RESUME
            # -----------------------------------------

            resume_data = (
                ProfileAgent.parse_resume(
                    temp_path
                )
            )

            candidate_profile = (

                ProfileAgent.extract_candidate_profile(
                    resume_data["raw_text"]
                )
            )

            # -----------------------------------------
            # MATCHING
            # -----------------------------------------

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

            # -----------------------------------------
            # SCORING
            # -----------------------------------------

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

            results.append(
                final_result
            )

        # =============================================
        # SORT CANDIDATES
        # =============================================

        results = sorted(

            results,

            key=lambda x:
                x[
                    "weighted_total_score"
                ],

            reverse=True
        )

        return results