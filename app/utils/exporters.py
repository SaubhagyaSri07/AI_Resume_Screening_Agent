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

        # =================================================
        # PROCESS CANDIDATES
        # =================================================

        for idx, candidate in enumerate(
            results,
            start=1
        ):

            # ---------------------------------------------
            # AI VALUES
            # ---------------------------------------------

            ai_score = candidate.get(
                "weighted_total_score",
                0
            )

            ai_recommendation = candidate.get(
                "recommendation",
                "Unknown"
            )

            # ---------------------------------------------
            # FINAL VALUES
            # ---------------------------------------------

            final_score = candidate.get(
                "final_score",
                ai_score
            )

            final_recommendation = candidate.get(
                "final_recommendation",
                ai_recommendation
            )

            # ---------------------------------------------
            # HR OVERRIDE
            # ---------------------------------------------

            hr_override = candidate.get(
                "hr_override",
                {}
            )

            override_applied = hr_override.get(
                "override_applied",
                False
            )

            # ---------------------------------------------
            # BASE ROW
            # ---------------------------------------------

            row = {

                "Rank":
                    idx,

                "Candidate Name":
                    candidate.get(
                        "candidate_name",
                        "Unknown"
                    ),

                # -----------------------------------------
                # AI DECISION
                # -----------------------------------------

                "AI Score":
                    ai_score,

                "AI Recommendation":
                    ai_recommendation,

                # -----------------------------------------
                # FINAL DECISION
                # -----------------------------------------

                "Final Score":
                    final_score,

                "Final Recommendation":
                    final_recommendation,

                # -----------------------------------------
                # OVERRIDE
                # -----------------------------------------

                "HR Override Applied":
                    override_applied
            }

            # ---------------------------------------------
            # ADD OVERRIDE DETAILS
            # ONLY IF APPLIED
            # ---------------------------------------------

            if override_applied:

                row.update({

                    "Flagged For Review":
                        hr_override.get(
                            "flagged_for_review",
                            False
                        ),

                    "HR Reason":
                        hr_override.get(
                            "reason",
                            ""
                        )
                })

            # =================================================
            # DIMENSION SCORES
            # =================================================

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

        # =================================================
        # DATAFRAME
        # =================================================

        df = pd.DataFrame(
            rows
        )

        # =================================================
        # EXPORT CSV
        # =================================================

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
        # DOCUMENT
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
            # AI VALUES
            # ---------------------------------------------

            ai_score = candidate.get(
                "weighted_total_score",
                0
            )

            ai_recommendation = candidate.get(
                "recommendation",
                "Unknown"
            )

            # ---------------------------------------------
            # FINAL VALUES
            # ---------------------------------------------

            final_score = candidate.get(
                "final_score",
                ai_score
            )

            final_recommendation = candidate.get(
                "final_recommendation",
                ai_recommendation
            )

            # ---------------------------------------------
            # HR OVERRIDE
            # ---------------------------------------------

            hr_override = candidate.get(
                "hr_override",
                {}
            )

            override_applied = hr_override.get(
                "override_applied",
                False
            )

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

            # =================================================
            # BASIC INFO
            # =================================================

            # ---------------------------------------------
            # WITH HR OVERRIDE
            # ---------------------------------------------

            if override_applied:

                basic_info = f"""

                <b>Final Score:</b>
                {final_score}/10
                <br/><br/>

                <b>Final Recommendation:</b>
                {final_recommendation}
                <br/><br/>

                <b>AI Original Score:</b>
                {ai_score}/10
                <br/><br/>

                <b>AI Original Recommendation:</b>
                {ai_recommendation}
                <br/><br/>

                <b>Final Summary:</b>
                {candidate['final_summary']}
                <br/><br/>
                """

            # ---------------------------------------------
            # WITHOUT HR OVERRIDE
            # ---------------------------------------------

            else:

                basic_info = f"""

                <b>Final Score:</b>
                {final_score}/10
                <br/><br/>

                <b>Final Recommendation:</b>
                {final_recommendation}
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

            # =================================================
            # HR OVERRIDE SECTION
            # =================================================

            if override_applied:

                override_text = f"""

                <b>HR Override Applied:</b>
                Yes
                <br/><br/>

                <b>Flagged For Manual Review:</b>
                {hr_override.get('flagged_for_review')}
                <br/><br/>

                <b>HR Override Reason:</b>
                {hr_override.get('reason')}
                <br/><br/>
                """

                elements.append(

                    Paragraph(

                        override_text,

                        styles["BodyText"]
                    )
                )

                elements.append(
                    Spacer(1, 10)
                )

            # =================================================
            # DIMENSION SCORES
            # =================================================

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

            # =================================================
            # PAGE SEPARATOR
            # =================================================

            elements.append(
                Spacer(1, 20)
            )

            # ---------------------------------------------
            # AVOID EXTRA BLANK PAGE
            # ---------------------------------------------

            if idx != len(results):

                elements.append(
                    PageBreak()
                )

        # =================================================
        # BUILD PDF
        # =================================================

        doc.build(
            elements
        )