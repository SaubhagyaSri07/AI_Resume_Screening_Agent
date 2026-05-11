import sys
import os
import json
import pandas as pd

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
# SESSION STATE
# =====================================================

if "results" not in st.session_state:

    st.session_state.results = None

if "screening_completed" not in st.session_state:

    st.session_state.screening_completed = False

if "json_output_path" not in st.session_state:

    st.session_state.json_output_path = ""

if "csv_output_path" not in st.session_state:

    st.session_state.csv_output_path = ""

if "pdf_output_path" not in st.session_state:

    st.session_state.pdf_output_path = ""

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
# JOB DESCRIPTION
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
                    "✅ JD parsed successfully."
                )

            except Exception as e:

                st.error(
                    "❌ Failed to parse JD."
                )

                st.exception(e)

# =====================================================
# CANDIDATE UPLOADS
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

    st.session_state.screening_completed = False

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

            with st.spinner(
                "Running AI screening pipeline..."
            ):

                st.session_state.results = (
                    ScreeningPipeline.process_candidates(

                        jd_text=
                            jd_text,

                        uploaded_files=
                            uploaded_files
                    )
                )

            st.session_state.screening_completed = True

        except Exception as e:

            st.error(
                "❌ Pipeline execution failed."
            )

            st.exception(e)

# =====================================================
# DISPLAY RESULTS
# =====================================================

if st.session_state.screening_completed:

    results = st.session_state.results

    st.success(
        "✅ Screening completed successfully."
    )

    # =================================================
    # SHORTLIST TABLE
    # =================================================

    st.divider()

    st.header(
        "📋 Recruiter Shortlist Table"
    )

    shortlist_rows = []

    for idx, candidate in enumerate(
        results,
        start=1
    ):

        ai_score = candidate.get(
            "weighted_total_score",
            0
        )

        ai_recommendation = candidate.get(
            "recommendation",
            "Unknown"
        )

        final_score = candidate.get(
            "final_score",
            ai_score
        )

        final_recommendation = candidate.get(
            "final_recommendation",
            ai_recommendation
        )

        dimension_scores = candidate.get(
            "dimension_scores",
            {}
        )

        shortlist_rows.append({

            "Rank":
                idx,

            "Candidate":
                candidate.get(
                    "candidate_name",
                    "Unknown"
                ),

            "Final Score":
                final_score,

            "Recommendation":
                final_recommendation,

            "Skills":
                dimension_scores.get(
                    "skills_match",
                    {}
                ).get(
                    "score",
                    0
                ),

            "Experience":
                dimension_scores.get(
                    "experience_relevance",
                    {}
                ).get(
                    "score",
                    0
                ),

            "Portfolio":
                dimension_scores.get(
                    "project_portfolio",
                    {}
                ).get(
                    "score",
                    0
                ),

            "Flagged":
                candidate.get(
                    "hr_override",
                    {}
                ).get(
                    "flagged_for_review",
                    False
                )
        })

    shortlist_df = pd.DataFrame(
        shortlist_rows
    )

    st.dataframe(

        shortlist_df,

        use_container_width=True,

        hide_index=True
    )

    # =================================================
    # DETAILED REPORTS
    # =================================================

    st.divider()

    st.header(
        "📑 Detailed Candidate Reports"
    )

    # =================================================
    # DISPLAY CANDIDATES
    # =================================================

    for idx, candidate in enumerate(
        results,
        start=1
    ):

        # =============================================
        # AI VALUES
        # =============================================

        ai_score = candidate.get(
            "weighted_total_score",
            0
        )

        ai_recommendation = candidate.get(
            "recommendation",
            "Unknown"
        )

        # =============================================
        # FINAL VALUES
        # =============================================

        final_score = candidate.get(
            "final_score",
            ai_score
        )

        final_recommendation = candidate.get(
            "final_recommendation",
            ai_recommendation
        )

        candidate_name = candidate.get(
            "candidate_name",
            "Unknown Candidate"
        )

        # =============================================
        # BADGES
        # =============================================

        if final_recommendation == "Strong Hire":

            badge = "🟢"

        elif final_recommendation == "Hire":

            badge = "🔵"

        elif final_recommendation == "Consider":

            badge = "🟠"

        else:

            badge = "🔴"

        expander_title = (

            f"{badge} "

            f"Rank #{idx} — "

            f"{candidate_name} "

            f"({final_score}/10)"
        )

        # =============================================
        # EXPANDER STATE
        # =============================================

        expander_key = (
            f"expander_{idx}"
        )

        if expander_key not in st.session_state:

            st.session_state[
                expander_key
            ] = (idx == 1)

        # =============================================
        # CANDIDATE EXPANDER
        # =============================================

        with st.expander(

            expander_title,

            expanded=st.session_state[
                expander_key
            ]
        ):

            # =========================================
            # SUMMARY
            # =========================================

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

            # =========================================
            # METRICS
            # =========================================

            metric_col1, metric_col2 = (
                st.columns(2)
            )

            with metric_col1:

                st.metric(

                    label=
                        "Final Score",

                    value=
                        f"{final_score}/10"
                )

            with metric_col2:

                st.metric(

                    label=
                        "Recommendation",

                    value=
                        final_recommendation
                )

            # =========================================
            # ORIGINAL AI DECISION
            # =========================================

            if candidate.get(
                "hr_override",
                {}
            ).get(
                "override_applied",
                False
            ):

                st.warning(
                    f"""
AI originally recommended:

{ai_recommendation}
({ai_score}/10)
"""
                )

            st.divider()

            # =========================================
            # SKILL MATCHING
            # =========================================

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

            # =========================================
            # DETAILED MATCHES
            # =========================================

            detailed_matches = (
                match_result.get(
                    "detailed_matches",
                    []
                )
            )

            if detailed_matches:

                st.subheader(
                    "🔍 Detailed Semantic Matches"
                )

                detailed_rows = []

                for match in detailed_matches:

                    detailed_rows.append({

                        "JD Skill":
                            match.get(
                                "jd_skill"
                            ),

                        "Best Match":
                            match.get(
                                "best_match"
                            ),

                        "Similarity":
                            match.get(
                                "similarity"
                            ),

                        "Match Type":
                            match.get(
                                "match_type"
                            )
                    })

                detailed_df = pd.DataFrame(
                    detailed_rows
                )

                st.dataframe(

                    detailed_df,

                    use_container_width=True,

                    hide_index=True
                )

            st.divider()

            # =========================================
            # DIMENSION SCORES
            # =========================================

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

            # =========================================
            # HR OVERRIDE PANEL
            # =========================================

            st.subheader(
                "👨‍💼 HR Override Panel"
            )

            override_enabled = st.checkbox(

                "Enable HR Override",

                value=candidate.get(
                    "hr_override",
                    {}
                ).get(
                    "override_applied",
                    False
                ),

                key=f"override_{idx}"
            )

            # =========================================
            # OVERRIDE ENABLED
            # =========================================

            if override_enabled:

                st.session_state[
                    expander_key
                ] = True

                override_score = st.slider(

                    "Override Final Score",

                    min_value=0.0,

                    max_value=10.0,

                    value=float(
                        final_score
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

                        index=[
                            "Strong Hire",
                            "Hire",
                            "Consider",
                            "Reject"
                        ].index(
                            final_recommendation
                        ),

                        key=
                            f"recommendation_{idx}"
                    )
                )

                hr_reason = st.text_area(

                    "HR Override Reason",

                    value=candidate.get(
                        "hr_override",
                        {}
                    ).get(
                        "reason",
                        ""
                    ),

                    placeholder=
                    """
Explain why the score or
recommendation was overridden...
""",

                    key=f"reason_{idx}"
                )

                flagged = st.checkbox(

                    "Flag Candidate For Manual Review",

                    value=candidate.get(
                        "hr_override",
                        {}
                    ).get(
                        "flagged_for_review",
                        False
                    ),

                    key=f"flag_{idx}"
                )

                # =====================================
                # STORE OVERRIDE
                # =====================================

                candidate["hr_override"] = {

                    "override_applied":
                        True,

                    "original_score":
                        ai_score,

                    "final_score":
                        override_score,

                    "original_recommendation":
                        ai_recommendation,

                    "final_recommendation":
                        override_recommendation,

                    "reason":
                        hr_reason,

                    "flagged_for_review":
                        flagged
                }

                # =====================================
                # FINAL VALUES
                # =====================================

                candidate[
                    "final_score"
                ] = override_score

                candidate[
                    "final_recommendation"
                ] = override_recommendation

                st.success(
                    "HR override applied."
                )

                if flagged:

                    st.error(
                        "🚩 Candidate flagged for manual review."
                    )

            # =========================================
            # REMOVE OVERRIDE
            # =========================================

            else:

                if "hr_override" in candidate:

                    del candidate[
                        "hr_override"
                    ]

                if "final_score" in candidate:

                    del candidate[
                        "final_score"
                    ]

                if "final_recommendation" in candidate:

                    del candidate[
                        "final_recommendation"
                    ]

    # =================================================
    # SAVE OVERRIDES
    # =================================================

    override_path = os.path.join(

        project_root,

        "outputs",

        "hr_overrides.json"
    )

    override_data = []

    for candidate in results:

        if "hr_override" in candidate:

            override_data.append({

                "candidate_name":
                    candidate[
                        "candidate_name"
                    ],

                **candidate[
                    "hr_override"
                ]
            })

    with open(
        override_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            override_data,

            file,

            indent=4
        )

    # =================================================
    # EXPORT RESULTS
    # =================================================

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

    st.session_state.json_output_path = (
        json_output_path
    )

    st.session_state.csv_output_path = (
        csv_output_path
    )

    st.session_state.pdf_output_path = (
        pdf_output_path
    )

    # =================================================
    # DOWNLOAD SECTION
    # =================================================

    st.divider()

    st.header(
        "📥 Export Reports"
    )

    col1, col2, col3 = st.columns(3)

    # =============================================
    # JSON
    # =============================================

    with col1:

        with open(
            st.session_state.json_output_path,
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

                use_container_width=True,

                on_click="ignore"
            )

    # =============================================
    # CSV
    # =============================================

    with col2:

        with open(
            st.session_state.csv_output_path,
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

                use_container_width=True,

                on_click="ignore"
            )

    # =============================================
    # PDF
    # =============================================

    with col3:

        with open(
            st.session_state.pdf_output_path,
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

                use_container_width=True,

                on_click="ignore"
            )