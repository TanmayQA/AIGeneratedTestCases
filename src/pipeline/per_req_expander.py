from src.pipeline.agent_runner import run_stage_with_retry

def reassign_markdown_tc_ids(table_text: str) -> str:
    lines = table_text.splitlines()
    if len(lines) < 3:
        return table_text

    fixed = lines[:2]  # header + separator
    counter = 1

    for line in lines[2:]:
        if not line.strip().startswith("|"):
            continue

        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 2:
            fixed.append(line)
            continue

        cols[1] = f"TC-{counter:03d}"
        counter += 1
        fixed.append("| " + " | ".join(cols) + " |")

    return "\n".join(fixed)

def extract_tables(text):
    lines = text.splitlines()
    tables = []
    current = []

    for line in lines:
        raw = line.rstrip()
        stripped = raw.strip()

        # skip markdown fences
        if stripped.startswith("```"):
            continue

        # accept normal markdown table rows
        if stripped.startswith("|") and stripped.endswith("|"):
            current.append(stripped)
            continue

        # flush current table on non-table line
        if current:
            tables.append("\n".join(current))
            current = []

    if current:
        tables.append("\n".join(current))

    return tables


def has_markdown_table(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pipe_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]
    return len(pipe_lines) >= 3


def expand_per_requirement(
    assets,
    rules,
    normalized,
    reader_output,
    expected_req_ids,
    template_text="",
    api_contract_text=""
):
    all_outputs = []

    for req_id in expected_req_ids:
        print(f"🔹 Expanding for {req_id}")

        focused_input = f"""
FOCUS REQUIREMENT:
{req_id}

FULL REQUIREMENT CONTEXT:
{reader_output}

IMPORTANT:
- Generate testcases ONLY for {req_id}
- Do NOT generate for other Requirement_IDs
- Ensure strong coverage for this requirement
"""

        generator_prompt = assets["generator"] + """

PER-REQUIREMENT DEEP COVERAGE MODE:

- Focus ONLY on the given Requirement_ID
- Read the requirement carefully and identify ALL distinct sub-behaviors, flows, and states it describes
- Generate a separate test case for EACH distinct sub-behavior — do NOT merge them
- Include:
  - Every positive flow and sub-flow explicitly mentioned
  - Every negative/error path explicitly mentioned
  - Every "must NOT" or "not shown" or "not functional" constraint → generate a negative test verifying it
  - Every conditional state (e.g. done/fail/in-progress states, toggle ON/OFF, with/without permission)
  - Every device/platform-specific interaction (camera, gallery, biometric, PIN, permission prompts)
  - Every persistence/lifecycle behavior (DataStore, app restart, background/foreground resume)
  - Edge cases and boundary conditions derived from the requirement
- Minimum TCs: number of distinct sub-behaviors in the requirement, with no upper cap
- Do NOT stop at 2–3 TCs if the requirement describes more behaviors than that
"""

        output = run_stage_with_retry(
            generator_prompt,
            rules,
            normalized,
            previous_output=focused_input,
            template_text=template_text,
            api_contract_text=api_contract_text,
        )

        if not has_markdown_table(output):
            print(f"⚠️ No markdown table for {req_id}. Retrying with stricter prompt...")

            retry_prompt = generator_prompt + """

STRICT RETRY:
- Return ONLY ONE markdown table
- Do NOT return prose
- Do NOT return bullets
- Do NOT return explanation
- First line must start with |
- Table must contain header + separator + at least 1 testcase row
"""

            output = run_stage_with_retry(
                retry_prompt,
                rules,
                normalized,
                previous_output=focused_input,
                template_text=template_text,
                api_contract_text=api_contract_text,
            )

        all_outputs.append(output)

    all_tables = []

    for output in all_outputs:
        tables = extract_tables(output)
        all_tables.extend(tables)

    print(f"Generated {len(all_tables)} tables, merged into one")

    clean_tables = []

    for table in all_tables:
        lines = table.splitlines()

        # basic validation
        if len(lines) < 3:
            continue

        header = lines[0]

        if "Requirement_ID" not in header:
            continue

        clean_tables.append(table)

    if not clean_tables:
        preview = "\n\n---\n\n".join(all_outputs[:2])
        raise Exception(f"No valid markdown tables found after cleaning. Preview:\n{preview[:1500]}")

    def safe_row(row, expected_cols):
        cols = row.strip("|").split("|")

        if len(cols) < expected_cols:
            # pad missing columns
            cols += [""] * (expected_cols - len(cols))
        elif len(cols) > expected_cols:
            # merge overflow into last column
            cols = cols[:expected_cols-1] + [" ".join(cols[expected_cols-1:])]

        return "| " + " | ".join(c.strip() for c in cols) + " |"

    merged_lines = clean_tables[0].splitlines()
    expected_cols = len(merged_lines[0].strip("|").split("|"))

    for table in clean_tables[1:]:
        lines = table.splitlines()

        for row in lines[2:]:  # skip header + separator
            if not row.strip().startswith("|"):
                continue

            fixed_row = safe_row(row, expected_cols)
            merged_lines.append(fixed_row)

    merged_table = "\n".join(merged_lines)
    merged_table = reassign_markdown_tc_ids(merged_table)
    return merged_table
