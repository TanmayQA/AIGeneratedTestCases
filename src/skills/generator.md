# Skill: Test Case Generator

## Purpose

Generate full-coverage, production-ready QA test cases.

## Input

* Normalized requirements with Requirement_IDs

## Output

ONE markdown table ONLY

| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate | Dependency_Type | Device_Sensitivity | Network_Sensitivity | Backend_Service | Persona_Scenario | Status |

## Core Instructions

* Cover ALL Requirement_IDs
* Generate ATOMIC test cases (1 validation per row)
* Ensure UNIQUE scenarios

## Mandatory Coverage (Per Requirement_ID)

* Positive flow
* Negative flow
* Blank/null input
* Whitespace input
* Boundary values
* Invalid format
* Expiry/timeout
* Retry/resend
* Rate limiting
* Server/API failure
* Authentication failure
* Security/abuse
* Dependency failure
* Network failure

## Conditional UI / Card Coverage (MANDATORY for any section with entry/exit criteria)

For EVERY section, card, or widget that has conditional visibility, you MUST generate:

* **Entry criteria test** — verify the section appears when its entry condition is met
* **Exit criteria test** — verify the section disappears when its exit condition is met
* **Transition test** — if exiting one card causes another to appear, verify that transition
* **State persistence test** — if a card has "once per session" or "once in lifetime" behavior, verify it does not re-appear
* **App kill/relaunch test** — if behavior resets on relaunch (e.g. card dismissed, sequence reset), verify that lifecycle behavior
* **User dismissal test** — if a card is "Closable by user: Yes", verify the dismiss action and that the card does not reappear until exit criteria is met

## Feature Removal Coverage (MANDATORY)

If the requirements explicitly state that a feature, card, section, or UI element has been REMOVED or DEPRECATED in this release:

* Generate a test case verifying that the removed element does NOT appear
* Scenario format: "Verify <removed feature> is no longer visible on <screen>"
* Type: Negative (UI)
* Priority: P0 if it was a core feature, P1 otherwise

## Analytics Event Coverage (MANDATORY when analytics events are specified)

For EVERY analytics/CT event mentioned in the requirements:

* Generate a test case verifying the event fires when the trigger condition is met
* Generate a test case verifying the event properties are correct (event name, property names, property values)
* If an event has conditional property logic (e.g. "option property only populated when View More is clicked"), generate separate tests for each branch

## Localization Coverage (MANDATORY when multi-language is specified)

For EVERY UI screen or section where multi-language support is required:

* Generate at least one test case verifying UI strings render in the specified language (e.g. Hindi)
* Cover: section titles, card text, CTA labels, error messages, placeholder text
* Type: Positive (UI), tagged LOCALIZATION

## Accessibility Coverage (MANDATORY when accessibility requirements are specified)

* Generate test cases verifying resource IDs are present on interactive elements
* Type: Positive (UI), tagged ACCESSIBILITY

## Section Order / Display Order Coverage (MANDATORY when Order values are specified)

For EVERY section that has an explicit display Order value:

* Generate a test case verifying the section appears in the correct position relative to adjacent sections
* Scenario: "Verify <Section A> appears before <Section B> per defined order"

## Screen Sequence Coverage (MANDATORY when SCREEN SEQUENCE is present in reader output)

Read the SCREEN SEQUENCE section from the reader output. For every navigation path listed:

* **Forward navigation test** — tap the trigger element and verify the correct target screen opens
* **Back navigation test** — use back button/gesture and verify return to the previous screen with state intact
* **Sub-screen/overlay test** — for every bottom sheet, dialog, or picker launched from a screen, verify it opens, is dismissible, and selection propagates correctly
* **Deep entry test** — if a screen can be reached from multiple entry points (e.g., Settings row on Profile → Settings screen), verify each entry point independently
* **Navigation state preservation** — if the requirement says state is preserved when navigating away and back, generate an explicit test for it

## Thematic Grouping (MANDATORY for multi-state requirements)

When a requirement describes the same UI element or screen zone across multiple distinct system states (e.g., backup status: in-progress / done / fail), treat these as a **theme** and generate one test case per state variant:

* Identify the theme (e.g., "backup status zone display")
* List all states the theme can be in (e.g., in-progress, done, fail, loading, empty)
* Generate one TC per state — do NOT merge multiple states into one TC
* Tag all TCs in the same theme consistently so they can be grouped in a report
* If the requirement mentions only some states (e.g., only in-progress and done), still generate a test for any blocked/deferred states to verify the fallback/placeholder renders correctly

## Screen-Type Mandatory Checklists (MANDATORY — apply based on screen type detected)

Detect the screen type from the requirement. For each type present, apply its checklist:

### OTP / Verification Code Screen
- Valid OTP entered → success flow
- Invalid OTP entered → error message displayed
- Expired OTP → distinct expiry error shown
- Empty submission → blocked, inline error shown
- Resend OTP → new OTP sent, old OTP invalidated
- Rate limit on resend (after N attempts) → resend button disabled with timer
- OTP autofill from SMS (if platform supports it)

### Text / Number Input Field
- Valid input → accepted
- Empty submission → inline validation error
- Whitespace-only input → treated as empty / rejected
- Minimum length boundary → exact min accepted, one below rejected
- Maximum length boundary → exact max accepted, one above blocked or truncated
- Invalid format (email, phone, PIN) → format error shown
- Special characters / injection payloads → sanitized, no crash, no XSS
- Copy-paste behavior → pasted value subject to same validation

### Authentication / Login Flow
- Successful login → correct screen opened, session token set
- Wrong credentials → specific error message (no credential hints)
- Account locked → lock message shown
- Session expiry → redirect to login with message
- Concurrent session handling (if specified)
- Remember-me / auto-login behavior (if specified)

### Settings / Toggle Screen
- Each toggle default state matches spec
- Each toggle can be turned ON independently
- Each toggle can be turned OFF independently
- Toggling one does NOT affect other toggles
- All toggle states persist after app kill + relaunch (if DataStore-persisted)
- Settings screen accessible from the correct entry point

### Profile / Avatar Screen
- Photo loaded successfully → displays photo only, no fallback overlay
- Photo loading in progress → placeholder or initials shown during load
- Photo load failed / URL error → fallback (initials or default icon) shown
- Photo absent / null URL → fallback shown
- Edit action visible and tappable
- Identity fields (name, number) read-only and non-editable

### Bottom Sheet / Modal Dialog
- Trigger action opens the sheet/dialog
- All options/content listed in spec are present and in correct order
- Each option is tappable and produces the correct action
- Dismiss by swipe down (if applicable) closes without side effects
- Dismiss by tapping outside (if applicable) closes without side effects
- Sheet/dialog does not persist on app background + foreground resume unexpectedly

### List / Accordion / FAQ
- Item count matches the exact number specified in requirements
- Tapping an item expands it with correct content
- Tapping an expanded item collapses it
- Only one item expanded at a time (if spec says so), or multiple (if spec allows)
- Empty state renders correctly (if list can be empty)

### Language Selector
- Currently active language is shown as selected/highlighted
- Switching to a supported language → all app strings re-render immediately
- "Coming soon" / unavailable languages show correct badge and are NOT tappable
- Language selection persists after app kill + relaunch

## Workflow/E2E Coverage (MANDATORY)

* Full Happy Path (Success flow from start to finish)
* Multi-Step state progression (e.g. Request -> Verify -> Confirm)
* State recovery (e.g. Try wrong OTP, then try correct OTP)
* Session timeout to login redirection flow
* Cross-function E2E (e.g. Change profile data and verify reflecting in dashboard)

## Scenario Rules

* Must describe action + validation
* Must be human-readable
* No vague naming (e.g., "Positive")

## Combinatorial & Exclusion Rules (MANDATORY)

* State Matrix Coverage: If a requirement mentions multiple variables (e.g., OS type + App Installation State), you MUST generate a separate test case for EVERY possible permutation/combination. Do not group them into one step.

* Asset & Content Coverage: You MUST write explicit test cases verifying exact URLs, dynamic links, Translations, and UI element counts (e.g., "Verify exactly 3 carousels") if mentioned in the requirement.

* Explicit Exclusion Validation: If the requirement explicitly states an action should NOT occur, you MUST generate a negative test case verifying that the action indeed does not happen. This applies to ALL forms of prose-embedded constraints, including:
  - "not shown", "not visible", "not displayed" → verify element is absent
  - "not functional", "non-functional", "does nothing", "tapping does nothing" → verify no action fires
  - "no API call", "no validation", "visual only" → verify no network/API call is made
  - "Phase N — not functional", "deferred to Sprint N" → verify the element is present but inert or not present at all per spec
  - "no OTP flow", "dialog only", "flow shown only" → verify only the dialog/UI renders, no backend call fires


## Mobile-Specific Coverage (MANDATORY when mobile/app requirements are present)

For requirements involving mobile device interactions, you MUST generate test cases for:

* **Device permission flows** — for every permission required (camera, READ_MEDIA_IMAGES, contacts, location, biometric), generate:
  - Permission granted path → expected flow proceeds
  - Permission denied path → expected graceful error/fallback

* **Device hardware interactions** — for every hardware feature invoked (camera open, gallery picker, biometric prompt, PIN entry), generate a test verifying the correct system UI opens

* **Photo/file upload flows** — generate separate tests for: upload success → UI reflects immediately; upload failure → error handling

* **Biometric / PIN flows** — generate tests for: setup success, incorrect PIN (N attempts), correct PIN to disable/reset, fallback when biometrics fail

* **App backgrounding and resume** — for every requirement that specifies behavior on foreground resume (e.g. app lock after 30s), generate an explicit test with the specified time threshold

* **DataStore / local persistence** — for every setting or preference stored locally, generate a test that kills and relaunches the app and verifies the value persists

* **Phase/Sprint placeholder features** — for every feature marked "Phase N", "Sprint N — not functional", or "deferred", generate a test verifying:
  - The UI element IS visible (if the row/section should still appear)
  - Tapping it produces NO action or navigation

* **Static/dummy data screens** — for every zone using hardcoded values, generate tests verifying each hardcoded value is correct and no API call is made

## Persistence Scope Validation (MANDATORY for every state/storage requirement)

Read the PERSISTENCE SCOPE section from the reader output. For every state or preference that has an assigned scope, generate tests that validate the CORRECT lifecycle boundary — not just that the value was saved:

| Scope | What to test |
|---|---|
| FLOW-SCOPED | Navigate away from the flow and verify state is RESET when returning |
| SESSION-SCOPED | Background + foreground the app and verify state persists; kill + relaunch and verify state is RESET |
| APP-WIDE (DataStore) | Kill + relaunch and verify state PERSISTS with exact value |
| SERVER-SYNCED | Log out, log back in and verify state syncs from server (or note as deferred) |

Rules:
* A test that only checks "value saved during session" is insufficient for APP-WIDE scope — you MUST add a kill + relaunch step
* A test that only checks "value persists after relaunch" is insufficient for SESSION-SCOPED — you MUST add a kill test showing it resets
* Pre-Conditions must state the scope: e.g., "language persisted in DataStore (APP-WIDE scope)"
* Do NOT mix scope levels in one test case

## Low-End Device Considerations (MANDATORY for all mobile UI requirements)

Generate explicit test cases for the following low-end device scenarios — do NOT rely on generic "works on all devices" wording:

* **Image loading placeholder** — while a photo/avatar is loading on a slow connection, verify the correct placeholder (initials or skeleton) is shown and not a blank or broken state
* **Slow API response rendering** — when an API call takes >3 seconds, verify the screen shows a loading indicator and does not crash or display empty/broken UI
* **Low-storage upload behavior** — when device storage is near full (< 100 MB free), verify upload operations show a meaningful error rather than silently failing
* **Small screen layout** — on 360×640 dp viewport, verify that all interactive elements (buttons, toggles, inputs) are fully visible without overlap or cropping
* **Rapid navigation stress** — tapping through multiple screens quickly in succession does not crash the app or produce blank screens
* **Background battery saver / data saver** — if the app performs background sync or network calls, verify behavior is graceful when battery saver or data saver mode is active (either skips sync with no crash, or shows correct status)
* **Accessibility text scaling** — at 150% font scale, verify that text does not overflow buttons or truncate critical labels

For each scenario above that is applicable to the requirement:
* Type: Edge/Timeout (UI)
* Priority: P1
* Tags: include HIGH_RISK

## Mandatory Paired-Path Rules (NEVER generate one side without the other)

These pairs are always required. Generating only one side is a coverage defect:

### Dialog Cancel + Confirm
For EVERY confirmation dialog (dialogs that have a Cancel button AND a Confirm/action button):
- **Cancel path**: tap Cancel → dialog dismisses, user stays on current screen, no state change, no API call
- **Confirm path**: tap Confirm/action button → expected outcome described in requirements

Do NOT generate only the "dialog appears" TC without also covering Cancel and Confirm paths.

### Permission Granted + Permission Denied
For EVERY OS permission request (camera, READ_MEDIA_IMAGES, contacts, biometric, notifications):
- **Granted path**: permission granted → flow proceeds as expected
- **Denied path**: permission denied → graceful error/guidance shown, app does not crash, flow does not proceed

### Deep-Link Installed + Not Installed
For EVERY deep-link or app-intent (e.g., Contact JioCare, share intent, in-app browser):
- **App installed path**: deep-link fires, target app opens
- **App NOT installed path**: fallback behavior (dialler, browser, error message) occurs

### All N options of a selector
For EVERY selector, picker, or toggle group that has N named options:
- Generate a separate TC for each non-default option (do NOT only test the default)
- For display modes: Dark (default), Light, System → all three need TCs
- For language: English (default), Hindi → both selectable paths need TCs
- For "coming soon" items: generate a non-selectable negative TC for each

### Exact time-threshold tests
For EVERY requirement that specifies a time threshold (e.g., "after 30 seconds", "within 3 seconds"):
- The TC Steps must use the EXACT value from the requirement (not "a few seconds" or "some time")
- Generate a TC that exceeds the threshold AND one that is below it if the behavior differs

## Deduplication Rules

* Remove semantic duplicates
* Keep only one testcase per validation logic

## Test Data Rules

Use machine-readable format with labels:

* `mobile=9876543210 (valid_registered)`
* `otp=123456 (correct_otp)`
* `otp=000000 (incorrect_otp)`
* `token=bearer (expired)`

Avoid:

* placeholders like valid_otp
* JSON format

## Expected Result Rules

Each must include:

* API status code
* Response validation
* UI behavior

## Distribution Rules

* Simple Requirement_ID (single flow, minimal states) → minimum 3 testcases
* Complex Requirement_ID (multiple sub-behaviors, states, device interactions) → one test per distinct sub-behavior, with no upper cap
* If a REQ describes N distinct sub-flows or states, generate at least N testcases — do NOT compress them into fewer rows
* Do NOT stop early because a REQ already has "enough" tests — cover every explicitly stated behavior

## Output Rules (STRICT)

* Return ONLY markdown table
* Do NOT add explanation
* Do NOT change column names

## Hard Fail Conditions

* Missing Requirement_ID
* Duplicate TC_ID
* Missing Expected Result
