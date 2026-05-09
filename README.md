# AI Resume Screening Agent

An AI-powered recruitment assistant that helps HR teams evaluate candidates efficiently using structured resume parsing, semantic matching, and explainable scoring.

## Features

- JD Parsing Agent
- Resume Parsing Agent
- Structured Candidate Profile Extraction
- Pydantic Validation
- LangChain Prompt Orchestration
- Gemini AI Integration
- PDF/DOCX Resume Support
- Modular Agent Architecture

## Tech Stack

- Python
- Gemini 2.5 Flash / Gemini 2.5 Pro
- LangChain
- Pydantic
- sentence-transformers
- Streamlit
- pdfplumber
- python-docx

## Current Progress

### Completed
- Environment setup
- Gemini integration
- Resume parsing system
- JD extraction agent
- Candidate profile extraction agent

### In Progress
- Semantic matching engine
- Scoring engine
- Ranking pipeline
- Streamlit dashboard

## Security Mitigations

- API keys stored in `.env`
- `.env` excluded using `.gitignore`
- Structured JSON outputs
- Pydantic validation
- Modular architecture for safer processing

## Setup

```bash
pip install -r requirements.txt