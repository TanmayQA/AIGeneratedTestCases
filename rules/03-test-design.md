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
3. TEST DATA FORMAT

- Use machine-readable key=value format with semantic labels in brackets.
- `mobile=9876543210 (valid_registered)`
- `otp=111111 (incorrect_otp)`
- `token=session_token (expired)`
- Avoid raw, meaningless values without labels.

==================================================
4. DUPLICATE CONTROL

- Do not create cases with duplicate intent.
- Keep only the most clear, most critical and executable case.
- Split wide boundary validations into separate, distinct test cases rather than overloading one case.

==================================================
5. ENTRY/EXIT CRITERIA PAIRING RULE

- For every UI section, card, or widget that has conditional display logic:
  - Entry test and exit test are BOTH required — they are not duplicates, they are paired
  - Entry test: pre-condition = condition NOT met, action = trigger the condition, expected = section appears
  - Exit test: pre-condition = section is currently visible, action = trigger exit condition, expected = section disappears

==================================================
6. CARD STATE MACHINE RULE

- When a requirement describes multiple card variants for the same UI slot (e.g. "Low Battery card", "No Network card", "Manual Upload card" all appearing in the same area):
  - Each variant is a distinct test case — do NOT group them
  - Test each card's unique entry condition, unique content, and unique exit condition separately
  - Test that cards override each other correctly when priority dictates

==================================================
7. FEATURE REMOVAL TEST RULE

- When a feature is explicitly removed in the requirements:
  - Write a test that navigates to the screen and verifies the removed element is NOT present
  - Do NOT assume removal — test it explicitly

==================================================
