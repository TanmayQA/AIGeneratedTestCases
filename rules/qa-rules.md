QA RULES – STRICT EXECUTION

==================================================
1. CORE COVERAGE

- Cover:
  - Positive
  - Negative
  - Boundary
  - Edge cases
  - Blank / null / whitespace
  - State transitions
  - Failure scenarios
  - UI + API + Integration layers when applicable
- Every requirement must be covered

==================================================
1A. CONDITIONAL VISIBILITY COVERAGE (UI CARDS / SECTIONS)

For any section, card, or widget with conditional visibility rules:
- ENTRY CRITERIA: Test that it appears when its entry condition is satisfied
- EXIT CRITERIA: Test that it disappears when its exit condition is satisfied
- TRANSITION: Test that the correct replacement card/section appears after exit
- USER DISMISSAL: Test close/dismiss action if "Closable by user: Yes"
- APP LIFECYCLE: Test behavior on app kill/relaunch if state resets
- SESSION BEHAVIOR: Test "once per session" or "once in lifetime" guards

These are NOT optional — missing any of them is a coverage gap.

==================================================
1B. FEATURE REMOVAL COVERAGE

When a release removes or deprecates features:
- Generate a NEGATIVE test for each removed item verifying it does NOT appear
- These must be P0 for core features, P1 for secondary features
- Scenario format: "Verify <removed feature> is absent from <screen>"

==================================================
1C. ANALYTICS EVENT COVERAGE

When analytics events are specified:
- Generate one test per event verifying it fires on the correct trigger
- Generate one test verifying the event properties and values are correct
- If property logic is conditional (e.g. only populated in certain cases), test each branch separately

==================================================
1D. LOCALIZATION COVERAGE

When multi-language support is specified:
- Generate at least one test per language per screen verifying UI strings render correctly
- Cover: titles, body text, CTA labels, error messages, placeholders

==================================================
1E. ACCESSIBILITY COVERAGE

When accessibility requirements are specified:
- Generate tests verifying resource IDs are present on interactive/visible elements
- Use Type: Positive (UI), Tags include ACCESSIBILITY

==================================================
- One test case = ONE core validation intent.
- ATOMIC RULE: For single-function requirements, maintain one validation per row.
- WORKFLOW/E2E RULE: For complex user journeys, multiple sequential steps (e.g. Login -> Action -> Logout) are ALLOWED if they culminate in a single primary business validation.
- Steps must be:
  - Clear
  - Sequential
  - Executable

==================================================
3. EXPECTED RESULT RULES

Expected Result MUST be:
- Single outcome
- Measurable
- Deterministic

DO NOT use:
- as designed
- if applicable
- if supported
- or equivalent
- or similar
- per policy

If contract is known:
- use exact status code / error code / response fields

If behavior is unknown:
- "Response matches the defined product/API contract"

==================================================
4. SCHEMA RULE

All testcase tables MUST use EXACTLY this header:

| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate | Dependency_Type | Device_Sensitivity | Network_Sensitivity | Backend_Service | Persona_Scenario | Status |

Do not change column names.
Do not reorder columns.
Do not omit columns.

New column value rules:

Dependency_Type: Live API | Stub | None
- Live API: TC exercises a real backend API
- Stub: TC validates a dummy/hardcoded/Sprint-blocked zone (no real API call)
- None: No backend dependency (pure local UI)

Device_Sensitivity: High | Medium | Low
- High: requires camera, biometric, specific hardware, low-end device conditions
- Medium: requires specific OS version, runtime permissions, app lifecycle (kill/relaunch)
- Low: pure UI, no device-specific hardware needed

Network_Sensitivity: High | Medium | Low
- High: TC exercises a live API call, file upload, or network condition
- Medium: TC depends on connectivity but it is not the primary validation
- Low: TC uses stub data or DataStore only

Backend_Service: name of the API or service exercised, or "-" if none
- Examples: Get User Profile API, JioCloud Upload API, DataStore (local), JioCare

Persona_Scenario: brief user context for UAT/exploratory testing
- Examples: Standard user, New user, Security-conscious user, Hindi-speaking user, User on slow network

Status: DRAFT | NEEDS_REFINEMENT | APPROVED
- DRAFT: default for all generated TCs
- NEEDS_REFINEMENT: TC has vague expected result, missing steps, or incomplete assertions
- APPROVED: manually reviewed and confirmed

==================================================
- Use machine-readable format with human-friendly labels.
- Format: `key=value (label)`
- Put all input values in the "Test Data" column only.
- Do NOT embed test data inside Steps.
- Do NOT use JSON.
- Do NOT use brackets () for anything other than labels.
- Do NOT use angle brackets <>.

Examples:
- `mobile=9876543210 (valid_registered)`
- `otp=123456 (correct_otp)`
- `otp=000000 (incorrect_otp)`
- `token=bearer_token (expired)`

Avoid:
- `{"mobile": "9876543210"}`
- `Mobile=valid_registered_mobile (9999999999)`
- `Authorization: Bearer <token>`

==================================================
6. TYPE RULE

Allowed values only:
- Positive (UI)
- Negative (UI)
- Edge/Timeout (UI)
- State management (UI)
- Performance (UI)
- Integration (UI)
- API validation (Positive)
- API validation (Negative)
- Security (API)
- Security (UI)

==================================================
7. PRIORITY RULE

Allowed values only:
- P0
- P1
- P2

==================================================
8. TAG RULE

- EXACTLY 3 tags
- UPPERCASE only

Allowed values:
SMOKE, REGRESSION, E2E, UI, API, SECURITY, NETWORK, STATE, ANALYTICS, LOCALIZATION, ACCESSIBILITY, REMOVAL, AUTH, HIGH_RISK, P0_FLOW, ABUSE, CONCURRENCY, INTEGRATION

Format:
- REGRESSION,API,AUTH
- REGRESSION,UI,P0_FLOW
- REGRESSION,NETWORK,HIGH_RISK
- REGRESSION,UI,REMOVAL
- REGRESSION,UI,ANALYTICS
- REGRESSION,UI,LOCALIZATION
- REGRESSION,UI,ACCESSIBILITY
- REGRESSION,STATE,HIGH_RISK

==================================================
9. EXECUTION TEAM RULE

Allowed values only:
- Mobile QA
- Web QA
- API QA
- Shared QA

Mapping:
- Mobile/UI flow → Mobile QA
- Web/browser flow → Web QA
- Backend/API contract flow → API QA
- Cross-layer/integration → Shared QA

==================================================
10. AUTOMATION CANDIDATE RULE

Allowed values only:
- Yes
- No

==================================================
11. DUPLICATE CONTROL

- Do not create duplicate intent
- Keep only unique validations
- If two rows validate different logic, keep both

==================================================
12. OUTPUT RULE

- Reader must NOT generate test cases or tables
- Generator must output ONLY one markdown table
- Validator must output ONLY one markdown table
- No prose before or after stage output

==================================================
13. COLUMN SAFETY RULE

- Do NOT use "|" character inside any cell value
- If needed, replace with "-" or "/"
- Using "|" inside Steps or Expected Result is STRICTLY FORBIDDEN