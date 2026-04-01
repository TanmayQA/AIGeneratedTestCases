import re

CSV_COLUMNS = [
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

ALLOWED_PRIORITIES = {"P0", "P1", "P2"}
ALLOWED_AUTOMATION = {"Yes", "No"}
ALLOWED_EXECUTION_TEAMS = {"Mobile QA", "Web QA", "API QA", "Shared QA"}

ALLOWED_TYPES = {
    "Positive (UI)",
    "Negative (UI)",
    "Edge/Timeout (UI)",
    "State management (UI)",
    "Performance (UI)",
    "Integration (UI)",
    "API validation (Positive)",
    "API validation (Negative)",
    "Security (API)",
    "Security (UI)",
}


def fix_column_shift(row: dict) -> dict:
    row = dict(row)

    if row.get("Type") in {"Yes", "No"} and not row.get("Automation Candidate"):
        row["Automation Candidate"] = row["Type"]
        row["Type"] = "Positive (UI)"

    return row


def normalize_priority(value: str) -> str:
    v = (value or "").strip().upper()

    if v in ALLOWED_PRIORITIES:
        return v

    if v in {"HIGH", "H", "P"}:
        return "P1"
    if v in {"MEDIUM", "M"}:
        return "P2"
    if v in {"LOW", "L"}:
        return "P2"

    return "P1"


def normalize_automation(value: str) -> str:
    v = (value or "").strip().lower()

    if v in {"yes", "y", "true"}:
        return "Yes"
    if v in {"no", "n", "false"}:
        return "No"

    return "Yes"


def normalize_execution_team(value: str, row: dict) -> str:
    v = (value or "").strip()

    if v in ALLOWED_EXECUTION_TEAMS:
        return v

    scenario = row.get("Scenario", "").lower()
    type_val = row.get("Type", "").lower()
    steps = row.get("Steps", "").lower()

    if "api" in type_val or "/otp/" in steps or "/profile" in steps:
        return "API QA"
    if "web" in scenario:
        return "Web QA"
    if "ui" in type_val or "screen" in steps or "button" in steps or "input field" in steps:
        return "Mobile QA"

    return "Shared QA"


def normalize_type(value: str, row: dict) -> str:
    v = (value or "").strip()

    if v in ALLOWED_TYPES:
        return v

    lower_v = v.lower()
    scenario = row.get("Scenario", "").lower()
    steps = row.get("Steps", "").lower()

    is_api = "api" in lower_v or "/otp/" in steps or "/profile" in steps
    is_negative = "negative" in lower_v or "error" in scenario or "invalid" in scenario or "negative" in scenario
    is_timeout = "timeout" in lower_v or "expiry" in scenario or "expired" in scenario or "boundary" in scenario
    is_security = "security" in lower_v or "auth" in scenario or "token" in scenario

    if is_security and is_api:
        return "Security (API)"
    if is_security:
        return "Security (UI)"
    if is_timeout and not is_api:
        return "Edge/Timeout (UI)"
    if is_api and is_negative:
        return "API validation (Negative)"
    if is_api:
        return "API validation (Positive)"
    if is_negative:
        return "Negative (UI)"

    return "Positive (UI)"


def normalize_tags(value: str, row: dict) -> str:
    raw = (value or "").upper().replace(" ", "")
    parts = [p for p in raw.split(",") if p]

    if len(parts) == 3:
        return ",".join(parts)

    scenario = row.get("Scenario", "").lower()
    type_val = row.get("Type", "").lower()
    steps = row.get("Steps", "").lower()

    suite = "REGRESSION"

    if "security" in type_val or "token" in scenario or "auth" in scenario:
        layer = "API" if "api" in type_val or "/profile" in steps or "/otp/" in steps else "SECURITY"
        risk = "AUTH"
    elif "api" in type_val or "/otp/" in steps or "/profile" in steps:
        layer = "API"
        risk = "HIGH_RISK"
    elif "timeout" in type_val or "expired" in scenario or "rate" in scenario:
        layer = "NETWORK"
        risk = "HIGH_RISK"
    else:
        layer = "UI"
        risk = "P0_FLOW"

    return f"{suite},{layer},{risk}"


def clean_steps(value: str) -> str:
    v = (value or "").replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    v = v.replace("`", "").replace("<", "").replace(">", "")
    return " ".join(v.split())


def clean_expected_result(value: str) -> str:
    v = (value or "").replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    v = v.replace("`", "")
    return " ".join(v.split())


def normalize_test_data(value: str) -> str:
    v = (value or "").replace("`", "").strip()

    if not v or v == "-" or v.lower() == "none":
        return "-"

    v = v.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    v = re.sub(r"\(.*?\)", "", v)

    v = v.replace("Authorization: Bearer ", "token=")
    v = v.replace("Content-Type: application/json,", "")
    v = v.replace("Content-Type: application/json", "")

    v = v.replace(",", ";")
    v = v.replace(" ", "")

    pairs = re.findall(r"([A-Za-z_]+)=([^;]+)", v)

    cleaned = []
    for key, val in pairs:
        key = key.strip().lower()

        if key in {"mobile", "otp", "request_id", "token"}:
            if val.lower() in {"null", ""}:
                cleaned.append(f"{key}=")
            else:
                cleaned.append(f"{key}={val}")

    return ";".join(cleaned) if cleaned else "-"


def normalize_row(row: dict) -> dict:
    normalized = {col: str(row.get(col, "")).strip() for col in CSV_COLUMNS}
    normalized = fix_column_shift(normalized)

    normalized["Priority"] = normalize_priority(normalized["Priority"])
    normalized["Automation Candidate"] = normalize_automation(normalized["Automation Candidate"])
    normalized["Steps"] = clean_steps(normalized["Steps"])
    normalized["Expected Result"] = clean_expected_result(normalized["Expected Result"])
    normalized["Test Data"] = normalize_test_data(normalized["Test Data"])
    normalized["Type"] = normalize_type(normalized["Type"], normalized)
    normalized["Execution Team"] = normalize_execution_team(normalized["Execution Team"], normalized)
    normalized["Tags"] = normalize_tags(normalized["Tags"], normalized)

    if not normalized["Pre-Conditions"] or normalized["Pre-Conditions"].lower() in {"nan", "none", "-"}:
        normalized["Pre-Conditions"] = ""

    return normalized


def fix_expected_result(row):
    exp = str(row.get("Expected Result", "")).strip()

    if len(exp) < 15:
        scenario = str(row.get("Scenario", "")).lower()
        steps = str(row.get("Steps", "")).lower()
        status = ""

        if "200" in exp:
            if "otp" in scenario or "otp" in steps:
                status = "Verify response status is 200 and OTP is sent successfully to the registered mobile number and success confirmation is displayed on screen"
            elif "login" in scenario or "login" in steps:
                status = "Verify response status is 200 and user is logged in successfully with valid session created and redirected to dashboard"
            elif "profile" in scenario or "profile" in steps:
                status = "Verify response status is 200 and profile data is returned correctly with all expected fields populated"
            else:
                status = "Verify response status is 200 and success response is returned with expected payload and no error flags"
        elif "400" in exp:
            if "otp" in scenario or "otp" in steps:
                status = "Verify response status is 400 and error message 'Invalid OTP' is displayed and user remains on OTP screen without session creation"
            elif "mobile" in scenario or "mobile" in steps:
                status = "Verify response status is 400 and error message 'Invalid mobile number format' is displayed and form remains editable"
            else:
                status = "Verify response status is 400 and descriptive error message is displayed to user and no state mutation occurs"
        elif "401" in exp:
            if "token" in scenario or "token" in steps:
                status = "Verify response status is 401 and error message 'Unauthorized or expired token' is shown and user is redirected to login screen"
            else:
                status = "Verify response status is 401 and unauthorized access error is shown and active session is invalidated"
        elif "429" in exp:
            status = "Verify response status is 429 and rate limit error message is displayed and user is temporarily blocked from further attempts with cooldown timer shown"
        elif "500" in exp:
            status = "Verify response status is 500 and generic server error message is displayed to user without exposing internal details and retry option is available"
        elif "expired" in scenario or "expiry" in scenario:
            status = "Verify expired input is rejected with appropriate error message and user is prompted to request a new valid input without session creation"
        elif "invalid" in scenario or "negative" in scenario:
            status = "Verify invalid input is rejected with clear validation error message and system state remains unchanged"
        else:
            status = "Verify system returns expected response as per requirement with correct status code, appropriate user-facing message, and no unintended side effects"

        row["Expected Result"] = status

    return row


def normalize_rows(rows: list) -> list:
    return [normalize_row(row) for row in rows]


def drop_incomplete_rows(rows: list) -> list:
    cleaned = []

    for row in rows:
        scenario = str(row.get("Scenario", "")).strip()
        steps = str(row.get("Steps", "")).strip()
        expected = str(row.get("Expected Result", "")).strip()

        if not scenario or not steps or not expected:
            continue

        cleaned.append(row)

    return cleaned


def reassign_tc_ids(rows: list) -> list:
    for idx, row in enumerate(rows, start=1):
        row["TC_ID"] = f"TC-{idx:03d}"
    return rows


def validate_rows(rows: list) -> tuple[bool, str]:
    if not rows:
        return False, "No rows found"

    for i, row in enumerate(rows):
        for col in CSV_COLUMNS:
            if col not in row:
                return False, f"Row {i} missing column {col}"

        if not row["Requirement_ID"]:
            return False, f"Row {i} missing Requirement_ID"
        if not row["Scenario"]:
            return False, f"Row {i} missing Scenario"
        if not row["Expected Result"]:
            return False, f"Row {i} missing Expected Result"

    return True, ""