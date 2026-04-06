import re
from typing import Dict, List, Tuple, Optional

REQ_PATTERN = re.compile(r"REQ-\d+")
SCENARIO_BUCKETS = [
    "positive",
    "negative",
    "boundary",
    "edge",
    "invalid",
    "error",
    "retry",
    "resend",
    "timeout",
    "state",
    "security",
    "abuse",
    "api",
    "ui",
    "integration",
    "network",
    "exit_criteria",
    "removal",
    "analytics",
    "localization",
    "accessibility",
    "lifecycle",
    "dismissal",
]

BUCKET_PATTERNS = {
    "positive": [r"\bpositive\b", r"\bsuccess\b", r"\bvalid\b"],
    "negative": [r"\bnegative\b", r"\binvalid\b", r"\berror\b", r"\breject\b", r"\bfail\b"],
    "boundary": [r"\bboundary\b", r"\bmin\b", r"\bmax\b", r"\blimit\b", r"\blength\b"],
    "edge": [r"\bedge\b", r"\bcorner\b"],
    "invalid": [r"\binvalid\b", r"\bblank\b", r"\bnull\b", r"\bempty\b", r"\bwhitespace\b", r"\bformat\b"],
    "error": [r"\berror\b", r"\bfailure\b", r"\bexception\b"],
    "retry": [r"\bretry\b"],
    "resend": [r"\bresend\b"],
    "timeout": [r"\btimeout\b", r"\bexpired\b", r"\bexpiry\b"],
    "state": [r"\bstate\b", r"\bsession\b", r"\bnavigation\b", r"\btransition\b"],
    "security": [r"\bsecurity\b", r"\bbrute force\b", r"\breplay\b", r"\bauthorization\b", r"\brate limit\b"],
    "abuse": [r"\babuse\b", r"\bbrute force\b", r"\brate limit\b"],
    "api": [r"\bapi\b", r"\bstatus code\b", r"\bresponse\b", r"\bcontract\b"],
    "ui": [r"\bui\b", r"\bscreen\b", r"\bmessage\b", r"\bvalidation\b"],
    "integration": [r"\bintegration\b", r"\bdependency\b", r"\bservice\b", r"\bbackend\b"],
    "network": [r"\bnetwork\b", r"\boffline\b", r"\bslow\b", r"\bconnection\b"],
    "exit_criteria": [r"\bexit\b", r"\bdisappear\b", r"\bhidden\b", r"\bremoved when\b", r"\bnot (be )?shown\b", r"\bno longer (visible|displayed)\b"],
    "removal": [r"\bremoved\b", r"\bdeprecated\b", r"\babsent\b", r"\bnot present\b", r"\bshould not (appear|be visible|be shown)\b", r"\bno longer available\b"],
    "analytics": [r"\banalytics\b", r"\bevent\b", r"\btracked\b", r"\bfires\b", r"\bct event\b", r"\bproperty\b"],
    "localization": [r"\bhindi\b", r"\blocali[sz]ation\b", r"\blanguage\b", r"\btranslation\b", r"\bmulti.?language\b"],
    "accessibility": [r"\baccessib\w+\b", r"\bresource.?id\b", r"\bscreen.?reader\b", r"\bcontent.?description\b"],
    "lifecycle": [r"\brelaunch\b", r"\bapp.?kill\b", r"\bkill.?app\b", r"\bonce per session\b", r"\bonce in lifetime\b", r"\bapp.?restart\b", r"\bsession.?end\b"],
    "dismissal": [r"\bdismiss\b", r"\bclose.?(button|card|banner)\b", r"\bclosable\b", r"\buser.?clos\b"],
}


def extract_coverage_checklist_from_reader(reader_output: str) -> Dict[str, List[str]]:
    """
    Parse the structured sections written by the reader stage into a machine-readable checklist.
    Returns a dict with keys: entry_exit, lifecycle, removals, analytics, non_functional.
    Each value is a list of item strings that must be covered by test cases.
    """
    checklist: Dict[str, List[str]] = {
        "entry_exit": [],
        "lifecycle": [],
        "removals": [],
        "analytics": [],
        "non_functional": [],
    }

    section_patterns = {
        "entry_exit": re.compile(
            r"ENTRY\s*/\s*EXIT\s+CONDITIONS?:(.*?)(?=\nAPP LIFECYCLE|\nREMOVALS|\nANALYTICS|\nNON.FUNCTIONAL|\nKNOWN GAPS|\Z)",
            re.DOTALL | re.IGNORECASE,
        ),
        "lifecycle": re.compile(
            r"APP LIFECYCLE\s+CONDITIONS?:(.*?)(?=\nREMOVALS|\nANALYTICS|\nNON.FUNCTIONAL|\nKNOWN GAPS|\Z)",
            re.DOTALL | re.IGNORECASE,
        ),
        "removals": re.compile(
            r"REMOVALS.*?:(.*?)(?=\nANALYTICS|\nNON.FUNCTIONAL|\nKNOWN GAPS|\Z)",
            re.DOTALL | re.IGNORECASE,
        ),
        "analytics": re.compile(
            r"ANALYTICS\s+EVENTS?:(.*?)(?=\nNON.FUNCTIONAL|\nKNOWN GAPS|\Z)",
            re.DOTALL | re.IGNORECASE,
        ),
        "non_functional": re.compile(
            r"NON.FUNCTIONAL\s+REQUIREMENTS?:(.*?)(?=\nKNOWN GAPS|\Z)",
            re.DOTALL | re.IGNORECASE,
        ),
    }

    for key, pattern in section_patterns.items():
        match = pattern.search(reader_output)
        if not match:
            continue
        block = match.group(1).strip()
        items = []
        for line in block.splitlines():
            line = line.strip().lstrip("-").lstrip("*").strip()
            if line:
                items.append(line)
        checklist[key] = items

    return checklist


def check_checklist_coverage(
    checklist: Dict[str, List[str]],
    table_text: str,
) -> Dict[str, List[str]]:
    """
    For each item in the checklist, check whether at least one test case in the table
    appears to cover it (by keyword matching the item text against Scenario + Steps + Expected Result).
    Returns a dict of uncovered items per checklist category.
    """
    rows = parse_markdown_table_rows(table_text)
    if len(rows) < 2:
        return {k: list(v) for k, v in checklist.items()}

    header = rows[0]
    col_idx = {}
    for col in ["Scenario", "Steps", "Expected Result", "Tags", "Type"]:
        try:
            col_idx[col] = header.index(col)
        except ValueError:
            col_idx[col] = None

    def row_text(row: List[str]) -> str:
        parts = []
        for col in ["Scenario", "Steps", "Expected Result", "Tags", "Type"]:
            idx = col_idx.get(col)
            if idx is not None and len(row) > idx:
                parts.append(row[idx])
        return " ".join(parts).lower()

    all_tc_texts = [row_text(r) for r in rows[1:]]

    def _item_is_covered(item: str) -> bool:
        keywords = [w.lower() for w in re.split(r"\W+", item) if len(w) > 3]
        if not keywords:
            return True
        # require at least half the meaningful keywords to match at least one TC
        hits = sum(1 for kw in keywords if any(kw in tc for tc in all_tc_texts))
        return hits >= max(1, len(keywords) // 2)

    uncovered: Dict[str, List[str]] = {}

    for category, items in checklist.items():
        missing = [item for item in items if not _item_is_covered(item)]
        if missing:
            uncovered[category] = missing

    return uncovered


def extract_requirement_ids_from_reader(reader_output: str) -> List[str]:
    ids = REQ_PATTERN.findall(reader_output)
    unique_ids = []
    for rid in ids:
        if rid not in unique_ids:
            unique_ids.append(rid)
    return unique_ids


def parse_markdown_table_rows(table_text: str) -> List[List[str]]:
    rows = []
    for line in table_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.count("|") < 3:
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]

        if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
            continue

        rows.append(cells)

    return rows


def build_trace_matrix(table_text: str) -> Dict[str, List[str]]:
    rows = parse_markdown_table_rows(table_text)
    if len(rows) < 2:
        return {}

    header = rows[0]
    try:
        req_idx = header.index("Requirement_ID")
        tc_idx = header.index("TC_ID")
    except ValueError:
        return {}

    matrix: Dict[str, List[str]] = {}

    for row in rows[1:]:
        if len(row) <= max(req_idx, tc_idx):
            continue

        req_cell = row[req_idx]
        tc_id = row[tc_idx]

        req_ids = [x.strip() for x in req_cell.split(",") if x.strip()]
        for req_id in req_ids:
            if not REQ_PATTERN.fullmatch(req_id):
                continue
            matrix.setdefault(req_id, []).append(tc_id)

    return matrix


def build_requirement_bucket_matrix(table_text: str) -> Dict[str, Dict[str, int]]:
    rows = parse_markdown_table_rows(table_text)
    if len(rows) < 2:
        return {}

    header = rows[0]
    required_cols = ["Requirement_ID", "Scenario", "Type", "Steps", "Expected Result", "Tags"]
    idx = {}

    for col in required_cols:
        try:
            idx[col] = header.index(col)
        except ValueError:
            idx[col] = None

    bucket_matrix: Dict[str, Dict[str, int]] = {}

    for row in rows[1:]:
        req_cell = row[idx["Requirement_ID"]] if idx["Requirement_ID"] is not None and len(row) > idx["Requirement_ID"] else ""
        req_ids = [x.strip() for x in req_cell.split(",") if x.strip()]

        combined_text = " ".join([
            row[idx["Scenario"]] if idx["Scenario"] is not None and len(row) > idx["Scenario"] else "",
            row[idx["Type"]] if idx["Type"] is not None and len(row) > idx["Type"] else "",
            row[idx["Steps"]] if idx["Steps"] is not None and len(row) > idx["Steps"] else "",
            row[idx["Expected Result"]] if idx["Expected Result"] is not None and len(row) > idx["Expected Result"] else "",
            row[idx["Tags"]] if idx["Tags"] is not None and len(row) > idx["Tags"] else "",
        ]).lower()

        detected_buckets = detect_buckets(combined_text)

        for req_id in req_ids:
            if not REQ_PATTERN.fullmatch(req_id):
                continue
            bucket_matrix.setdefault(req_id, {})
            for bucket in detected_buckets:
                bucket_matrix[req_id][bucket] = bucket_matrix[req_id].get(bucket, 0) + 1

    return bucket_matrix


def detect_buckets(text: str) -> List[str]:
    found = []
    for bucket, patterns in BUCKET_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            found.append(bucket)
    return found


def find_missing_requirements(expected_req_ids: List[str], trace_matrix: Dict[str, List[str]]) -> List[str]:
    return [req_id for req_id in expected_req_ids if req_id not in trace_matrix or not trace_matrix[req_id]]


def find_weak_requirements(expected_req_ids: List[str], table_text: str) -> Dict[str, List[str]]:
    bucket_matrix = build_requirement_bucket_matrix(table_text)
    weak: Dict[str, List[str]] = {}

    core_buckets = ["positive", "negative"]

    # keep only one soft optional group
    optional_groups = [
        ["retry", "resend", "timeout"],
    ]

    MIN_ROWS_PER_REQ = 3
    MAX_ROWS_PER_REQ = 8

    for req_id in expected_req_ids:
        buckets = bucket_matrix.get(req_id, {})
        missing = []

        row_count = sum(buckets.values())

        for b in core_buckets:
            if buckets.get(b, 0) == 0:
                missing.append(b)

        for group in optional_groups:
            if not any(buckets.get(b, 0) > 0 for b in group):
                missing.append("/".join(group))

        if row_count < MIN_ROWS_PER_REQ:
            missing.append("insufficient_rows")

        if row_count >= MAX_ROWS_PER_REQ:
            continue

        if missing:
            weak[req_id] = missing

    return weak


def calculate_coverage_score(
    expected_req_ids: List[str],
    trace_matrix: Dict[str, List[str]],
    weak_requirements: Optional[Dict[str, List[str]]] = None,
) -> Tuple[int, int, float]:
    total = len(expected_req_ids)
    weak_requirements = weak_requirements or {}

    covered = 0
    for req_id in expected_req_ids:
        if req_id in trace_matrix and trace_matrix[req_id] and req_id not in weak_requirements:
            covered += 1

    percent = round((covered / total) * 100, 2) if total else 0.0
    return covered, total, percent


def build_gap_summary(
    expected_req_ids: List[str],
    trace_matrix: Dict[str, List[str]],
    table_text: str,
    checklist: Optional[Dict[str, List[str]]] = None,
) -> str:
    missing = find_missing_requirements(expected_req_ids, trace_matrix)
    weak = find_weak_requirements(expected_req_ids, table_text)

    lines = []
    lines.append("COVERAGE GAP SUMMARY")
    lines.append("====================")
    lines.append(f"Expected requirement IDs: {', '.join(expected_req_ids) if expected_req_ids else 'None found'}")
    lines.append("")

    if missing:
        lines.append("Missing requirement coverage:")
        for req_id in missing:
            lines.append(f"- {req_id}")
    else:
        lines.append("No fully missing requirement IDs.")

    lines.append("")

    if weak:
        lines.append("Partially covered requirement IDs and missing scenario dimensions:")
        for req_id, buckets in weak.items():
            lines.append(f"- {req_id}: missing {', '.join(buckets)}")
    else:
        lines.append("No partially covered requirement IDs.")

    if checklist:
        uncovered = check_checklist_coverage(checklist, table_text)
        if uncovered:
            lines.append("")
            lines.append("Checklist items not covered by any test case:")
            for category, items in uncovered.items():
                lines.append(f"  [{category.upper()}]")
                for item in items:
                    lines.append(f"  - {item}")

    return "\n".join(lines)