# 03. TEST DESIGN & DEVELOPMENT RULES – STRICT EXECUTION

==================================================
1. SCENARIO-STEP ALIGNMENT

- Scenario MUST match Steps strictly.
- If Scenario = "Send OTP API" → Steps must ONLY instruct interactions with "Send OTP API".
- If Scenario = "Verify OTP API" → Steps must ONLY instruct interactions with "Verify OTP API".
- Do NOT mix UI + API within a single step unless it's explicitly explicitly verifying a cross-layer reflection (e.g. "Trigger UI action and observe API payload").

==================================================
2. TEST STEP CONSTRUCTION

- One test case = ONE core validation intent. Do not combine multiple independent validations into a single test case.
- Steps must be:
  - Clear and unambiguous
  - Sequential
  - Fully Executable (imperative mood, e.g. "Enter valid mobile")

==================================================
3. TEST DATA RULE (SEMANTIC LABELS)

Test Data must use semantic labels, including examples when useful:
- `Mobile=valid_registered_mobile (9999999999)`
- `OTP=invalid_incorrect_otp (000000)`
- `OTP=expired_otp (123456 after 31s)`

Avoid raw, meaning-less values without labels (e.g., do not just write "Use 999999", write what it represents).

==================================================
4. DUPLICATE CONTROL

- Do not create cases with duplicate intent.
- Keep only the most clear, most critical and executable case.
- Split wide boundary validations into separate, distinct test cases rather than overloading one case.
==================================================
