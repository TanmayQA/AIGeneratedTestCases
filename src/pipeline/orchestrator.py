from pathlib import Path
import json

from src.pipeline.agent_runner import run_stage_with_retry
from src.pipeline.prompt_loader import load_all_prompt_assets
from src.pipeline.requirement_normalizer import normalize_azure_work_item
from src.azure.azure_client import AzureDevOpsClient
from src.azure.azure_parser import extract_work_item_id
from src.models import NormalizedRequirement
from src.pipeline.coverage_utils import (
    extract_requirement_ids_from_reader,
    build_trace_matrix,
    calculate_coverage_score,
    build_gap_summary,
    find_weak_requirements,
)
from src.pipeline.table_parser import (
    table_to_json,
    ensure_no_prose_around_table,
    extract_first_markdown_table,
    extract_best_markdown_table,
)
from src.pipeline.row_normalizer import (
    normalize_rows,
    validate_rows,
    reassign_tc_ids,
    drop_incomplete_rows,
    fix_expected_result,
)
from src.pipeline.quality_gates import run_quality_gates
from src.pipeline.csv_writer import write_csv_output
from src.pipeline.per_req_expander import expand_per_requirement


def resolve_requirement(source, value):
    if source in {"azure_url", "azure_work_item_id"}:
        client = AzureDevOpsClient()
        work_item_id = extract_work_item_id(str(value))
        if not work_item_id:
            raise ValueError("Unable to extract a valid Azure work item ID.")

        work_item = client.get_work_item(work_item_id)

        if source == "azure_url":
            source_url = value
        else:
            source_url = client.build_work_item_url(work_item_id)

        return normalize_azure_work_item(work_item, source_url)

    return NormalizedRequirement(
        requirement_id="",
        title="Local Requirement",
        description=value,
        acceptance_criteria=value,
        repro_steps="",
        tags=[],
        source_url=None,
        source_type="text",
    )


def _normalize_final_rows(final_table_text: str):
    ensure_no_prose_around_table(final_table_text)
    final_data = table_to_json(final_table_text)
    final_data = normalize_rows(final_data)
    final_data = [fix_expected_result(r) for r in final_data]
    final_data = drop_incomplete_rows(final_data)
    final_data = reassign_tc_ids(final_data)
    return final_data


def _find_present_req_ids(table_text: str, expected_req_ids: list[str]) -> set[str]:
    present = set()
    for line in table_text.splitlines():
        for req in expected_req_ids:
            if req in line:
                present.add(req)
    return present


def _is_table_safe_to_replace(candidate_table: str, expected_req_ids: list[str]) -> tuple[bool, list[str]]:
    if not candidate_table.strip():
        return False, expected_req_ids

    present_req_ids = _find_present_req_ids(candidate_table, expected_req_ids)
    missing = sorted(set(expected_req_ids) - present_req_ids)

    if missing:
        return False, missing

    return True, []


def _assert_req_coverage_rows(rows: list[dict], expected_req_ids: list[str], stage: str):
    found = set()
    for row in rows:
        for req in str(row.get("Requirement_ID", "")).split(","):
            req = req.strip()
            if req:
                found.add(req)

    missing = sorted(set(expected_req_ids) - found)
    if missing:
        raise ValueError(f"{stage} dropped Requirement_IDs: {missing}")


def _safe_table_upgrade(current_table: str, candidate_table: str, expected_req_ids: list[str]) -> str:
    if not candidate_table.strip():
        return current_table

    safe, _ = _is_table_safe_to_replace(candidate_table, expected_req_ids)
    if not safe:
        return current_table

    try:
        current_rows = table_to_json(current_table)
        candidate_rows = table_to_json(candidate_table)
    except Exception:
        return current_table

    if len(candidate_rows) < max(1, int(len(current_rows) * 0.7)):
        return current_table

    return candidate_table


def _rows_to_markdown(rows: list[dict]) -> str:
    if not rows:
        return ""

    headers = list(rows[0].keys())

    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"

    lines = [header_line, separator]

    for row in rows:
        line = "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |"
        lines.append(line)

    return "\n".join(lines)


def apply_mode(prompt: str, mode: str, stage: str) -> str:
    """Return a safe copy of prompt with mode-specific addendum appended."""
    result = str(prompt)

    if mode == "exploratory":
        if stage == "generator":
            result += """

EXPLORATORY MODE (MANDATORY):

You MUST expand coverage across ALL Requirement_IDs evenly.

DISTRIBUTION RULE:
- Do NOT generate all cases for one Requirement_ID
- Ensure EACH Requirement_ID has multiple testcases (min 3–5 where applicable)

COVERAGE EXPANSION RULE:
For EACH Requirement_ID, generate additional cases for:
- blank input
- null input
- whitespace input
- boundary values
- malformed input
- invalid combinations
- state transitions
- retry/resend abuse
- rate limit abuse
- concurrency scenarios
- API failure (500)
- dependency failure
- security misuse
- replay attempts
- invalid token usage
- expired token usage
- missing fields
- invalid request_id / missing request_id

ANTI-DUPLICATION RULE:
- Each testcase must validate UNIQUE logic
- Do NOT repeat same steps with minor wording changes
- If logic is same → do NOT create another row

STRICT:
- Increase testcase count significantly
- Maintain schema correctness
- Maintain atomicity (one validation per row)
"""
        elif stage == "validator":
            result += """

EXPLORATORY MODE:
- Add broader missing coverage if logically applicable
- Be aggressive in expanding:
  - edge cases
  - abuse cases
  - invalid state cases
  - resilience/failure cases
- Do not reduce suite size unless exact duplicates exist
"""
    else:
        if stage == "generator":
            result += """

STRICT MODE:
- Prioritize deterministic, production-safe testcases
- Stay close to explicit requirement and contract
- Avoid speculative cases unless strongly supported
- Prefer cleaner, smaller, reliable suite over broad exploration
"""
        elif stage == "validator":
            result += """

STRICT MODE:
- Focus on schema correctness, dedupe, and requirement-backed coverage only
- Do not add speculative cases
- Keep output stable and production-ready
"""

    return result


def _dedupe_rows(rows: list[dict]) -> list[dict]:
    seen = set()
    deduped = []

    for row in rows:
        key = tuple(
            str(row.get(col, "")).strip().lower()
            for col in [
                "Requirement_ID",
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
        )
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    return deduped


def _run_finalizer_stage(
    assets: dict,
    normalized,
    rules_text: str,
    current_table_text: str,
    expected_req_ids: list[str],
    api_contract_text: str = "",
) -> tuple[str, list[dict]]:
    finalizer_prompt = str(assets["finalizer"]) + f"""

FINAL TRACEABILITY CHECK:

Expected Requirement_IDs:
{', '.join(expected_req_ids)}

MANDATORY:
- Keep all Requirement_IDs above in final output
- Do not invent new Requirement_IDs
- Return ONE complete markdown table only
"""

    raw_finalizer = run_stage_with_retry(
        finalizer_prompt,
        rules_text,
        normalized,
        previous_output=current_table_text,
        template_text="",
        api_contract_text=api_contract_text,
    )

    finalizer_table = extract_best_markdown_table(raw_finalizer, expected_req_ids)
    if not finalizer_table.strip():
        return current_table_text, _normalize_final_rows(current_table_text)

    safe, dropped = _is_table_safe_to_replace(finalizer_table, expected_req_ids)
    if not safe:
        print(f"⚠️ Finalizer dropped REQs: {dropped}. Keeping previous table.")
        return current_table_text, _normalize_final_rows(current_table_text)

    candidate_rows = _normalize_final_rows(finalizer_table)
    candidate_rows = _dedupe_rows(candidate_rows)
    candidate_rows = [fix_expected_result(r) for r in candidate_rows]
    candidate_rows = drop_incomplete_rows(candidate_rows)
    candidate_rows = reassign_tc_ids(candidate_rows)

    _assert_req_coverage_rows(candidate_rows, expected_req_ids, "finalizer")

    return _rows_to_markdown(candidate_rows), candidate_rows


def execute_pipeline(source, value, progress_callback=None, mode_variant=None):
    from src.config import Settings

    active_mode_variant = mode_variant or Settings.MODE_VARIANT
    assets = load_all_prompt_assets()
    normalized = resolve_requirement(source, value)

    def tick(msg):
        if progress_callback:
            progress_callback(msg)

    tick("reader")
    reader = run_stage_with_retry(
        assets["azure_requirement_reader"],
        assets["rules"],
        normalized,
        template_text="",
        api_contract_text=assets.get("api_contract", ""),
    )
    print("READER OUTPUT:\n", reader)

    expected_req_ids = extract_requirement_ids_from_reader(reader)
    if not expected_req_ids:
        raise Exception("No Requirement_IDs extracted from reader output")

    tick("generator")
    generator_prompt = apply_mode(assets["generator"], active_mode_variant, "generator")

    if active_mode_variant == "exploratory":
        raw_generator = expand_per_requirement(
            assets,
            assets["rules"],
            normalized,
            reader,
            expected_req_ids,
            template_text="",
            api_contract_text=assets.get("api_contract", ""),
        )
    else:
        raw_generator = run_stage_with_retry(
            generator_prompt,
            assets["rules"],
            normalized,
            previous_output=reader,
            template_text="",
            api_contract_text=assets.get("api_contract", ""),
        )

    generator = extract_best_markdown_table(raw_generator, expected_req_ids)
    if not generator.strip():
        raise Exception("No valid markdown table extracted from generator")

    final_table_text = generator
    final_data = _normalize_final_rows(final_table_text)
    final_source = "generator"

    try:
        _assert_req_coverage_rows(final_data, expected_req_ids, "generator")
    except ValueError as e:
        print(f"⚠️ {e}. Retrying generator once with strict traceability recovery...")

        generator_retry_prompt = generator_prompt + f"""

STRICT TRACEABILITY RECOVERY:

Expected Requirement_IDs:
{', '.join(expected_req_ids)}

MANDATORY:
- Every testcase row MUST contain a valid Requirement_ID from the list above
- Do NOT invent new Requirement_IDs
- Do NOT leave Requirement_ID blank
- Return ONE complete markdown table only
- Preserve full coverage across all Requirement_IDs
"""

        raw_generator_retry = run_stage_with_retry(
            generator_retry_prompt,
            assets["rules"],
            normalized,
            previous_output=reader,
            template_text="",
            api_contract_text=assets.get("api_contract", ""),
        )

        generator_retry = extract_best_markdown_table(raw_generator_retry, expected_req_ids)
        if not generator_retry.strip():
            raise Exception("No valid markdown table extracted from generator retry")

        retry_data = _normalize_final_rows(generator_retry)
        _assert_req_coverage_rows(retry_data, expected_req_ids, "generator_retry")

        generator = generator_retry
        final_table_text = generator_retry
        final_data = retry_data

    tick("validator")
    validator_prompt = apply_mode(assets["validator"], active_mode_variant, "validator")

    raw_validator = run_stage_with_retry(
        validator_prompt,
        assets["rules"],
        normalized,
        previous_output=generator,
        template_text="",
        api_contract_text=assets.get("api_contract", ""),
    )

    validator = extract_best_markdown_table(raw_validator, expected_req_ids)

    if validator.strip():
        safe, dropped = _is_table_safe_to_replace(validator, expected_req_ids)
        if safe:
            candidate_table = _safe_table_upgrade(final_table_text, validator, expected_req_ids)
            candidate_data = _normalize_final_rows(candidate_table)
            _assert_req_coverage_rows(candidate_data, expected_req_ids, "validator")
            final_table_text = candidate_table
            final_data = candidate_data
            final_source = "validator"
        else:
            print(f"⚠️ Validator dropped REQs: {dropped}. Keeping generator output.")
    else:
        print("⚠️ Validator returned no usable table. Keeping generator output.")

    present_req_ids = _find_present_req_ids(final_table_text, expected_req_ids)
    missing_req_ids = sorted(set(expected_req_ids) - present_req_ids)

    if missing_req_ids:
        print(f"⚠️ Missing REQs after validator: {missing_req_ids}. Retrying validator once...")

        validator_retry_prompt = validator_prompt + f"""

STRICT TRACEABILITY RECOVERY:

Missing Requirement_IDs:
{', '.join(missing_req_ids)}

You MUST add testcase rows for the missing Requirement_IDs above.
Return the FULL corrected markdown table.
Preserve all existing valid rows.
Do NOT return partial output.
"""

        raw_validator_retry = run_stage_with_retry(
            validator_retry_prompt,
            assets["rules"],
            normalized,
            previous_output=final_table_text,
            template_text="",
            api_contract_text=assets.get("api_contract", ""),
        )

        validator_retry = extract_best_markdown_table(raw_validator_retry, expected_req_ids)
        if validator_retry.strip():
            safe, dropped = _is_table_safe_to_replace(validator_retry, expected_req_ids)
            if safe:
                candidate_table = _safe_table_upgrade(final_table_text, validator_retry, expected_req_ids)
                candidate_data = _normalize_final_rows(candidate_table)
                _assert_req_coverage_rows(candidate_data, expected_req_ids, "validator_retry")
                final_table_text = candidate_table
                final_data = candidate_data
                validator = validator_retry
            else:
                print(f"⚠️ Validator retry dropped REQs: {dropped}. Keeping previous table.")

    tick("post_processing")
    final_data = _normalize_final_rows(final_table_text)
    _assert_req_coverage_rows(final_data, expected_req_ids, "post_processing")

    valid, errors = validate_rows(final_data)
    if not valid:
        raise Exception(f"Validator output failed normalization checks: {errors}")

    weak_reqs = find_weak_requirements(expected_req_ids, final_table_text)

    if weak_reqs:
        print(f"⚠️ Weak coverage detected for: {weak_reqs}. Running coverage repair...")

        weak_req_list = list(weak_reqs.keys()) if isinstance(weak_reqs, dict) else list(weak_reqs)

        coverage_prompt = str(assets["coverage_regenerator"]) + f"""

STRICT COVERAGE REPAIR:

Weak Requirement_IDs:
{', '.join(weak_req_list)}

You MUST:
- Add missing testcase rows ONLY for the weak Requirement_IDs above
- Ensure EACH weak Requirement_ID ends with at least 3 meaningful and distinct testcases
- Prioritize weak Requirement_IDs before adding anything else
- Do NOT add more rows for already-strong Requirement_IDs
- Return ONLY NEW testcase rows as a markdown table with the same header
- Do NOT repeat existing rows
- Do NOT rewrite the full suite

MANDATORY DISTRIBUTION RULE:
- If REQ-002 is weak, add rows for REQ-002 only until it has enough coverage
- Do not stop with only 1 testcase for any weak Requirement_ID
"""

        raw_coverage = run_stage_with_retry(
            coverage_prompt,
            assets["rules"],
            normalized,
            previous_output=final_table_text,
            template_text="",
            api_contract_text=assets.get("api_contract", ""),
        )

        repair_table = extract_best_markdown_table(raw_coverage, list(weak_reqs.keys()) if isinstance(weak_reqs, dict) else list(weak_reqs))
        if repair_table.strip():
            repair_rows = _normalize_final_rows(repair_table)
            final_rows = list(final_data)
            final_rows.extend(repair_rows)
            final_rows = normalize_rows(final_rows)
            final_rows = [fix_expected_result(r) for r in final_rows]
            final_rows = drop_incomplete_rows(final_rows)
            final_rows = reassign_tc_ids(final_rows)

            _assert_req_coverage_rows(final_rows, expected_req_ids, "coverage_merge")

            final_data = final_rows
        else:
            print("⚠️ Coverage repair returned no usable table. Keeping previous table.")

    final_table_for_distribution = _rows_to_markdown(final_data)
    weak_reqs_after_repair = find_weak_requirements(expected_req_ids, final_table_for_distribution)

    if weak_reqs_after_repair:
        print(f"⚠️ Still weak after repair: {weak_reqs_after_repair}")

    tick("finalizer")
    prev_table = _rows_to_markdown(final_data)
    final_table_text, final_data = _run_finalizer_stage(
        assets=assets,
        normalized=normalized,
        rules_text=assets["rules"],
        current_table_text=prev_table,
        expected_req_ids=expected_req_ids,
        api_contract_text=assets.get("api_contract", ""),
    )
    if final_table_text.strip() != prev_table.strip():
        final_source = "finalizer"

    _assert_req_coverage_rows(final_data, expected_req_ids, "before_final_gates")

    gates_ok, gate_error, final_data = run_quality_gates(
        final_data,
        expected_req_ids=expected_req_ids,
    )
    if not gates_ok:
        raise Exception(f"Final quality gates failed: {gate_error}")

    validator_table_for_metrics = validator if validator.strip() else generator

    trace_matrix_before = build_trace_matrix(validator_table_for_metrics)
    weak_before = find_weak_requirements(expected_req_ids, validator_table_for_metrics)
    covered_before, total_before, score_before = calculate_coverage_score(
        expected_req_ids,
        trace_matrix_before,
        weak_before,
    )
    gap_summary = build_gap_summary(expected_req_ids, trace_matrix_before, validator_table_for_metrics)

    final_table_for_metrics = _rows_to_markdown(final_data)
    trace_matrix_after = build_trace_matrix(final_table_for_metrics)
    weak_after = find_weak_requirements(expected_req_ids, final_table_for_metrics)
    covered_after, total_after, score_after = calculate_coverage_score(
        expected_req_ids,
        trace_matrix_after,
        weak_after,
    )

    Path("output").mkdir(exist_ok=True)

    csv_path = "output/final_test_cases.csv"
    json_path = "output/latest_run.json"
    trace_path = "output/trace_matrix.json"
    coverage_path = "output/coverage_summary.json"

    write_csv_output(final_data, csv_path)
    csv_output = Path(csv_path).read_text(encoding="utf-8")


    run_payload = {
        "normalized": normalized.model_dump(),
        "mode_variant": active_mode_variant,
        "stage_outputs": {
            "reader": reader,
            "generator": generator,
            "validator": validator,
            "final_source": final_source,
        },
        "final_rows": final_data,
    }
    Path(json_path).write_text(json.dumps(run_payload, indent=2), encoding="utf-8")
    Path(trace_path).write_text(json.dumps(trace_matrix_after, indent=2), encoding="utf-8")

    coverage_payload = {
        "expected_requirement_ids": expected_req_ids,
        "before": {
            "covered": covered_before,
            "total": total_before,
            "score_percent": score_before,
            "trace_matrix": trace_matrix_before,
            "weak_requirements": weak_before,
            "gap_summary": gap_summary,
        },
        "after": {
            "covered": covered_after,
            "total": total_after,
            "score_percent": score_after,
            "trace_matrix": trace_matrix_after,
            "weak_requirements": weak_after,
        },
    }
    Path(coverage_path).write_text(json.dumps(coverage_payload, indent=2), encoding="utf-8")

    return {
        "final_csv_text": csv_output,
        "csv_path": csv_path,
        "json_path": json_path,
        "trace_path": trace_path,
        "coverage_path": coverage_path,
        "coverage_score_before": score_before,
        "coverage_score_after": score_after,
        "expected_req_ids": expected_req_ids,
        "mode_variant": active_mode_variant,
        "trace_matrix": trace_matrix_after,
        "stage_outputs": {
            "reader": reader,
            "generator": generator,
            "validator": validator,
            "final_source": final_source,
        },
        "suite_files": {},
    }