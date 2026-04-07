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
    "Dependency_Type",
    "Device_Sensitivity",
    "Network_Sensitivity",
    "Backend_Service",
    "Persona_Scenario",
    "Status",
]

ALLOWED_PRIORITIES = {"P0", "P1", "P2"}
ALLOWED_AUTOMATION = {"Yes", "No"}
ALLOWED_EXECUTION_TEAMS = {"Mobile QA", "Web QA", "API QA", "Shared QA"}
ALLOWED_DEPENDENCY_TYPES = {"Live API", "Stub", "None"}
ALLOWED_SENSITIVITIES = {"High", "Medium", "Low"}
ALLOWED_STATUSES = {"DRAFT", "NEEDS_REFINEMENT", "APPROVED"}

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

# Patterns that indicate a fabricated test value in Expected Result (name, initials, phone)
_ER_SPECIFIC_VALUE_PATTERNS = [
    re.compile(r"'[A-Z][a-z]+\s[A-Z][a-z]+'"),   # 'First Last' name
    re.compile(r"'[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+'"),  # 'First Mid Last'
    re.compile(r"'\d{10}'"),                        # '9876543210' phone
    re.compile(r"'[A-Z]{2}'"),                      # 'JD' initials
    re.compile(r"'[A-Z]{3}'"),                      # 'ABC' 3-char initials
]


def _has_fabricated_value_in_er(row: dict) -> bool:
    """Return True when Expected Result has a specific fabricated test value but Test Data is empty."""
    test_data = row.get("Test Data", "").strip()
    if test_data and test_data not in {"-", ""}:
        return False  # Test Data provided — no issue
    er = row.get("Expected Result", "")
    return any(p.search(er) for p in _ER_SPECIFIC_VALUE_PATTERNS)


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
    scenario = row.get("Scenario", "").lower()
    steps = row.get("Steps", "").lower()

    # Override Performance (UI) when it is misused for UI responsiveness/tap checks.
    # Performance (UI) is reserved for actual load/throughput/latency benchmarks.
    if v == "Performance (UI)":
        is_real_performance = any(k in scenario or k in steps for k in [
            "load time", "render time", "fps", "throughput", "latency",
            "benchmark", "memory usage", "cpu usage",
        ])
        if not is_real_performance:
            v = ""  # Fall through to inference below

    if v in ALLOWED_TYPES:
        return v

    lower_v = v.lower()

    is_api = "api" in lower_v or "/otp/" in steps or "/profile" in steps
    is_negative = "negative" in lower_v or "error" in scenario or "invalid" in scenario or "negative" in scenario
    is_timeout = (
        "timeout" in lower_v or "expiry" in scenario or "expired" in scenario or "boundary" in scenario
        or "slow network" in steps or "slow network" in scenario
        or "slow connection" in steps or "slow connection" in scenario
        or "2g" in steps or "2g" in scenario
        or "degraded" in steps or "degraded" in scenario
        or "low-end" in steps or "low-end" in scenario
    )
    is_security = "security" in lower_v or "auth" in scenario or "token" in scenario
    is_state = (
        "state management" in lower_v
        or "no restart" in steps or "no restart" in scenario
        or "without restart" in steps or "without restart" in scenario
        or "applies immediately" in steps or "applies immediately" in scenario
        or "persists" in steps or "persist" in scenario
        or ("kill" in steps and "relaunch" in steps)
    )

    if is_security and is_api:
        return "Security (API)"
    if is_security:
        return "Security (UI)"
    if is_timeout and not is_api:
        return "Edge/Timeout (UI)"
    if is_state and not is_api and not is_negative:
        return "State management (UI)"
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


def normalize_dependency_type(value: str, row: dict) -> str:
    steps = (row.get("Steps", "") + " " + row.get("Expected Result", "") + " " + row.get("Scenario", "")).lower()
    pre = row.get("Pre-Conditions", "").lower()
    combined = steps + " " + pre

    # ── Override rules applied BEFORE trusting any LLM-provided value ──────

    # Rule 1: Always-visible spec-mandated UI elements have no backend dependency
    is_always_visible = (
        "always visible" in combined or "always displayed" in combined or "always shown" in combined
    )
    if is_always_visible:
        return "None"

    # Rule 2: Stub context keywords → force Stub regardless of what LLM set
    stub_keywords = [
        "dummy", "static", "hardcoded", "no api call", "visual only", "sprint 1", "stub", "mock",
        "no real api", "no network call", "no server call", "deferred", "placeholder",
        "is not made", "no network", "no api", "visual-only",
    ]
    if any(k in combined for k in stub_keywords):
        return "Stub"

    # Rule 3: DataStore persistence (kill/relaunch) without live API context → Stub
    is_datastore_persist = (
        ("datastore" in combined or "sharedpreferences" in combined or "persists after" in combined)
        or ("kill" in combined and "relaunch" in combined)
    )
    live_api_evidence = [
        "upload", "get user profile", "jiocloud", "backend", "/api/", "rest api",
        "401", "500 internal", "200 ok", "http response",
    ]
    is_live_api_context = any(k in combined for k in live_api_evidence)

    if is_datastore_persist and not is_live_api_context:
        return "Stub"

    # ── Trust LLM value if it passed all override rules ─────────────────────
    v = (value or "").strip()
    if v in ALLOWED_DEPENDENCY_TYPES:
        return v

    # ── Keyword-based inference for unset/invalid values ────────────────────
    api_keywords = [
        "upload", "get user profile", "jiocloud", "backend", "http", "response", "endpoint",
        "/api/", "rest api", "live api",
    ]
    if is_live_api_context or any(k in combined for k in api_keywords):
        return "Live API"

    return "None"


def normalize_device_sensitivity(value: str, row: dict) -> str:
    v = (value or "").strip()
    if v in ALLOWED_SENSITIVITIES:
        return v

    combined = (row.get("Steps", "") + " " + row.get("Scenario", "") + " " + row.get("Pre-Conditions", "")).lower()

    high_keywords = [
        "camera", "biometric", "fingerprint", "face recognition", "biometricprompt", "localauthentication",
        "pin", "read_media_images", "2 gb ram", "low-end", "ram", "anr", "notification",
    ]
    medium_keywords = [
        "permission", "background", "foreground", "app kill", "relaunch", "android", "ios",
        "datastore", "sharedpreferences",
    ]

    if any(k in combined for k in high_keywords):
        return "High"
    if any(k in combined for k in medium_keywords):
        return "Medium"
    return "Low"


def normalize_network_sensitivity(value: str, row: dict) -> str:
    v = (value or "").strip()
    if v in ALLOWED_SENSITIVITIES:
        return v

    dep_type = row.get("Dependency_Type", "")

    if dep_type == "Stub":
        return "Low"
    if dep_type == "None":
        return "Low"
    if dep_type == "Live API":
        return "High"

    combined = (row.get("Steps", "") + " " + row.get("Expected Result", "") + " " + row.get("Scenario", "")).lower()
    high_keywords = ["upload", "http", "2g", "slow network", "endpoint", "server error", "live api"]
    if any(k in combined for k in high_keywords):
        return "High"

    return "Low"


def normalize_backend_service(value: str, row: dict) -> str:
    dep_type = row.get("Dependency_Type", "")

    # Stub and None TCs have no live backend service — always "-"
    if dep_type in {"Stub", "None"}:
        return "-"

    v = (value or "").strip()
    if v and v not in {"-", "None", "none", ""}:
        return v

    combined = (row.get("Steps", "") + " " + row.get("Expected Result", "") + " " + row.get("Scenario", "")).lower()

    if "get user profile" in combined:
        return "Get User Profile API"
    if "jiocloud upload" in combined or "upload api" in combined:
        return "JioCloud Upload API"
    if "backup api" in combined:
        return "Backup API"
    if "storage quota" in combined:
        return "Storage Quota API"
    if "family hub api" in combined:
        return "Family Hub API"
    if "jiocare" in combined:
        return "JioCare"

    return "-"


def normalize_persona_scenario(value: str, row: dict) -> str:
    v = (value or "").strip()
    if v and v not in {"-", "None", "none", ""}:
        return v

    combined = (row.get("Scenario", "") + " " + row.get("Steps", "")).lower()

    if any(k in combined for k in ["hindi", "language", "localization"]):
        return "Hindi-speaking user"
    if any(k in combined for k in ["biometric", "app lock", "pin", "privacy", "security"]):
        return "Security-conscious user"
    if any(k in combined for k in ["2g", "slow network", "low-end", "2 gb"]):
        return "User on low-end or slow-network device"
    if any(k in combined for k in ["permission denied", "deny"]):
        return "Privacy-conscious user"
    if any(k in combined for k in ["new user", "first time", "onboard"]):
        return "New user"
    if any(k in combined for k in ["delete account", "log out"]):
        return "User exiting the app"

    return "Standard user"


def normalize_status(value: str, row: dict) -> str:
    """
    ALWAYS validates Expected Result quality regardless of what the LLM set.
    The LLM universally sets DRAFT — we must override when the ER is actually vague.
    """
    expected = row.get("Expected Result", "")
    steps = row.get("Steps", "")
    exp_lower = expected.lower()

    # ── Quality checks run unconditionally ──────────────────────────────────

    vague_phrases = [
        "as expected", "should work", "if applicable", "as designed", "per requirement",
        "expected behavior", "works correctly", "functions as intended",
        "appropriate", "appropriately", "correctly displays", "displays correctly",
        "properly", "gracefully", "works properly",
        "as per design", "as per spec", "per spec", "may vary", "or equivalent",
        "if it works", "works fine", "functions correctly", "behaves correctly",
        "handled correctly", "handled properly", "shown correctly", "renders correctly",
    ]
    if any(p in exp_lower for p in vague_phrases):
        return "NEEDS_REFINEMENT"

    # Non-deterministic two-outcome Expected Results
    if " either " in exp_lower or exp_lower.startswith("either "):
        return "NEEDS_REFINEMENT"

    # Too short to be a real Expected Result
    if len(expected.strip()) < 20 or len(steps.strip()) < 20:
        return "NEEDS_REFINEMENT"

    # Fabricated test values (names/initials/phone) in ER without Test Data
    if _has_fabricated_value_in_er(row):
        return "NEEDS_REFINEMENT"

    # ── Trust LLM value after passing all checks ────────────────────────────
    v = (value or "").strip().upper()
    if v in ALLOWED_STATUSES:
        return v

    return "DRAFT"


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
    v = " ".join(v.split())

    # Preserve ALL key=value pairs (not just whitelisted keys)
    pairs = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+)", v)
    if pairs:
        cleaned = []
        for key, val in pairs:
            key = key.strip().lower()
            val = val.strip()
            if key and val and val.lower() not in {"null", ""}:
                cleaned.append(f"{key}={val}")
        if cleaned:
            return ";".join(cleaned)

    # Not key=value format — return as-is if meaningful
    v = v.strip()
    if len(v) > 2 and v != "-":
        return v

    return "-"


def clean_steps(value: str) -> str:
    v = (value or "").replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    v = v.replace("`", "").replace("<", "").replace(">", "")
    return " ".join(v.split())


def clean_expected_result(value: str) -> str:
    v = (value or "").replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    v = v.replace("`", "")
    return " ".join(v.split())


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

    # Metadata columns — override rules run first, then trust LLM, then infer
    normalized["Dependency_Type"] = normalize_dependency_type(normalized["Dependency_Type"], normalized)
    normalized["Device_Sensitivity"] = normalize_device_sensitivity(normalized["Device_Sensitivity"], normalized)
    normalized["Network_Sensitivity"] = normalize_network_sensitivity(normalized["Network_Sensitivity"], normalized)
    normalized["Backend_Service"] = normalize_backend_service(normalized["Backend_Service"], normalized)
    normalized["Persona_Scenario"] = normalize_persona_scenario(normalized["Persona_Scenario"], normalized)
    # Status runs last — needs final ER and Test Data values
    normalized["Status"] = normalize_status(normalized["Status"], normalized)

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


def validate_rows(rows: list) -> tuple:
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
