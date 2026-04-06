from pathlib import Path

from src.pipeline.prompt_loader import load_all_prompt_assets
from src.pipeline.orchestrator import resolve_requirement, apply_mode
from src.pipeline.agent_runner import run_stage_with_retry

SOURCE = "text"
VALUE = """
As a user, I want to log in with OTP so that I can access my account securely.

Acceptance Criteria:
1. User can enter a valid registered mobile number.
2. OTP is sent successfully.
3. Invalid mobile format shows an error.
4. Expired OTP shows an error.
"""

EXPECTED_TABLE_HEADER = "| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate | Dependency_Type | Device_Sensitivity | Network_Sensitivity | Backend_Service | Persona_Scenario | Status |"

DEBUG_DIR = Path("debug_outputs")
DEBUG_DIR.mkdir(exist_ok=True, parents=True)


def save_output(filename: str, content: str) -> None:
    (DEBUG_DIR / filename).write_text(content, encoding="utf-8")


def print_stage_result(stage_name: str, output: str) -> None:
    print(f"\n\n===== {stage_name.upper()} OUTPUT =====\n")
    print(output[:12000])


def validate_reader_output(reader_output: str) -> None:
    if reader_output.strip().startswith("|") or "| TC_ID |" in reader_output or "| Requirement_ID |" in reader_output:
        print("\n❌ Reader output invalid: reader returned table/testcase content\n")
    else:
        print("\n✅ Reader output looks valid\n")


def validate_table_output(stage_name: str, output: str) -> None:
    if EXPECTED_TABLE_HEADER not in output:
        print(f"\n❌ {stage_name} header invalid\n")
    else:
        print(f"\n✅ {stage_name} header valid\n")


from src.config import Settings

def main() -> None:
    Settings.MODE_VARIANT = "strict"   # change to exploratory when needed
    assets = load_all_prompt_assets()
    normalized = resolve_requirement(SOURCE, VALUE)

    # Reader
    reader = run_stage_with_retry(
        assets["azure_requirement_reader"],
        assets["rules"],
        normalized,
        template_text=assets.get("template", ""),
        api_contract_text=assets.get("api_contract", ""),
    )
    save_output("01_reader_output.txt", reader)
    print_stage_result("reader", reader)
    validate_reader_output(reader)

    # Generator
    generator_prompt = apply_mode(assets["generator"], Settings.MODE_VARIANT, "generator")
    generator = run_stage_with_retry(
        generator_prompt,
        assets["rules"],
        normalized,
        previous_output=reader,
        template_text=assets.get("template", ""),
        api_contract_text=assets.get("api_contract", ""),
    )
    save_output("02_generator_output.txt", generator)
    print_stage_result("generator", generator)
    validate_table_output("Generator", generator)

    # Validator
    validator_prompt = apply_mode(assets["validator"], Settings.MODE_VARIANT, "validator")
    validator = run_stage_with_retry(
        validator_prompt,
        assets["rules"],
        normalized,
        previous_output=generator,
        template_text=assets.get("template", ""),
        api_contract_text=assets.get("api_contract", ""),
    )
    save_output("03_validator_output.txt", validator)
    print_stage_result("validator", validator)
    validate_table_output("Validator", validator)

    print(f"\n📁 Debug files saved in: {DEBUG_DIR.resolve()}\n")


if __name__ == "__main__":
    main()