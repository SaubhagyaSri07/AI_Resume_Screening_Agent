import json


class LinkedInParser:

    @staticmethod
    def parse_linkedin_json(
        file_path
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        candidate_profile = {

            "candidate_name":
                data.get("name", ""),

            "skills":
                data.get("skills", []),

            "projects":
                data.get("projects", []),

            "experience":
                data.get("experience", []),

            "education":
                data.get("education", []),

            "certifications":
                data.get(
                    "certifications",
                    []
                ),

            "tools_frameworks":
                data.get(
                    "tools_frameworks",
                    []
                ),

            "summary":
                data.get("summary", "")
        }

        return candidate_profile