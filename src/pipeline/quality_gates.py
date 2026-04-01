from typing import List, Dict, Tuple
from collections import Counter

from src.pipeline.row_normalizer import reassign_tc_ids

REQUIRED_COLUMNS = [
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


def canonical_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def row_signature(row: Dict[str, str]) -> str:
    return (
        canonical_text(row.get("Requirement_ID", "")) +
        canonical_text(row.get("Scenario", "")) +
        canonical_text(row.get("Steps", "")) +
        canonical_text(row.get("Expected Result", ""))
    )


def remove_exact_and_semantic_duplicates(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    deduped = []

    for row in rows:
        sig = row_signature(row)
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(row)

    return deduped


def validate_required_columns(rows: List[Dict[str, str]]) -> Tuple[bool, str]:
    for i, row in enumerate(rows):
        for col in REQUIRED_COLUMNS:
            if col not in row:
                return False, f"Row {i} missing required column: {col}"
    return True, ""


def validate_tc_ids(rows: List[Dict[str, str]]) -> Tuple[bool, str]:
    seen = set()
    for i, row in enumerate(rows):
        tc_id = (row.get("TC_ID") or "").strip()
        if not tc_id:
            return False, f"Row {i} missing TC_ID"
        if tc_id in seen:
            return False, f"Duplicate TC_ID found: {tc_id}"
        seen.add(tc_id)
    return True, ""


def validate_requirement_ids(rows: List[Dict[str, str]], expected_req_ids: List[str]) -> Tuple[bool, str]:
    expected = set(expected_req_ids)
    found = set()

    for row in rows:
        reqs = [r.strip() for r in (row.get("Requirement_ID") or "").split(",") if r.strip()]
        for req in reqs:
            found.add(req)

    missing = sorted(expected - found)
    if missing:
        present = sorted(found)
        return False, (
            f"Missing Requirement_ID coverage. "
            f"Missing: {', '.join(missing)} "
            f"Present: {', '.join(present)}"
        )

    return True, ""


def validate_no_prose_pollution(rows: List[Dict[str, str]]) -> Tuple[bool, str]:
    bad_patterns = [
        "based on the provided",
        "here is the output",
        "i have removed",
        "i have added",
        "this table covers",
        "note that",
    ]

    for i, row in enumerate(rows):
        joined = " ".join(str(v) for v in row.values()).lower()
        for pattern in bad_patterns:
            if pattern in joined:
                return False, f"Prose pollution found in row {i}"
    return True, ""


def validate_minimum_quality(rows: List[Dict[str, str]]) -> Tuple[bool, str]:
    for i, row in enumerate(rows):
        if len((row.get("Scenario") or "").strip()) < 5:
            return False, f"Scenario too short in row {i}"

        if len((row.get("Steps") or "").strip()) < 5:
            return False, f"Steps too short in row {i}"

        if len((row.get("Expected Result") or "").strip()) < 5:
            return False, f"Expected Result too short in row {i}"

    return True, ""


def validate_distribution(rows: List[Dict[str, str]], expected_req_ids: List[str]) -> Tuple[bool, str]:
    counts = Counter()

    for row in rows:
        for req in row.get("Requirement_ID", "").split(","):
            req = req.strip()
            if req:
                counts[req] += 1

    total_rows = len(rows)
    total_reqs = len(expected_req_ids)

    if total_reqs == 0:
        return True, ""

    # Flexible threshold for small inputs
    if total_reqs <= 2 and total_rows <= 4:
        min_rows_per_req = 1
    elif total_reqs <= 3 and total_rows <= 6:
        min_rows_per_req = 1
    else:
        min_rows_per_req = 2

    weak = [req for req in expected_req_ids if counts[req] < min_rows_per_req]

    if weak:
        return False, (
            f"Poor distribution. Low coverage for: {', '.join(weak)} "
            f"(minimum required per Requirement_ID: {min_rows_per_req})"
        )

    return True, ""


def run_quality_gates(rows: List[Dict[str, str]], expected_req_ids: List[str]) -> Tuple[bool, str, List[Dict[str, str]]]:
    rows = remove_exact_and_semantic_duplicates(rows)

    # Never trust model-generated TC_ID values.
    rows = reassign_tc_ids(rows)

    checks = [
        validate_required_columns(rows),
        validate_tc_ids(rows),
        validate_requirement_ids(rows, expected_req_ids),
        validate_distribution(rows, expected_req_ids),
        validate_no_prose_pollution(rows),
        validate_minimum_quality(rows),
    ]

    for ok, msg in checks:
        if not ok:
            return False, msg, rows

    return True, "", rows