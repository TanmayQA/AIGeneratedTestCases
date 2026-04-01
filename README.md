# AI Generated Test Cases Pipeline 🤖📉

An autonomous QA test case generation system that transforms requirements into production-ready CSV test suites using a multi-stage LLM pipeline. This tool supports Azure DevOps work item ingestion, plain text, or file inputs to automatically generate extensive, edge-case inclusive test cases.

## ✨ Features

- **Multi-Stage LLM Pipeline**: Operates through a 4-stage pipeline (Reader, Generator, Validator, Post-Processing) for extremely robust outputs.
- **Multiple Integrations**: Directly fetch requirements via Azure DevOps REST APIs or provide textual requirements.
- **Strict & Exploratory Modes**: Generate purely deterministic, requirement-backed scenarios, or broaden the scope for abuse, edge cases, and security test cases.
- **Auto-Correction & Validation**: Features built-in auto-repair loops if the generated test coverage misses any requirements.
- **Traceability Matrix**: Generates requirement-to-test-case traceability matrix and coverage summaries.
- **Interactive UI**: Includes a Streamlit-based web interface for real-time progress monitoring and artifact downloads.

## 🚀 Setup & Running

### 1. Installation

```bash
# Initial setup (creates venv & installs dependencies)
bash setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configuration
Create a `.env` file in the root directory and configure the environment variables:

```env
AZURE_ORG=your_org
AZURE_PROJECT=your_project
AZURE_PAT=your_personal_access_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OUTPUT_DIR=output
PROMPTS_DIR=prompts
RULES_PATH=rules/qa-rules.md
```

### 3. Running the Application

**Start the Web UI (Recommended)**
```bash
streamlit run app.py
```

**Run via CLI**
```bash
# Using plain text
python src/main.py --source text --value "Your requirement text here" --mode strict

# Using Azure DevOps integration
python src/main.py --source azure --value "https://dev.azure.com/..." --mode exploratory
```

## 🧠 Architecture Overview

The core is a 4-stage sequential LLM pipeline orchestrated inside `src/pipeline/orchestrator.py`:

1. **Reader**: Extracts atomic requirements from raw input, assigning identifiers (REQ-001, REQ-002, etc.).
2. **Generator**: Creates a comprehensive 12-column markdown table of test cases based on the requirements.
3. **Validator**: Validates coverage, deduplicates, and triggers auto-repair loops if any requirements are missing.
4. **Post-Processing**: Parses outputs into structured JSON/CSV, normalizes fields, enforces quality gates, and builds the trace matrix.

### Generated Test Case Schema

Each generated test case strictly follows a 12-column format:
`Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate`

Outputs are saved in the `output/` directory, including the final `final_test_cases.csv`, `trace_matrix.json`, and `coverage_summary.json`.
