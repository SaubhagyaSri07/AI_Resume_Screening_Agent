import sys
import os
import json

# =====================================================
# ADD PROJECT ROOT TO PYTHON PATH
# =====================================================

project_root = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if project_root not in sys.path:

    sys.path.append(project_root)

# =====================================================
# IMPORTS
# =====================================================

import streamlit as st

from app.pipeline import (
    ScreeningPipeline
)

from app.agents.profile_agent import (
    ProfileAgent
)

from app.utils.exporters import (
    Exporter
)

# =====================================================
# CREATE REQUIRED DIRECTORIES
# =====================================================

os.makedirs(
    os.path.join(
        project_root,
        "temp"
    ),
    exist_ok=True
)

os.makedirs(
    os.path.join(
        project_root,
        "outputs"
    ),
    exist_ok=True
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(

    page_title=
        "AI Resume Screening Agent",

    page_icon="🤖",

    layout="wide"
)

# =====================================================
# HEADER
# =====================================================

st.title(
    "🤖 AI Resume Screening Agent"
)

st.markdown(
    """
AI-powered recruitment assistant
for intelligent candidate evaluation,
semantic matching, recruiter scoring,
and hiring recommendations.
"""
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📌 About")

    st.info(
        """
Features:

- Resume Parsing
- JD Parsing
- LinkedIn JSON Ingestion
- Semantic Skill Matching
- AI-Based Candidate Scoring
- Recruiter Recommendations
- Human-in-the-Loop Overrides
- PDF / CSV / JSON Exports
"""
    )

    st.divider()

    st.markdown(
        """
### ⚙️ AI Stack

- Gemini 2.5 Pro
- Gemini 2.0 Flash
- Sentence Transformers
- Streamlit
- LangChain
- Pydantic
"""
    )

# =====================================================
# MAIN LAYOUT
# =====================================================

left_col, right_col = st.columns(
    [1, 1]
)

# =====================================================
# JOB DESCRIPTION SECTION
# =====================================================

with left_col:

    st.subheader(
        "📄 Job Description"
    )

    jd_input_method = st.radio(

        "Choose JD Input Method",

        [
            "Paste Text",
            "Upload File"
        ]
    )

    jd_text = ""

    # =================================================
    # TEXT INPUT
    # =================================================

    if jd_input_method == "Paste Text":

        jd_text = st.text_area(

            label="Paste Job Description",

            height=400,

            placeholder=
            """
Paste the job description here...

Example:
- Python
- NLP
- Machine Learning
- LLMs
- FastAPI
"""
        )

    # =================================================
    # FILE INPUT
    # =================================================

    else:

        jd_file = st.file_uploader(

            label="Upload JD File",

            type=["pdf", "docx"],

            accept_multiple_files=False
        )

        if jd_file:

            try:

                temp_jd_path = os.path.join(

                    project_root,

                    "temp",

                    jd_file.name
                )

                with open(
                    temp_jd_path,
                    "wb"
                ) as file:

                    file.write(
                        jd_file.getbuffer()
                    )

                parsed_jd = (
                    ProfileAgent.parse_resume(
                        temp_jd_path
                    )
                )

                jd_text = parsed_jd[
                    "raw_text"
                ]

                st.success(
                    "✅ JD file parsed successfully."
                )

            except Exception as e:

                st.error(
                    "❌ Failed to parse JD file."
                )

                st.exception(e)

# =====================================================
# CANDIDATE UPLOAD SECTION
# =====================================================

with right_col:

    st.subheader(
        "📂 Candidate Upload"
    )

    uploaded_files = st.file_uploader(

        label=
            "Upload Resume / LinkedIn Files",

        type=[
            "pdf",
            "docx",
            "json"
        ],

        accept_multiple_files=True
    )

    if uploaded_files:

        st.success(
            f"{len(uploaded_files)} file(s) uploaded."
        )

# =====================================================
# RUN BUTTON
# =====================================================

st.divider()

run_button = st.button(

    "🚀 Run AI Screening",

    use_container_width=True
)

# =====================================================
# EXECUTE PIPELINE
# =====================================================

if run_button:

    if not jd_text.strip():

        st.warning(
            "Please provide a Job Description."
        )

    elif not uploaded_files:

        st.warning(
            "Please upload candidate files."
        )

    else:

        try:

            # =========================================
            # RUN PIPELINE
            # =========================================

            with st.spinner(
                "Running AI screening pipeline..."
            ):

                results = (
                    ScreeningPipeline.process_candidates(

                        jd_text=
                            jd_text,

                        uploaded_files=
                            uploaded_files
                    )
                )

            # =========================================
            # EXPORT REPORTS
            # =========================================

            json_output_path = os.path.join(
                project_root,
                "outputs",
                "results.json"
            )

            csv_output_path = os.path.join(
                project_root,
                "outputs",
                "results.csv"
            )

            pdf_output_path = os.path.join(
                project_root,
                "outputs",
                "results.pdf"
            )

            Exporter.export_json(
                results,
                json_output_path
            )

            Exporter.export_csv(
                results,
                csv_output_path
            )

            Exporter.export_pdf(
                results,
                pdf_output_path
            )

            # =========================================
            # SUCCESS
            # =========================================

            st.success(
                "✅ Screening completed successfully."
            )

            st.divider()

            st.header(
                "🏆 Candidate Rankings"
            )

            hr_overrides = []

            # =========================================
            # DISPLAY CANDIDATES
            # =========================================

            for idx, candidate in enumerate(
                results,
                start=1
            ):

                candidate_name = candidate.get(
                    "candidate_name",
                    "Unknown Candidate"
                )

                recommendation = candidate.get(
                    "recommendation",
                    "Unknown"
                )

                total_score = candidate.get(
                    "weighted_total_score",
                    0
                )

                # =====================================
                # RECOMMENDATION COLORS
                # =====================================

                if recommendation == "Strong Hire":

                    badge = "🟢"

                elif recommendation == "Hire":

                    badge = "🔵"

                elif recommendation == "Consider":

                    badge = "🟠"

                else:

                    badge = "🔴"

                expander_title = (

                    f"{badge} "

                    f"{idx}. "

                    f"{candidate_name} "

                    f"— "

                    f"{recommendation} "

                    f"({total_score}/10)"
                )

                with st.expander(
                    expander_title
                ):

                    # ---------------------------------
                    # SUMMARY
                    # ---------------------------------

                    st.subheader(
                        "🧠 Final Summary"
                    )

                    st.write(
                        candidate.get(
                            "final_summary",
                            "No summary available."
                        )
                    )

                    st.divider()

                    # ---------------------------------
                    # METRICS
                    # ---------------------------------

                    metric_col1, metric_col2 = (
                        st.columns(2)
                    )

                    with metric_col1:

                        st.metric(

                            label=
                                "Overall Score",

                            value=
                                f"{total_score}/10"
                        )

                    with metric_col2:

                        st.metric(

                            label=
                                "Recommendation",

                            value=
                                recommendation
                        )

                    st.divider()

                    # ---------------------------------
                    # SKILL MATCHING
                    # ---------------------------------

                    st.subheader(
                        "🛠 Skill Matching"
                    )

                    match_result = candidate.get(
                        "match_result",
                        {}
                    )

                    matched_skills = (
                        match_result.get(
                            "matched_skills",
                            []
                        )
                    )

                    missing_skills = (
                        match_result.get(
                            "missing_skills",
                            []
                        )
                    )

                    if matched_skills:

                        st.success(
                            "Matched Skills:\n\n"
                            + ", ".join(
                                matched_skills
                            )
                        )

                    if missing_skills:

                        st.error(
                            "Missing Skills:\n\n"
                            + ", ".join(
                                missing_skills
                            )
                        )

                    st.divider()

                    # ---------------------------------
                    # DIMENSION SCORES
                    # ---------------------------------

                    st.subheader(
                        "📊 Dimension Scores"
                    )

                    dimension_scores = (
                        candidate.get(
                            "dimension_scores",
                            {}
                        )
                    )

                    for (
                        dimension,
                        details
                    ) in dimension_scores.items():

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

                        st.markdown(
                            f"### {pretty_name}"
                        )

                        st.progress(
                            score / 10
                        )

                        st.write(
                            f"Score: {score}/10"
                        )

                        st.write(
                            f"Weight: {weight}%"
                        )

                        st.info(
                            justification
                        )

                    st.divider()

                    # ---------------------------------
                    # HUMAN-IN-THE-LOOP PANEL
                    # ---------------------------------

                    st.subheader(
                        "👨‍💼 HR Override Panel"
                    )

                    override_enabled = st.checkbox(

                        "Enable HR Override",

                        key=f"override_{idx}"
                    )

                    if override_enabled:

                        override_score = st.slider(

                            "Override Score",

                            min_value=0.0,

                            max_value=10.0,

                            value=float(
                                total_score
                            ),

                            step=0.1,

                            key=f"score_{idx}"
                        )

                        override_recommendation = (
                            st.selectbox(

                                "Override Recommendation",

                                [
                                    "Strong Hire",
                                    "Hire",
                                    "Consider",
                                    "Reject"
                                ],

                                key=
                                    f"recommendation_{idx}"
                            )
                        )

                        hr_reason = st.text_area(

                            "HR Override Reason",

                            placeholder=
                            """
Explain why the score or
recommendation was overridden...
""",

                            key=f"reason_{idx}"
                        )

                        flagged = st.checkbox(

                            "Flag Candidate for Manual Review",

                            key=f"flag_{idx}"
                        )

                        override_data = {

                            "candidate_name":
                                candidate_name,

                            "original_score":
                                total_score,

                            "override_score":
                                override_score,

                            "original_recommendation":
                                recommendation,

                            "override_recommendation":
                                override_recommendation,

                            "reason":
                                hr_reason,

                            "flagged":
                                flagged
                        }

                        hr_overrides.append(
                            override_data
                        )

                        st.success(
                            "HR override applied."
                        )

            # =========================================
            # SAVE HR OVERRIDES
            # =========================================

            if hr_overrides:

                override_path = os.path.join(

                    project_root,

                    "outputs",

                    "hr_overrides.json"
                )

                with open(
                    override_path,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(

                        hr_overrides,

                        file,

                        indent=4
                    )

            # =========================================
            # DOWNLOAD SECTION
            # =========================================

            st.divider()

            st.header(
                "📥 Export Reports"
            )

            col1, col2, col3 = st.columns(3)

            # -----------------------------------------
            # JSON
            # -----------------------------------------

            with col1:

                with open(
                    json_output_path,
                    "rb"
                ) as file:

                    st.download_button(

                        label=
                            "Download JSON",

                        data=file,

                        file_name=
                            "results.json",

                        mime=
                            "application/json",

                        use_container_width=True
                    )

            # -----------------------------------------
            # CSV
            # -----------------------------------------

            with col2:

                with open(
                    csv_output_path,
                    "rb"
                ) as file:

                    st.download_button(

                        label=
                            "Download CSV",

                        data=file,

                        file_name=
                            "results.csv",

                        mime=
                            "text/csv",

                        use_container_width=True
                    )

            # -----------------------------------------
            # PDF
            # -----------------------------------------

            with col3:

                with open(
                    pdf_output_path,
                    "rb"
                ) as file:

                    st.download_button(

                        label=
                            "Download PDF Report",

                        data=file,

                        file_name=
                            "results.pdf",

                        mime=
                            "application/pdf",

                        use_container_width=True
                    )

        # =============================================
        # ERROR HANDLING
        # =============================================

        except Exception as e:

            st.error(
                "❌ Pipeline execution failed."
            )

            st.exception(e)