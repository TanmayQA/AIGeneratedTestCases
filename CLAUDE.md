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
python src/main.py --source text --value "requirement text" --mode local
python src/main.py --source azure_url --value "https://dev.azure.com/..." --mode full

# Debug a single pipeline stage (edit SOURCE/VALUE/MODE_VARIANT at top of file)
python debug_stage_runner.py
# Debug outputs saved to debug_outputs/
```

No test runner or lint commands are configured in this project.

## Architecture

### Pipeline Stages (`src/pipeline/orchestrator.py`)

The core is a 5-stage sequential LLM pipeline:

1. **Reader** — Extracts atomic requirements from raw input, assigns REQ-001, REQ-002, ... identifiers. Uses `src/skills/azure-requirement-reader.md`.
2. **Generator** — Creates a 12-column markdown table of test cases from the extracted requirements. Uses `src/skills/generator.md`. Two modes:
   - **Strict** (`--mode local`): Deterministic, production-safe, requirement-backed only
   - **Exploratory** (`--mode full`): Per-requirement expansion via `per_req_expander.py`; broader edge/abuse/security coverage
3. **Validator** — Validates coverage, deduplicates, repairs missing requirements. Uses `src/skills/validator.md`. May retry with a traceability-recovery prompt.
4. **Post-Processing** — Parses markdown table → JSON rows, normalizes fields, runs coverage repair loop (`src/skills/coverage_regenerator.md`), runs quality gates, reassigns TC_IDs, builds trace matrix.
5. **Finalizer** — Final LLM pass using `src/skills/finalizer.md` to ensure all Requirement_IDs are present and deduplicated before writing output.

### Key Source Files

| File | Role |
|------|------|
| `app.py` | Streamlit web UI (input, real-time progress, artifact downloads) |
| `src/main.py` | CLI entry point |
| `src/pipeline/orchestrator.py` | Orchestrates all 5 pipeline stages |
| `src/pipeline/agent_runner.py` | LLM invocation with retry/continuation logic; supports Anthropic, Groq, Ollama |
| `src/pipeline/per_req_expander.py` | Exploratory mode: generates test cases per requirement then merges |
| `src/pipeline/quality_gates.py` | 6 final output validation checks |
| `src/pipeline/coverage_utils.py` | Coverage metrics, gap detection, trace matrix |
| `src/pipeline/table_parser.py` | Markdown table → JSON row extraction |
| `src/pipeline/row_normalizer.py` | Field normalization (priority, type, team, automation flag) |
| `src/azure/azure_client.py` | Azure DevOps REST API client |
| `src/azure/azure_parser.py` | HTML content extraction from Azure work items |
| `src/config.py` | Settings loaded from `.env` |
| `src/models.py` | `NormalizedRequirement` Pydantic model |

### Prompt / Skill Files (`src/skills/`)

All LLM prompts are stored as markdown files in `src/skills/` and loaded by `src/pipeline/prompt_loader.py`. Rules from `rules/0*.md` and `rules/qa-rules.md` are concatenated and injected into every stage prompt.

An optional API contract can be placed at `input/api-contract.txt` — it is automatically injected into all stage prompts if present.

### LLM Providers (`src/pipeline/agent_runner.py`)

Provider is selected via `MODEL_PROVIDER` env var. All providers fall back to Ollama on failure.

| `MODEL_PROVIDER` | Primary keys |
|---|---|
| `anthropic` | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
| `groq` | `GROQ_API_KEY`, `GROQ_MODEL` |
| `ollama` (default) | `OLLAMA_URL`, `OLLAMA_MODEL` |

### Test Case Schema (18 columns)

```
Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data |
Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate |
Dependency_Type | Device_Sensitivity | Network_Sensitivity | Backend_Service |
Persona_Scenario | Status
```

- **Priority**: P0, P1, P2 only
- **Type**: Positive/Negative UI, Edge/Timeout, State management, Performance, Integration, API validation, Security
- **Test Data**: `key=value` format only (no JSON, no prose)
- **Dependency_Type**: Live API | Stub | None
- **Device_Sensitivity**: High | Medium | Low
- **Network_Sensitivity**: High | Medium | Low
- **Backend_Service**: API/service name or "-"
- **Persona_Scenario**: user context (e.g., Standard user, Security-conscious user)
- **Status**: DRAFT | NEEDS_REFINEMENT | APPROVED (default: DRAFT)

### Outputs (`output/`)

- `final_test_cases.csv` — Final test suite
- `latest_run.json` — Full pipeline run data
- `trace_matrix.json` — Requirement-to-TC traceability
- `coverage_summary.json` — Coverage metrics before/after repair

## Environment Configuration (`.env`)

```
# Azure DevOps (required for azure_url source)
AZURE_ORG=...
AZURE_PROJECT=...
AZURE_PAT=...

# LLM provider selection: anthropic | groq | ollama (default: ollama)
MODEL_PROVIDER=groq

# Anthropic (when MODEL_PROVIDER=anthropic)
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Groq (when MODEL_PROVIDER=groq)
GROQ_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama fallback / primary
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

OUTPUT_DIR=output
```
