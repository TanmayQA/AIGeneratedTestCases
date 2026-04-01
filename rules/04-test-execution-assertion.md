# 04. TEST EXECUTION & ASSERTION RULES – STRICT EXECUTION

==================================================
1. EXPECTED RESULT DETERMINISM

Expected Result MUST be:
- Single specific outcome
- Measurable and observable
- Executable by a tester or automation script

DO NOT use ambiguous phrases:
- "as designed"
- "if applicable"
- "if supported"
- "or equivalent"
- "or similar"
- "per policy"

Fallback Rule: If exact behavior is completely unknown from docs:
- Use "Response matches the defined product/API contract"
- Use "Behavior matches the defined product/API contract"

==================================================
2. UI ASSERTION RULE

UI Expected Results must strictly include:
- What is visibly shown (specific validation/error/success message).
- What action is explicitly blocked or allowed.
- What screen remains active or displayed.
- Whether a corresponding API/Network call is triggered (if relevant context).

==================================================
3. API ASSERTION RULE

API Expected Results must strictly include:
- Response schema/payload matches the defined API contract.
- Status Code (e.g., 200 OK, 400 Bad Request, 401 Unauthorized, etc.).
- State changes (e.g., whether session/token is created, database updated).
- Security assertion (e.g., whether sensitive data is inappropriately exposed or properly masked).

==================================================
4. NEGATIVE, SECURITY & RELIABILITY COVERAGE

Mandatory assertions inside test coverage constraints:
- Inputs: Invalid, Null/blank/whitespace, Format violations, Boundary limits.
- Security: Rate limiting, Brute force prevention, Replay protection, Injection handling, Authorization logic.
- Performance/Network: Timeout handling, Expiry scenarios, Slow network delays, Retry policies, Dependency/3rd Party API failures.
==================================================
