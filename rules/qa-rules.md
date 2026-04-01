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
2. TEST DESIGN RULES

- One test case = ONE validation
- Do not combine multiple validations
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

| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate |

Do not change column names.
Do not reorder columns.
Do not omit columns.

==================================================
5. TEST DATA RULE

- Use machine-readable format only
- Use ONLY key=value format
- Put all input values in the "Test Data" column only
- Do NOT embed test data inside Steps
- Do NOT use JSON
- Do NOT use descriptive wrappers like valid_/invalid_
- Do NOT use brackets ()
- Do NOT use angle brackets <>

Examples:
- mobile=9876543210
- otp=123456
- request_id=valid_request_id
- token=valid_bearer_token

Avoid:
- {"mobile": "9876543210"}
- Mobile=valid_registered_mobile (9999999999)
- Authorization: Bearer <token>

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

Format:
- REGRESSION,API,AUTH
- REGRESSION,UI,P0_FLOW
- REGRESSION,NETWORK,HIGH_RISK

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