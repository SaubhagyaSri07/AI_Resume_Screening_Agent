import sys
import os

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

# =====================================================
# CREATE TEMP DIRECTORY
# =====================================================

os.makedirs(
    os.path.join(
        project_root,
        "temp"
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
semantic matching, and hiring recommendations.
"""
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📌 About")

    st.info(
        """
This AI-powered recruitment system can:

- Parse Job Descriptions
- Parse Resumes
- Extract Candidate Profiles
- Perform Semantic Skill Matching
- Evaluate Candidates using AI
- Generate Hiring Recommendations
- Rank Candidates Automatically
"""
    )

    st.divider()

    st.markdown(
        """
### ⚙️ Tech Stack

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

                # -------------------------------------
                # SAVE TEMP JD FILE
                # -------------------------------------

                temp_jd_path = os.path.join(

                    project_root,

                    "temp",

                    jd_file.name
                )

                with open(
                    temp_jd_path,
                    "wb"
                ) as f:

                    f.write(
                        jd_file.getbuffer()
                    )

                # -------------------------------------
                # PARSE JD FILE
                # -------------------------------------

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
# RESUME UPLOAD SECTION
# =====================================================

with right_col:

    st.subheader(
        "📂 Resume Upload"
    )

    uploaded_files = st.file_uploader(

        label="Upload Resume Files",

        type=["pdf", "docx"],

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
# PIPELINE EXECUTION
# =====================================================

if run_button:

    # =================================================
    # VALIDATION
    # =================================================

    if not jd_text.strip():

        st.warning(
            "Please provide a Job Description."
        )

    elif not uploaded_files:

        st.warning(
            "Please upload at least one resume."
        )

    else:

        try:

            # -----------------------------------------
            # RUN PIPELINE
            # -----------------------------------------

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

            # -----------------------------------------
            # SUCCESS
            # -----------------------------------------

            st.success(
                "✅ Screening completed successfully."
            )

            st.divider()

            st.header(
                "🏆 Candidate Rankings"
            )

            # =========================================
            # DISPLAY RESULTS
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

                expander_title = (

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
                    # OVERALL METRICS
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

                        st.markdown(
                            f"### {pretty_name}"
                        )

                        st.write(
                            f"**Score:** "
                            f"{details['score']}/10"
                        )

                        st.write(
                            f"**Weight:** "
                            f"{details['weight']}%"
                        )

                        st.write(
                            "**Justification:**"
                        )

                        st.info(
                            details.get(
                                "justification",
                                "No justification available."
                            )
                        )

        # =================================================
        # ERROR HANDLING
        # =================================================

        except Exception as e:

            st.error(
                "❌ Pipeline execution failed."
            )

            st.exception(e)