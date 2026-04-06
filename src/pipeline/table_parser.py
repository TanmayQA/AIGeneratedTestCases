import csv
import io


EXPECTED_HEADERS = [
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
    "Dependency_Type",
    "Device_Sensitivity",
    "Network_Sensitivity",
    "Backend_Service",
    "Persona_Scenario",
    "Status",
]


def extract_first_markdown_table(text: str) -> str:
    lines = text.splitlines()
    table_lines = []
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            in_table = True
            table_lines.append(stripped)
        elif in_table:
            break

    return "\n".join(table_lines).strip()


def extract_all_markdown_tables(text: str) -> list[str]:
    lines = text.splitlines()
    tables = []
    current = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            current.append(stripped)
        else:
            if current:
                tables.append("\n".join(current).strip())
                current = []

    if current:
        tables.append("\n".join(current).strip())

    return [t for t in tables if t.strip()]


def extract_best_markdown_table(text: str, expected_req_ids: list[str]) -> str:
    tables = extract_all_markdown_tables(text)
    if not tables:
        return ""

    def score(table: str):
        present = set()
        for req in expected_req_ids:
            if req in table:
                present.add(req)

        lines = [l for l in table.splitlines() if l.strip().startswith("|")]
        row_count = max(0, len(lines) - 2)
        return (len(present), row_count)

    tables.sort(key=score, reverse=True)
    return tables[0]


def ensure_no_prose_around_table(table_text: str):
    if not table_text.strip():
        raise ValueError("No markdown table found in output")

    lines = [line.strip() for line in table_text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Markdown table is empty")

    for line in lines:
        if not (line.startswith("|") and "|" in line[1:]):
            raise ValueError("Prose detected outside markdown table")


def table_to_json(table_text: str):
    ensure_no_prose_around_table(table_text)

    lines = [line.strip() for line in table_text.splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("Markdown table must contain header and separator")

    reader = csv.reader(io.StringIO("\n".join(lines)), delimiter="|")
    parsed = []

    for row in reader:
        cleaned = [cell.strip() for cell in row]
        if cleaned and cleaned[0] == "":
            cleaned = cleaned[1:]
        if cleaned and cleaned[-1] == "":
            cleaned = cleaned[:-1]
        parsed.append(cleaned)

    header = parsed[0]
    if header != EXPECTED_HEADERS:
        raise ValueError(f"Header mismatch. Expected {EXPECTED_HEADERS}, got {header}")

    data_rows = []
    for row in parsed[2:]:
        if len(row) != len(EXPECTED_HEADERS):
            continue
        data_rows.append(dict(zip(EXPECTED_HEADERS, row)))

    return data_rows