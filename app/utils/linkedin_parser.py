import json


class LinkedInParser:

    @staticmethod
    def normalize_experience(
        experience_list
    ):

        normalized = []

        for item in experience_list:

            # =========================================
            # ALREADY STRUCTURED
            # =========================================

            if isinstance(
                item,
                dict
            ):

                normalized.append({

                    "title":
                        item.get(
                            "title",
                            ""
                        ),

                    "company":
                        item.get(
                            "company",
                            ""
                        ),

                    "duration":
                        item.get(
                            "duration",
                            ""
                        ),

                    "description":
                        item.get(
                            "description",
                            []
                        )
                        if isinstance(
                            item.get(
                                "description",
                                []
                            ),
                            list
                        )
                        else [
                            str(
                                item.get(
                                    "description",
                                    ""
                                )
                            )
                        ]
                })

            # =========================================
            # STRING EXPERIENCE
            # =========================================

            else:

                normalized.append({

                    "title": "",

                    "company": "",

                    "duration": "",

                    "description": [
                        str(item)
                    ]
                })

        return normalized

    # =====================================================
    # MAIN PARSER
    # =====================================================

    @classmethod
    def parse_linkedin_json(

        cls,

        file_path
    ):

        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as file:

            data = json.load(file)

        # =================================================
        # EXPERIENCE NORMALIZATION
        # =================================================

        normalized_experience = (

            cls.normalize_experience(

                data.get(
                    "experience",
                    []
                )
            )
        )

        # =================================================
        # PROFILE
        # =================================================

        candidate_profile = {

            "candidate_name":

                data.get(

                    "candidate_name",

                    data.get(
                        "name",
                        ""
                    )
                ),

            "skills":

                data.get(
                    "skills",
                    []
                ),

            "projects":

                data.get(
                    "projects",
                    []
                ),

            "experience":
                normalized_experience,

            "education":

                data.get(
                    "education",
                    []
                ),

            "certifications":

                data.get(
                    "certifications",
                    []
                ),

            "tools_frameworks":

                data.get(

                    "tools_frameworks",

                    data.get(
                        "skills",
                        []
                    )
                ),

            "summary":

                data.get(

                    "summary",

                    data.get(
                        "headline",
                        ""
                    )
                )
        }

        return candidate_profile