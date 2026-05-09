import json
import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


class Exporter:

    # =====================================================
    # JSON EXPORT
    # =====================================================

    @staticmethod
    def export_json(

        results,

        output_path
    ):

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(

                results,

                file,

                indent=4
            )

    # =====================================================
    # CSV EXPORT
    # =====================================================

    @staticmethod
    def export_csv(

        results,

        output_path
    ):

        rows = []

        for idx, candidate in enumerate(
            results,
            start=1
        ):

            row = {

                "Rank":
                    idx,

                "Candidate Name":
                    candidate[
                        "candidate_name"
                    ],

                "Overall Score":
                    candidate[
                        "weighted_total_score"
                    ],

                "Recommendation":
                    candidate[
                        "recommendation"
                    ]
            }

            # -------------------------------------------------
            # ADD DIMENSION SCORES
            # -------------------------------------------------

            dimensions = candidate.get(
                "dimension_scores",
                {}
            )

            for (
                dimension,
                details
            ) in dimensions.items():

                pretty_name = (
                    dimension
                    .replace("_", " ")
                    .title()
                )

                row[
                    f"{pretty_name} Score"
                ] = details.get(
                    "score",
                    0
                )

                row[
                    f"{pretty_name} Justification"
                ] = details.get(
                    "justification",
                    ""
                )

            rows.append(
                row
            )

        df = pd.DataFrame(
            rows
        )

        df.to_csv(

            output_path,

            index=False
        )

    # =====================================================
    # PDF EXPORT
    # =====================================================

    @staticmethod
    def export_pdf(

        results,

        output_path
    ):

        # -------------------------------------------------
        # CREATE DOCUMENT
        # -------------------------------------------------

        doc = SimpleDocTemplate(
            output_path
        )

        styles = (
            getSampleStyleSheet()
        )

        elements = []

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Paragraph(

            "AI Resume Screening Shortlist Report",

            styles["Title"]
        )

        elements.append(
            title
        )

        elements.append(
            Spacer(1, 20)
        )

        # =================================================
        # PROCESS EACH CANDIDATE
        # =================================================

        for idx, candidate in enumerate(
            results,
            start=1
        ):

            # ---------------------------------------------
            # HEADER
            # ---------------------------------------------

            heading = Paragraph(

                f"""
                <b>
                Rank #{idx} —
                {candidate['candidate_name']}
                </b>
                """,

                styles["Heading2"]
            )

            elements.append(
                heading
            )

            elements.append(
                Spacer(1, 12)
            )

            # ---------------------------------------------
            # BASIC INFORMATION
            # ---------------------------------------------

            basic_info = f"""

            <b>Overall Score:</b>
            {candidate['weighted_total_score']}/10
            <br/><br/>

            <b>Recommendation:</b>
            {candidate['recommendation']}
            <br/><br/>

            <b>Final Summary:</b>
            {candidate['final_summary']}
            <br/><br/>
            """

            elements.append(

                Paragraph(

                    basic_info,

                    styles["BodyText"]
                )
            )

            elements.append(
                Spacer(1, 10)
            )

            # ---------------------------------------------
            # DIMENSION SCORES
            # ---------------------------------------------

            dimensions = candidate.get(
                "dimension_scores",
                {}
            )

            dimension_heading = Paragraph(

                "<b>Dimension-Level Evaluation</b>",

                styles["Heading3"]
            )

            elements.append(
                dimension_heading
            )

            elements.append(
                Spacer(1, 8)
            )

            for (
                dimension,
                details
            ) in dimensions.items():

                pretty_name = (
                    dimension
                    .replace("_", " ")
                    .title()
                )

                score = details.get(
                    "score",
                    0
                )

                weight = details.get(
                    "weight",
                    0
                )

                justification = details.get(
                    "justification",
                    "No justification available."
                )

                dimension_text = f"""

                <b>{pretty_name}</b>
                <br/><br/>

                Score:
                {score}/10
                <br/>

                Weight:
                {weight}%
                <br/><br/>

                Justification:
                {justification}
                <br/><br/>
                """

                elements.append(

                    Paragraph(

                        dimension_text,

                        styles["BodyText"]
                    )
                )

                elements.append(
                    Spacer(1, 8)
                )

            # ---------------------------------------------
            # SEPARATOR
            # ---------------------------------------------

            elements.append(
                Spacer(1, 20)
            )

            elements.append(
                PageBreak()
            )

        # =================================================
        # BUILD PDF
        # =================================================

        doc.build(
            elements
        )