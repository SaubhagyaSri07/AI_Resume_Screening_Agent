import json
import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle
)

from reportlab.lib import colors

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib.pagesizes import (
    letter
)


# =========================================================
# EXPORTER
# =========================================================

class Exporter:

    # =====================================================
    # BUILD SHORTLIST TABLE
    # =====================================================

    @staticmethod
    def build_shortlist_table(
        results
    ):

        shortlist_rows = []

        for idx, candidate in enumerate(
            results,
            start=1
        ):

            # -------------------------------------------------
            # AI VALUES
            # -------------------------------------------------

            ai_score = candidate.get(
                "weighted_total_score",
                0
            )

            ai_recommendation = candidate.get(
                "recommendation",
                "Unknown"
            )

            # -------------------------------------------------
            # FINAL VALUES
            # -------------------------------------------------

            final_score = candidate.get(
                "final_score",
                ai_score
            )

            final_recommendation = candidate.get(
                "final_recommendation",
                ai_recommendation
            )

            # -------------------------------------------------
            # HR OVERRIDE
            # -------------------------------------------------

            hr_override = candidate.get(
                "hr_override",
                {}
            )

            override_applied = hr_override.get(
                "override_applied",
                False
            )

            flagged = hr_override.get(
                "flagged_for_review",
                False
            )

            shortlist_rows.append({

                "Rank":
                    idx,

                "Candidate Name":
                    candidate.get(
                        "candidate_name",
                        "Unknown"
                    ),

                "Final Score":
                    round(
                        float(final_score),
                        2
                    ),

                "Recommendation":
                    final_recommendation,

                "HR Override":
                    "Yes"
                    if override_applied
                    else "No",

                "Flagged":
                    "Yes"
                    if flagged
                    else "No"
            })

        return shortlist_rows

    # =====================================================
    # JSON EXPORT
    # =====================================================

    @classmethod
    def export_json(

        cls,

        results,

        output_path
    ):

        shortlist_table = (
            cls.build_shortlist_table(
                results
            )
        )

        export_payload = {

            "shortlist_table":
                shortlist_table,

            "candidate_reports":
                results
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(

                export_payload,

                file,

                indent=4,

                ensure_ascii=False
            )

    # =====================================================
    # CSV EXPORT
    # =====================================================

    @classmethod
    def export_csv(

        cls,

        results,

        output_path
    ):

        shortlist_table = (
            cls.build_shortlist_table(
                results
            )
        )

        df = pd.DataFrame(
            shortlist_table
        )

        df.to_csv(

            output_path,

            index=False
        )

    # =====================================================
    # PDF EXPORT
    # =====================================================

    @classmethod
    def export_pdf(

        cls,

        results,

        output_path
    ):

        # -------------------------------------------------
        # DOCUMENT
        # -------------------------------------------------

        doc = SimpleDocTemplate(

            output_path,

            pagesize=letter
        )

        styles = (
            getSampleStyleSheet()
        )

        elements = []

        # =================================================
        # TITLE
        # =================================================

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
        # SHORTLIST TABLE HEADING
        # =================================================

        shortlist_heading = Paragraph(

            "<b>Recruiter Shortlist Table</b>",

            styles["Heading2"]
        )

        elements.append(
            shortlist_heading
        )

        elements.append(
            Spacer(1, 12)
        )

        # =================================================
        # BUILD SHORTLIST TABLE
        # =================================================

        shortlist_table = (
            cls.build_shortlist_table(
                results
            )
        )

        table_data = [[

            "Rank",
            "Candidate",
            "Final Score",
            "Recommendation",
            "Override",
            "Flagged"
        ]]

        for row in shortlist_table:

            table_data.append([

                row["Rank"],

                row["Candidate Name"],

                f"{row['Final Score']}/10",

                row["Recommendation"],

                row["HR Override"],

                row["Flagged"]
            ])

        table = Table(

            table_data,

            colWidths=[
                50,
                180,
                80,
                110,
                70,
                60
            ]
        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#2E3B4E")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    10
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.whitesmoke
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica"
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                )
            ])
        )

        elements.append(
            table
        )

        elements.append(
            Spacer(1, 24)
        )

        # =================================================
        # DETAILED REPORTS HEADING
        # =================================================

        detail_heading = Paragraph(

            "<b>Detailed Candidate Reports</b>",

            styles["Heading2"]
        )

        elements.append(
            detail_heading
        )

        elements.append(
            Spacer(1, 18)
        )

        # =================================================
        # PROCESS EACH CANDIDATE
        # =================================================

        for idx, candidate in enumerate(
            results,
            start=1
        ):

            # -------------------------------------------------
            # AI VALUES
            # -------------------------------------------------

            ai_score = candidate.get(
                "weighted_total_score",
                0
            )

            ai_recommendation = candidate.get(
                "recommendation",
                "Unknown"
            )

            # -------------------------------------------------
            # FINAL VALUES
            # -------------------------------------------------

            final_score = candidate.get(
                "final_score",
                ai_score
            )

            final_recommendation = candidate.get(
                "final_recommendation",
                ai_recommendation
            )

            # -------------------------------------------------
            # HR OVERRIDE
            # -------------------------------------------------

            hr_override = candidate.get(
                "hr_override",
                {}
            )

            override_applied = hr_override.get(
                "override_applied",
                False
            )

            flagged = hr_override.get(
                "flagged_for_review",
                False
            )

            # =================================================
            # HEADER
            # =================================================

            heading = Paragraph(

                f"""
                <b>
                Rank #{idx} —
                {candidate.get('candidate_name', 'Unknown')}
                </b>
                """,

                styles["Heading2"]
            )

            elements.append(
                heading
            )

            elements.append(
                Spacer(1, 10)
            )

            # =================================================
            # BASIC INFO
            # =================================================

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
                {candidate.get('final_summary', '')}
                <br/><br/>
                """

            else:

                basic_info = f"""

                <b>Final Score:</b>
                {final_score}/10
                <br/><br/>

                <b>Final Recommendation:</b>
                {final_recommendation}
                <br/><br/>

                <b>Final Summary:</b>
                {candidate.get('final_summary', '')}
                <br/><br/>
                """

            elements.append(

                Paragraph(
                    basic_info,
                    styles["BodyText"]
                )
            )

            elements.append(
                Spacer(1, 8)
            )

            # =================================================
            # HR OVERRIDE DETAILS
            # =================================================

            if override_applied:

                override_text = f"""

                <b>HR Override Applied:</b>
                Yes
                <br/><br/>

                <b>Flagged For Manual Review:</b>
                {"Yes" if flagged else "No"}
                <br/><br/>

                <b>HR Reason:</b>
                {hr_override.get('reason', '')}
                <br/><br/>
                """

                elements.append(

                    Paragraph(
                        override_text,
                        styles["BodyText"]
                    )
                )

                elements.append(
                    Spacer(1, 8)
                )

            # =================================================
            # DIMENSION SCORES
            # =================================================

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
                    ""
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
            # PAGE BREAK
            # =================================================

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