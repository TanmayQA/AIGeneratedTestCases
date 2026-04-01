from pathlib import Path


def load_text_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return file_path.read_text(encoding="utf-8")


def load_skill(skill_file_name: str) -> str:
    return load_text_file(f"src/skills/{skill_file_name}.md")


def load_rules() -> str:
    rules_dir = Path("rules")
    if not rules_dir.exists():
        return ""

    preferred_rule_order = [
        "01-requirement-analysis.md",
        "02-test-planning.md",
        "03-test-design.md",
        "04-test-execution-assertion.md",
        "05-test-closure-formatting.md",
        "qa-rules.md",
    ]

    rule_texts = []
    for rule_file in preferred_rule_order:
        rule_path = rules_dir / rule_file
        if rule_path.exists():
            rule_texts.append(rule_path.read_text(encoding="utf-8"))

    return "\n\n".join(rule_texts)


def load_api_contract_if_exists() -> str:
    contract_path = Path("input/api-contract.txt")
    if contract_path.exists():
        return contract_path.read_text(encoding="utf-8")
    return ""


def load_all_prompt_assets() -> dict:
    return {
        "azure_requirement_reader": load_skill("azure-requirement-reader"),
        "generator": load_skill("generator"),
        "validator": load_skill("validator"),
        "coverage_regenerator": load_skill("coverage_regenerator"),
        "csv_exporter": load_skill("csv-exporter"),
        "qa_auditor": load_skill("qa-auditor"),
        "finalizer": load_skill("finalizer"),
        "rules": load_rules(),
        "api_contract": load_api_contract_if_exists(),
    }