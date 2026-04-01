# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autonomous QA test case generation system that transforms requirements into production-ready CSV test suites using a multi-stage LLM pipeline. Supports Azure DevOps work item ingestion, plain text, or file inputs.

## Setup & Running

```bash
# Initial setup (creates venv, installs dependencies)
bash setup.sh

# Activate virtual environment
source venv/bin/activate

# Run Streamlit web UI
streamlit run app.py

# Run CLI
python src/main.py --source text --value "requirement text" --mode strict
python src/main.py --source azure --value "https://dev.azure.com/..." --mode exploratory

# Debug a single pipeline stage
python debug_stage_runner.py
```

No test runner or lint commands are configured in this project.

## Architecture

### Pipeline Stages (`src/pipeline/orchestrator.py`)

The core is a 4-stage sequential LLM pipeline:

1. **Reader** — Extracts atomic requirements from raw input, assigns REQ-001, REQ-002, ... identifiers. Uses `prompts/azure-requirement-reader.txt`.
2. **Generator** — Creates a 12-column markdown table of test cases from the extracted requirements. Uses `prompts/generator.txt`. Two modes:
   - **Strict**: Deterministic, production-safe, requirement-backed only
   - **Exploratory**: Broader coverage including edge cases, abuse, security scenarios
3. **Validator** — Validates coverage, deduplicates, repairs missing requirements. Uses `prompts/validator.txt`. May trigger a coverage repair loop via `prompts/coverage_regenerator.txt`.
4. **Post-Processing** — Parses markdown table → JSON rows, normalizes fields, runs quality gates, reassigns TC_IDs, builds trace matrix and coverage summary.

### Key Source Files

| File | Role |
|------|------|
| `app.py` | Streamlit web UI (input, real-time progress, artifact downloads) |
| `src/main.py` | CLI entry point |
| `src/pipeline/orchestrator.py` | Orchestrates all 4 pipeline stages |
| `src/pipeline/agent_runner.py` | LLM invocation with retry/continuation logic, supports Groq and Ollama |
| `src/pipeline/quality_gates.py` | 6 final output validation checks |
| `src/pipeline/coverage_utils.py` | Coverage metrics, gap detection, trace matrix |
| `src/pipeline/table_parser.py` | Markdown table → JSON row extraction |
| `src/pipeline/row_normalizer.py` | Field normalization (priority, type, team, automation flag) |
| `src/azure/azure_client.py` | Azure DevOps REST API client |
| `src/azure/azure_parser.py` | HTML content extraction from Azure work items |
| `src/config.py` | Settings loaded from `.env` |
| `src/models.py` | `NormalizedRequirement` Pydantic model |

### LLM Providers (`src/pipeline/agent_runner.py`)

- **Primary**: Groq (`GROQ_API_KEY`, `GROQ_MODEL`)
- **Fallback**: Ollama (`OLLAMA_URL`, `OLLAMA_MODEL`)
- Handles rate limits with exponential backoff, incomplete outputs with continuation prompts

### Test Case Schema (12 columns — immutable)

```
Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data |
Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate
```

- **Priority**: P0, P1, P2 only
- **Type**: Positive/Negative UI, Edge/Timeout, State management, Performance, Integration, API validation, Security
- **Test Data**: `key=value` format only (no JSON, no prose)

### Outputs (`output/`)

- `final_test_cases.csv` — Final test suite
- `latest_run.json` — Full pipeline run data
- `trace_matrix.json` — Requirement-to-TC traceability
- `coverage_summary.json` — Coverage metrics before/after repair

### QA Rules

The `rules/` directory contains the QA execution guidelines injected into prompts. `rules/qa-rules.md` is the primary ruleset (7 rules covering coverage types, atomicity, expected result determinism, schema enforcement, and test data format). The `rules/0*.md` files cover individual topics and are loaded by `src/pipeline/prompt_loader.py`.

## Environment Configuration (`.env`)

```
AZURE_ORG=...
AZURE_PROJECT=...
AZURE_PAT=...
GROQ_API_KEY=...
GROQ_MODEL=llama-3.1-8b-instant
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OUTPUT_DIR=output
PROMPTS_DIR=prompts
RULES_PATH=rules/qa-rules.md
```
