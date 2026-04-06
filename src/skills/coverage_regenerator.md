# Skill: Coverage Regenerator

## Purpose

Improve coverage by adding missing or weak test cases.

## Input

* Normalized requirements
* Reader output
* Existing validated test cases
* Coverage gap summary

## Data Synthesis
 - When generating new test cases, you MUST utilize specific, realistic data strings. Use valid formats (e.g., test_user@gmail.com), exact boundary strings (e.g., exactly 255 chars), and malicious payloads (e.g., <script>alert(1)</script>) in the Test Data column.


## Output

ONE corrected markdown table

## Core Rules

* DO NOT modify valid rows
* ONLY add missing coverage
* DO NOT create new Requirement_IDs

## Coverage Repair Rules

For weak/missing Requirement_ID:

* Add:

  * positive
  * negative
  * boundary
  * edge
  * invalid input
  * blank/null
  * whitespace
  * error handling
  * retry/resend
  * timeout/expiry
  * rate limit
  * state transition
  * API/UI behavior
  * security
  * dependency failure
  * network failure
  * Missing Permutations: Check if the requirement has multiple conditions (e.g., Logged in vs Logged out). If the existing table only covers one condition, generate the missing permutations.
* Missing Content Validations: Add cases for missing UI verifications, exact hyperlink routing, and translation mappings.

For mobile/app requirements, also check and add:

* **Device permission paths**: permission granted AND denied for each required permission
* **Device hardware flows**: camera open, gallery picker open, biometric prompt launch, PIN entry screen
* **Upload flows**: success → immediate UI reflection; failure → error state shown
* **Biometric/PIN flows**: correct PIN, incorrect PIN (stays locked), disable requires correct PIN
* **App lifecycle**: kill + relaunch with persistence assertions; foreground resume after background timeout
* **Sprint-blocked features**: verify "visual only" toggles make no API call; verify deferred/Phase N elements are non-functional
* **Explicit "must NOT" constraints**: for every constraint in requirements saying something must NOT appear or fire, verify a negative test exists

## Distribution Rules

* Each Requirement_ID → minimum 2–3 testcases
* Prioritize weak Requirement_IDs

## Atomic Quality

* One test case = one validation
* Avoid combining flows

## Expected Result Rule

* Must be detailed and verifiable

## Output Rules

* Return FULL table (not partial)
* No prose
* No JSON
* Maintain column structure strictly

### Added Rules:

- Technical Failure Scenarios: Specifically add cases for:

  - Network: Latency, 404/500 errors, and offline mode.

  - Security: SQL injection patterns in inputs, unauthorized API access (401/403).

- State-Transition Logic: Add cases for interrupted flows (e.g., "User backgrounded the app during OTP verification").

- Localization/Accessibility: Ensure coverage for different screen sizes and languages if mentioned in the reader output.