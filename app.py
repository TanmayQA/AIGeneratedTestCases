from pathlib import Path
from io import StringIO
from datetime import datetime

import pandas as pd
import streamlit as st

from src.pipeline.orchestrator import execute_pipeline
from src.config import Settings


st.set_page_config(
    page_title="QA Agent Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

EXPECTED_HEADER = [
    "Requirement_ID",
    "TC_ID",
    "Scenario",
    "Pre-Conditions",
    "Steps",
    "Test Data",
    "Expected Result",
    "Priority",
    "Type",
    "Tags",
    "Execution Team",
    "Automation Candidate",
]


def init_session_state() -> None:
    if "run_history" not in st.session_state:
        st.session_state.run_history = []
    if "is_running" not in st.session_state:
        st.session_state.is_running = False
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "sample_text" not in st.session_state:
        st.session_state.sample_text = ""
    if "last_uploaded_filename" not in st.session_state:
        st.session_state.last_uploaded_filename = ""
    if "last_run_provider" not in st.session_state:
        st.session_state.last_run_provider = Settings.MODEL_PROVIDER
    if "last_run_source" not in st.session_state:
        st.session_state.last_run_source = "text"



def get_stage_list() -> list[str]:
    return [
        "reader",
        "generator",
        "validator",
        "post_processing",
        "finalizer",
    ]


def render_stage_chips(all_stages: list[str], completed: list[str]) -> str:
    completed_set = set(completed)
    chips = []
    for stage in all_stages:
        if stage in completed_set:
            css_class = "stage-chip stage-chip-done"
            icon = "✅"
        else:
            css_class = "stage-chip"
            icon = "⏳"
        chips.append(f'<span class="{css_class}">{icon} {stage}</span>')
    return '<div class="stage-chip-wrap">' + "".join(chips) + "</div>"


def read_file_text(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8", errors="ignore")


def count_csv_rows(csv_text: str) -> int:
    if not csv_text.strip():
        return 0
    lines = [line for line in csv_text.splitlines() if line.strip()]
    return max(0, len(lines) - 1)


def load_csv_safely(csv_text: str):
    try:
        df = pd.read_csv(StringIO(csv_text))
        if list(df.columns) != EXPECTED_HEADER:
            return None, f"Unexpected CSV header. Found: {list(df.columns)}"
        return df, None
    except Exception as e:
        return None, str(e)


init_session_state()

st.markdown(
    """
<style>
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(59,130,246,0.10), transparent 25%),
            radial-gradient(circle at top left, rgba(124,58,237,0.12), transparent 30%),
            linear-gradient(180deg, #0b1020 0%, #111827 45%, #0f172a 100%);
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .hero-wrap {
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.94));
        border: 1px solid rgba(99,102,241,0.24);
        border-radius: 26px;
        padding: 28px 30px 24px 30px;
        box-shadow: 0 14px 40px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 110px 1fr;
        gap: 18px;
        align-items: center;
    }

    .robot-shell {
        width: 98px;
        height: 98px;
        border-radius: 24px;
        background: linear-gradient(135deg, #1d4ed8, #7c3aed);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 10px 24px rgba(37,99,235,0.25);
        border: 1px solid rgba(255,255,255,0.08);
    }

    .hero-title {
        color: #f8fafc;
        font-size: 2.45rem;
        font-weight: 850;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }

    .hero-mini {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    .badge-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 16px;
    }

    .badge {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        color: white;
        letter-spacing: 0.2px;
    }

    .badge-blue { background: linear-gradient(135deg, #2563eb, #3b82f6); }
    .badge-purple { background: linear-gradient(135deg, #7c3aed, #8b5cf6); }
    .badge-green { background: linear-gradient(135deg, #059669, #10b981); }
    .badge-amber { background: linear-gradient(135deg, #d97706, #f59e0b); }

    .shield {
        margin-top: 16px;
        color: #c7d2fe;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .section-card {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }

    .section-title {
        color: #f8fafc;
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .section-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .info-strip {
        background: rgba(30, 41, 59, 0.72);
        border: 1px solid rgba(96, 165, 250, 0.25);
        color: #dbeafe;
        padding: 12px 14px;
        border-radius: 14px;
        margin-bottom: 1rem;
    }

    .pipeline-step {
        background: rgba(30,41,59,0.75);
        border: 1px solid rgba(148,163,184,0.15);
        color: #e2e8f0;
        border-radius: 12px;
        padding: 8px 10px;
        margin-bottom: 8px;
        font-size: 0.92rem;
        font-weight: 600;
    }

    .history-card {
        background: rgba(15,23,42,0.70);
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 14px;
        padding: 10px 12px;
        margin-bottom: 10px;
    }

    .history-title {
        color: #f8fafc;
        font-size: 0.92rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .history-meta {
        color: #94a3b8;
        font-size: 0.78rem;
    }

    .qa-meter {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0 10px 0;
    }

    .qa-tile {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 16px;
        padding: 14px;
    }

    .qa-tile-title {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 8px;
    }

    .qa-tile-value {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 800;
    }

    .stage-chip-wrap {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    .stage-chip {
        background: rgba(51,65,85,0.82);
        border: 1px solid rgba(148,163,184,0.20);
        color: #cbd5e1;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .stage-chip-done {
        background: rgba(6,95,70,0.82);
        border-color: rgba(52,211,153,0.30);
        color: #d1fae5;
    }

    @media (max-width: 980px) {
        .hero-grid {
            grid-template-columns: 1fr;
            text-align: center;
        }

        .robot-shell {
            margin: 0 auto;
        }

        .qa-meter {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero-wrap">
    <div class="hero-grid">
        <div class="robot-shell">🤖</div>
        <div>
            <div class="hero-title">QA Agent Console</div>
            <div class="hero-subtitle">
                Multi-stage AI pipeline for requirement analysis, test generation, validation, coverage repair, and final CSV export.
            </div>
            <div class="hero-mini">
                Use debug mode to inspect reader, generator, validator, and final pipeline outputs before trusting final CSV.
            </div>
            <div class="badge-row">
                <span class="badge badge-blue">Azure-Aware</span>
                <span class="badge badge-purple">AI Multi-Stage Pipeline</span>
                <span class="badge badge-green">CSV Ready</span>
                <span class="badge badge-amber">QA Workflow Engine</span>
            </div>
            <div class="shield">🛡️ QA Shield Active</div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ⚙️ Agent Controls")
    source = st.selectbox("Input Source", ["azure_url", "file", "text"])
    debug_mode = st.checkbox("Debug mode", value=True)

    st.markdown("---")
    st.markdown("## 🧠 Model Provider")
    provider_options = ["anthropic", "groq", "ollama"]
    default_index = provider_options.index(Settings.MODEL_PROVIDER) if Settings.MODEL_PROVIDER in provider_options else 0
    provider_ui = st.selectbox(
        "Choose Provider",
        provider_options,
        index=default_index,
    )

    anthropic_model_ui = st.text_input(
        "Anthropic Model",
        value=Settings.ANTHROPIC_MODEL,
        disabled=(provider_ui != "anthropic"),
    )

    groq_model_ui = st.text_input(
        "Groq Model",
        value=Settings.GROQ_MODEL,
        disabled=(provider_ui != "groq"),
    )

    ollama_model_ui = st.text_input(
        "Ollama Model",
        value=Settings.OLLAMA_MODEL,
        disabled=(provider_ui != "ollama"),
    )

    st.markdown("---")
    st.markdown("### 🧠 Pipeline")
    st.markdown(
        """
    <div class="pipeline-step">1. Requirement Reader</div>
    <div class="pipeline-step">2. Generator</div>
    <div class="pipeline-step">3. Validator</div>
    <div class="pipeline-step">4. Post Processing</div>
    <div class="pipeline-step">5. Finalizer</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🕘 Run History")
    if st.session_state.run_history:
        for item in st.session_state.run_history[:8]:
            st.markdown(
                f"""
            <div class="history-card">
                <div class="history-title">{item['title']}</div>
                <div class="history-meta">
                    {item['time']} • source={item['source']} • provider={item['provider']}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No runs yet.")

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📥 Requirement Intake</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Select a source and provide the requirement payload for the QA agent.</div>',
    unsafe_allow_html=True,
)

input_value = ""

if source == "azure_url":
    input_value = st.text_input(
        "Azure DevOps Work Item URL",
        placeholder="https://dev.azure.com/.../_workitems/edit/12345",
    )

elif source == "file":
    uploaded_file = st.file_uploader("Upload requirement file", type=["txt", "md"])
    if uploaded_file is not None:
        st.session_state.last_uploaded_filename = uploaded_file.name
        input_value = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        st.success(f"Uploaded: {uploaded_file.name}")

else:
    c1, c2 = st.columns([4, 1])
    with c2:
        if st.button("⚡ Load Sample", use_container_width=True, disabled=st.session_state.is_running):
            st.session_state.sample_text = (
                "As a user, I want to log in with OTP so that I can access my account securely.\n\n"
                "Acceptance Criteria:\n"
                "1. User can enter a valid registered mobile number.\n"
                "2. OTP is sent successfully.\n"
                "3. Invalid mobile format shows an error.\n"
                "4. Expired OTP shows an error.\n"
            )
    with c1:
        input_value = st.text_area(
            "Paste requirement text",
            height=220,
            value=st.session_state.sample_text,
            placeholder="Paste user story, acceptance criteria, bug description, or requirement text here...",
        )
    


st.markdown(
    """
<div class="info-strip">
    <strong>Recommendation:</strong> keep <strong>Debug mode</strong> enabled until generator and validator output stabilize.
</div>
""",
    unsafe_allow_html=True,
)

generate = st.button(
    "🚀 Launch QA Agent",
    type="primary",
    use_container_width=True,
    disabled=st.session_state.is_running,
)

if generate:
    if not input_value.strip():
        st.error("Please provide input before generating.")
    else:
        st.session_state.is_running = True

        Settings.MODEL_PROVIDER = provider_ui
        Settings.ANTHROPIC_MODEL = anthropic_model_ui.strip() or Settings.ANTHROPIC_MODEL
        Settings.GROQ_MODEL = groq_model_ui.strip() or Settings.GROQ_MODEL
        Settings.OLLAMA_MODEL = ollama_model_ui.strip() or Settings.OLLAMA_MODEL

        st.session_state.last_run_provider = provider_ui
        st.session_state.last_run_source = source

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🛰️ Agent Mission Status</div>', unsafe_allow_html=True)

        progress_placeholder = st.empty()
        stage_chip_placeholder = st.empty()
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        steps = []

        all_stages = get_stage_list()

        def progress_callback(message: str):
            steps.append(message)
            unique_steps = list(dict.fromkeys(steps))
            progress = min(len(unique_steps) / len(all_stages), 1.0)
            progress_bar.progress(progress)
            status_text.markdown(f"**Current Stage:** {message}")
            progress_placeholder.code("\n".join(steps))
            stage_chip_placeholder.markdown(
                render_stage_chips(all_stages, steps),
                unsafe_allow_html=True,
            )

        try:
            with st.spinner("QA Agent is reasoning through the requirement..."):
                result = execute_pipeline(
                    source=source,
                    value=input_value,
                    progress_callback=progress_callback,
                )

            result["provider"] = provider_ui
            result["anthropic_model"] = anthropic_model_ui
            result["groq_model"] = groq_model_ui
            result["ollama_model"] = ollama_model_ui
            result["source"] = source
            st.session_state.pipeline_result = result

            if source == "azure_url":
                history_title = input_value.strip()
            elif source == "file":
                history_title = st.session_state.last_uploaded_filename or "Uploaded Requirement File"
            else:
                history_title = "Direct Text Requirement"

            st.session_state.run_history.insert(
                0,
                {
                    "title": history_title[:70],
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": source,
                    "provider": provider_ui,
                },
            )

        except Exception as e:
            st.error(f"Generation failed: {e}")

        finally:
            st.session_state.is_running = False

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.pipeline_result:
    result = st.session_state.pipeline_result

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Output Control Center</div>', unsafe_allow_html=True)

    df, csv_error = load_csv_safely(result["final_csv_text"])

    if df is not None:
        st.dataframe(df, use_container_width=True)
        st.success(f"✅ Generated {len(df)} test cases successfully.")
    else:
        fallback_row_count = count_csv_rows(result["final_csv_text"])
        st.error(f"CSV load issue: {csv_error}")
        if fallback_row_count:
            st.info(f"Detected approximately {fallback_row_count} data rows from raw CSV text.")
        st.code(result["final_csv_text"][:5000], language="csv")

    coverage_before = result.get("coverage_score_before", 0)
    coverage_after = result.get("coverage_score_after", 0)
    expected_req_ids = result.get("expected_req_ids", [])
    stage_outputs = result.get("stage_outputs", {})
    final_source = stage_outputs.get("final_source", "unknown")
    result_provider = result.get("provider", st.session_state.last_run_provider)

    st.markdown(
        f"""
    <div class="qa-meter">
        <div class="qa-tile">
            <div class="qa-tile-title">Provider</div>
            <div class="qa-tile-value">{str(result_provider).upper()}</div>
        </div>
        <div class="qa-tile">
            <div class="qa-tile-title">Coverage Before</div>
            <div class="qa-tile-value">{coverage_before}%</div>
        </div>
        <div class="qa-tile">
            <div class="qa-tile-title">Coverage After</div>
            <div class="qa-tile-value">{coverage_after}%</div>
        </div>
        <div class="qa-tile">
            <div class="qa-tile-title">Expected REQs</div>
            <div class="qa-tile-value">{len(expected_req_ids)}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.caption(f"Requirement IDs detected: {', '.join(expected_req_ids) if expected_req_ids else 'None'}")
    st.caption(f"Final source used: {final_source}")

    if final_source == "finalizer":
        st.success("Final output refined by Finalizer stage")
    elif final_source == "validator":
        st.info("Final output from Validator stage")
    else:
        st.warning("Final output directly from Generator stage")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.download_button(
            label="⬇️ Final CSV",
            data=result["final_csv_text"],
            file_name=Path(result["csv_path"]).name,
            mime="text/csv",
            use_container_width=True,
        )

    with c2:
        st.download_button(
            label="⬇️ Full JSON",
            data=read_file_text(result["json_path"]),
            file_name=Path(result["json_path"]).name,
            mime="application/json",
            use_container_width=True,
        )

    with c3:
        st.download_button(
            label="⬇️ Trace Matrix",
            data=read_file_text(result["trace_path"]),
            file_name=Path(result["trace_path"]).name,
            mime="application/json",
            use_container_width=True,
        )

    with c4:
        st.download_button(
            label="⬇️ Coverage Summary",
            data=read_file_text(result["coverage_path"]),
            file_name=Path(result["coverage_path"]).name,
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if debug_mode:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔍 Stage Output Preview</div>', unsafe_allow_html=True)
 
        for stage_name, stage_output in stage_outputs.items():
            if stage_name == "final_source":
                continue
            with st.expander(stage_name, expanded=(stage_name in {"validator", "finalizer"})):
                st.code(str(stage_output)[:12000])

        st.markdown("</div>", unsafe_allow_html=True)