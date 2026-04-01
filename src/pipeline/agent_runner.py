import json
import time
import requests
from src.config import Settings


EXPECTED_TABLE_HEADER = "| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate |"


def call_ollama_llm(prompt_text: str) -> str:
    url = f"{Settings.OLLAMA_URL}/api/generate"

    payload = {
        "model": Settings.OLLAMA_MODEL,
        "prompt": prompt_text,
        "stream": False
    }

    response = requests.post(url, json=payload, timeout=600)
    response.raise_for_status()

    data = response.json()
    text = data.get("response", "").strip()

    if not text:
        raise ValueError("Ollama returned empty response")

    return text


def call_groq_llm(prompt_text: str, max_retries: int = 3) -> str:
    if not Settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing")

    url = f"{Settings.GROQ_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {Settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": Settings.GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0,
        "max_tokens": 2500,
    }

    last_error = None

    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload, timeout=600)

        if response.status_code == 200:
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()
            if not text:
                raise ValueError("Groq returned empty response")
            return text

        if response.status_code == 429:
            wait = min(2 ** attempt, 20)
            print(f"429 hit. Retrying in {wait}s")
            time.sleep(wait)
            last_error = response
            continue

        response.raise_for_status()

    if last_error is not None:
        raise RuntimeError(f"Groq failed after retries: {last_error.status_code} {last_error.text}")

    raise RuntimeError("Groq failed after retries")


def call_llm(prompt_text: str) -> str:
    if Settings.MODEL_PROVIDER == "groq":
        try:
            return call_groq_llm(prompt_text)
        except Exception as exc:
            print(f"Groq failed: {exc}")
            print("Fallback to Ollama")
            return call_ollama_llm(prompt_text)

    return call_ollama_llm(prompt_text)


def build_stage_input(
    stage_prompt,
    rules_text,
    normalized_requirement,
    previous_output="",
    template_text="",
    api_contract_text=""
):
    requirement_json = json.dumps(
        normalized_requirement.model_dump(),
        indent=2,
        ensure_ascii=False
    )

    parts = [
        stage_prompt,
        "\n=== RULES ===\n",
        rules_text,
        "\n=== REQUIREMENT ===\n",
        requirement_json
    ]

    if template_text:
        parts += ["\n=== TEMPLATE ===\n", template_text]

    if api_contract_text:
        parts += ["\n=== API CONTRACT ===\n", api_contract_text]

    if previous_output:
        parts += ["\n=== PREVIOUS OUTPUT ===\n", previous_output]

    return "\n".join(parts)


def is_incomplete(text: str):
    if not text.strip():
        return True

    if "| Requirement_ID |" not in text:
        return False

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|")]

    if len(table_lines) < 5:
        return True

    if not lines[-1].startswith("|"):
        return True

    return False


def extract_first_table(text: str) -> str:
    lines = text.splitlines()

    table_started = False
    table_lines = []

    for line in lines:
        if "| Requirement_ID" in line:
            table_started = True

        if table_started:
            if not line.strip().startswith("|"):
                break
            table_lines.append(line)

    return "\n".join(table_lines).strip()


def is_dirty_output(text: str) -> bool:
    bad_patterns = [
        "###",
        "analysis",
        "suggestions",
        "overall analysis",
        "this appears to be",
        "here is",
        "this table covers",
        "based on the provided",
        "comprehensive list",
        "note that",
    ]

    lower = text.lower()
    return any(p in lower for p in bad_patterns)


def stage_output_invalid(stage_prompt: str, output: str) -> bool:
    text = output.strip()

    reader_mode = "QA Requirement Extractor" in stage_prompt
    generator_mode = (
        "COMPLETE, PRODUCTION-READY, EXCEL-COMPATIBLE test suite" in stage_prompt
        and "Act as a QA Validator." not in stage_prompt
    )
    validator_mode = "Act as a QA Validator." in stage_prompt

    if reader_mode:
        if text.startswith("|") or "| TC_ID |" in text or "| Requirement_ID |" in text:
            return True
        if "TC_ID" in text or "Automation Candidate" in text:
            return True

    if generator_mode:
        if EXPECTED_TABLE_HEADER not in text:
            return True
        if "REQ-LOCAL-" in text:
            return True
        if not text.startswith("|"):
            return True

    if validator_mode:
        if EXPECTED_TABLE_HEADER not in text:
            return True
        if "REQ-LOCAL-" in text:
            return True
        if not text.startswith("|"):
            return True

    return False


def run_stage_with_retry(
    stage_prompt,
    rules_text,
    normalized_requirement,
    previous_output="",
    template_text="",
    api_contract_text="",
    max_attempts: int = 2
):
    stage_input = build_stage_input(
        stage_prompt,
        rules_text,
        normalized_requirement,
        previous_output,
        template_text,
        api_contract_text
    )

    output = ""

    for attempt in range(3):
        output = call_llm(stage_input)
        print(f"Output size: {len(output)} (attempt {attempt + 1})")

        if stage_output_invalid(stage_prompt, output):
            print("⚠️ Stage output invalid for this stage. Retrying...")
            continue

        if not output.strip().startswith("|"):
            print("⚠️ Non-table output detected. Retrying...")
            continue

        if "| Requirement_ID" in output:
            output = extract_first_table(output)

        if is_dirty_output(output):
            print("⚠️ Pollution detected. Forcing retry...")
            continue

        break

    if not is_incomplete(output):
        return output

    combined = output

    for attempt in range(max_attempts):
        print(f"Incomplete output, retrying continuation... attempt {attempt + 1}")

        continuation_prompt = (
            stage_prompt
            + "\n\nCONTINUATION RULE:\n"
              "Continue ONLY the missing remaining content.\n"
              "Do NOT repeat already generated rows.\n"
              "Do NOT restart from the beginning.\n"
              "Return only the same output format.\n"
        )

        continuation_input = build_stage_input(
            continuation_prompt,
            rules_text,
            normalized_requirement,
            previous_output + "\n\nPARTIAL OUTPUT SO FAR:\n" + combined,
            template_text,
            api_contract_text
        )

        continuation = call_llm(continuation_input).strip()

        if continuation:
            combined = combined.rstrip() + "\n" + continuation

        if stage_output_invalid(stage_prompt, combined):
            print("⚠️ Combined continuation output invalid for this stage.")
            continue

        if not is_incomplete(combined):
            break

    return combined