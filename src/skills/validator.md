# Skill: Test Case Validator

## Purpose

Validate, clean, and normalize test cases to enterprise quality.

## Input

* One or more test case tables

## Output

ONE clean markdown table

## Responsibilities

* Merge multiple tables
* Remove duplicates (exact + semantic)
* Fix missing fields
* Normalize values

## Traceability Rules

* DO NOT create new Requirement_IDs
* ALL Requirement_IDs must be present
* Add missing testcases if required

## Atomic Rule

* One testcase = one validation
* Split multi-validation rows

## Expected Result Enforcement

Must include:

* API status code
* Response validation
* UI behavior

## Workflow/E2E Rules

* DO NOT atomize high-quality E2E workflows into single steps.
* Preserve sequential logic (e.g. Try wrong OTP -> Try correct OTP) if it serves a single core validation.

## Coverage Repair

Ensure each Requirement_ID includes:

* positive, negative (E2E flows where applicable)
* blank/null, whitespace
* boundary, invalid format
* expiry, retry, rate limit
* server failure, auth failure
* security, dependency failure
* network failure

For mobile/app requirements, additionally check for:

* Device permission flows (granted AND denied paths)
* Device hardware interactions (camera open, gallery picker, biometric prompt)
* File/photo upload success and failure paths
* Biometric/PIN setup, incorrect PIN, fallback paths
* App backgrounding and foreground resume behavior
* DataStore/local persistence verified via app kill + relaunch
* Phase/Sprint placeholder features — visible but non-functional verification
* Hardcoded/dummy data values verified explicitly

## Explicit Exclusion Audit (MANDATORY)

Scan the requirements for ALL prose-embedded "must NOT" constraints. For each one found, verify a negative test exists. If missing, ADD it. Look for:

* "not shown", "not visible", "not displayed" in any state
* "not functional", "non-functional", "does nothing", "tapping does nothing"
* "no API call", "visual only", "no real API call is made"
* "Phase N — not functional", "deferred to Sprint N", "not confirmed for Sprint N"
* "no OTP flow", "dialog only", "dialog flow shown only"
* Sprint-constrained features that are blocked or incomplete

For each missing exclusion test — ADD a Negative (UI) testcase verifying the constraint holds.

## Paired-Path Audit (MANDATORY)

For every confirmation dialog, permission request, deep-link, and selector in the suite:

* **Dialog Cancel path missing?** → ADD a TC: tap Cancel → dialog dismisses, user stays on screen, no state change
* **Dialog Confirm path missing?** → ADD a TC: tap Confirm → expected outcome per requirement
* **Permission denied path missing?** → ADD a TC: deny permission → graceful error shown, flow blocked, no crash
* **Deep-link "not installed" path missing?** → ADD a TC: app not installed → fallback behavior (dialler/browser)
* **Only default option tested for a selector?** → ADD a TC for each non-default option
* **"Coming soon" items untested?** → ADD a negative TC: tap coming-soon item → no selection occurs

## Screen Navigation Audit (MANDATORY when SCREEN SEQUENCE is present in reader output)

For every navigation path in the reader's SCREEN SEQUENCE:

* Verify a forward navigation test exists (trigger → target screen opens)
* Verify a back navigation test exists (target screen → previous screen via back/close)
* Verify sub-screens (bottom sheets, dialogs) have both an open and dismiss test
* If any navigation path has no test → ADD it

## Thematic Grouping Audit (MANDATORY)

For any requirement that describes a UI element, zone, or screen that can be in multiple distinct states (e.g., backup status: in-progress / done / fail; toggle: ON / OFF; avatar: photo / initials / loading):

* Identify the theme (the shared UI element or zone)
* Verify a test case exists for EACH named state
* If a state is mentioned in requirements but has no TC → ADD it
* Verify that no single TC tries to cover multiple states in its steps — if found, SPLIT it
* Flag any state that was mentioned in requirements but marked as "dummy / deferred" — a placeholder rendering test is still required

## Persistence Scope Audit (MANDATORY)

For every test case that validates state, preference, or data persistence:

* Check the Pre-Conditions and Steps declare the correct persistence scope (FLOW-SCOPED / SESSION-SCOPED / APP-WIDE / SERVER-SYNCED)
* Check the Steps include the correct lifecycle action for the scope:
  - APP-WIDE: Steps must include "kill app" + "relaunch app" to confirm persistence
  - SESSION-SCOPED: Steps must include "background app" test AND "kill + relaunch" test (expect reset)
  - FLOW-SCOPED: Steps must include "navigate away" and verify state reset on return
* If the Steps only say "verify value is saved" without a lifecycle action → ADD the lifecycle step or create a companion test
* If the scope is mismatched (e.g., a DataStore preference only tested within session) → ADD the correct scope test

## Conditional UI Coverage Audit (MANDATORY)

For any Requirement_ID that describes a section, card, or widget with conditional visibility:

* Verify there is an ENTRY CRITERIA test (section appears when condition met)
* Verify there is an EXIT CRITERIA test (section disappears when condition met)
* Verify there is a USER DISMISSAL test if the card is "Closable by user"
* Verify there is an APP LIFECYCLE test if the card resets on app kill/relaunch
* Verify there is a TRANSITION test if exiting one card causes another card to appear
* If any of these are missing — ADD them

## Feature Removal Audit (MANDATORY)

* If the requirements mention removed/deprecated features, verify there is at least one test per removed item confirming it does not appear
* If missing — ADD them

## Analytics Audit (MANDATORY)

* If analytics events are specified in requirements, verify each event has at least one test confirming it fires with correct properties
* If missing — ADD them

## Localization Audit

* If multi-language support is specified, verify at least one test per language per screen
* If missing — ADD them

## Deduplication

Remove:

* Exact duplicates
* Semantic duplicates

## Value Normalization

Priority:
* P0 / P1 / P2
- If Priority is missing, default to P2.

Execution Team:
* Mobile QA / Web QA / API QA / Shared QA
- If missing, default to Shared QA

Automation Candidate:
* Yes / No

Tags:
* Exactly 3 uppercase values

Dependency_Type:
* Live API — TC exercises a real backend API
* Stub — TC validates a dummy/hardcoded/Sprint-blocked zone
* None — no backend dependency
- Derive from step content if LLM did not fill it

Device_Sensitivity:
* High — camera, biometric, hardware, low-end device
* Medium — permissions, app lifecycle, kill/relaunch
* Low — pure local UI, DataStore only

Network_Sensitivity:
* High — live API call, upload, network condition test
* Medium — connectivity dependent but not primary
* Low — stub or DataStore only

Backend_Service:
* Name of the API or service exercised, or "-"

Persona_Scenario:
* Brief user context — e.g., Standard user, Security-conscious user, Hindi-speaking user
* Default to "Standard user" if missing

Status:
* DRAFT — default for all generated TCs
* NEEDS_REFINEMENT — flag when expected result is vague, steps are incomplete, or TC conflates multiple validations
* APPROVED — do not assign; reserved for human review

Mark a TC as NEEDS_REFINEMENT if:
- Expected result contains phrases like "as expected", "should work", "if applicable", "as designed"
- Steps say only "observe behavior" without specifying what to observe
- Scenario bundles more than one independent validation intent

## Final Rules

* No duplicate scenarios
* Balanced distribution across Requirement_IDs
* Output ONLY markdown table
* No prose

### Added Rules:

- Controlled Tagging: Use a fixed dictionary for the Tags field to prevent AI drift.

- Allowed Tags: SMOKE, REGRESSION, E2E, UI, API, SECURITY, NETWORK, STATE, ANALYTICS, LOCALIZATION, ACCESSIBILITY, REMOVAL.

- Automation Feasibility Logic: Define "Automation Candidate: Yes" strictly for cases that are:

- Repetitive / High Volume.

- Critical Path (Smoke/Sanity).

- UI-Stable or API-based.

- Traceability Lock: Ensure that every merged row maintains its original Requirement_ID to prevent "orphaned" test cases.