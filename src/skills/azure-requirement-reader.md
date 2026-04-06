# Skill: Requirement Reader

## Purpose
Extract only testing-relevant requirement content from raw requirement text or Azure DevOps work items.

## Critical Rules
- You are NOT allowed to generate test cases
- You are NOT allowed to generate markdown tables
- You are NOT allowed to generate TC_ID
- If output contains table rows or testcase content, output is invalid

## Task
- Extract only testing-relevant requirement content
- Break it into ATOMIC, TESTABLE conditions
- Assign unique IDs exactly in this format (mandatory):
  - REQ-001
  - REQ-002
  - REQ-003
- You MUST use the `REQ-` prefix followed by numbers. NEVER use `Requirement 1` or other formats.
- Do NOT use REQ-LOCAL

## Grouping Rule
- Group related behaviors under ONE Requirement_ID when they share the same entry point and logical context
- State Matrices: If a feature has multiple conditional states (e.g., Platform: iOS/Android AND App State: Installed/Not Installed), group them under ONE Requirement_ID but explicitly list ALL combinations in the output.
- **Sub-behavior enumeration (CRITICAL)**: When a REQ contains multiple distinct sub-flows, device interactions, or conditional states, you MUST enumerate ALL of them as explicit bullet points under that REQ. The generator uses this list to know how many test cases to create. A REQ with 6 sub-behaviors must show 6 bullets — not a single summary sentence.

### Good Examples
- OTP login flow → one requirement, with sub-bullets: enter mobile, receive OTP, enter OTP, OTP expiry, wrong OTP, resend OTP
- Edit Profile Picture → one requirement, with sub-bullets: icon always visible, bottom sheet opens, Camera tap → device camera opens, Gallery tap → READ_MEDIA_IMAGES permission prompt, gallery picker opens, upload success → avatar refreshes, upload failure → error shown
- Error handling → one requirement, with sub-bullets per error type

### Bad
- Splitting each sentence into separate Requirement_ID
- Writing a REQ as a single summary line when it contains multiple distinct testable sub-behaviors (this causes the generator to produce only 1–2 TCs instead of one per sub-behavior)

## Target
- For small/simple requirements → 2 to 5 Requirement_IDs
- For complex multi-section features (e.g. Home screen with multiple independent sections, each with unique entry/exit criteria) → scale up to 12–15 Requirement_IDs
- Do NOT collapse independent sections that each have their own entry criteria, exit criteria, or card state machines into a single REQ-ID
- Rule: If a section has its own entry criteria AND exit criteria AND distinct card states → it deserves its own REQ-ID

## Extraction Rules
- Split acceptance criteria into atomic lines
- Split business rules into atomic lines
- Split auth rules into atomic lines
- Split API behavior into atomic lines
- Split security/data exposure rules into atomic lines
- Extract ALL UI content requirements (e.g., Banners, Carousels, specific text/translations).
- Extract ALL explicit URLs, deep links, or tracking event names as testable data points.
- Extract Explicit Exclusions (e.g., "Do NOT validate this here", "No checks required").

### SCREEN SEQUENCE EXTRACTION (MANDATORY)
- Identify every distinct screen or view mentioned in the requirements
- For each screen, extract:
  - Its entry trigger (what tap, action, or condition causes navigation to it)
  - Its exit paths (back navigation, close button, success redirect, error redirect)
  - Any sub-screens or overlays it launches (bottom sheets, dialogs, pickers)
- Identify the full user journey sequence: which screens appear in order for each key flow
- This is used by the generator to produce navigation path tests and back-navigation tests

## Mandatory Extraction Categories (ALWAYS include in output)

### ENTRY & EXIT CRITERIA (Critical)
- For EVERY section, card, or widget that has conditional visibility:
  - Extract the ENTRY CRITERIA (conditions under which it appears) as a testable condition
  - Extract the EXIT CRITERIA (conditions under which it disappears) as a separate testable condition
  - If a card transitions to another card when dismissed, extract that transition as its own testable behavior

### APP LIFECYCLE CONDITIONS
- Extract any behavior tied to app kill/relaunch (e.g., "card resets on relaunch", "sequence shown once per session")
- Extract any behavior tied to session state (e.g., "shown once per session", "once in lifetime")
- Extract any resume/continuation behavior (e.g., "sequence resumes from where it stopped")

### REMOVAL / DEPRECATION ITEMS
- Extract ALL items explicitly stated as removed, deprecated, or replaced in this release
- These must be listed under a dedicated REMOVALS section
- Format: "REMOVED: <feature name> — must not appear on <screen>"

### ANALYTICS EVENTS
- Extract ALL analytics/CT event names mentioned
- For each event, extract: event name, trigger condition, all property names, and property value logic
- Format: "EVENT: <event_name> — fires when <condition> — properties: <prop1>=<value>, <prop2>=<value>"

### NON-FUNCTIONAL REQUIREMENTS
- Extract multi-language / localization requirements (e.g., "Hindi strings must be supported")
- Extract accessibility requirements (e.g., "Resource IDs required for all elements")
- Extract performance requirements if mentioned
- These must be listed under a dedicated NON-FUNCTIONAL section

### MOBILE / DEVICE-SPECIFIC BEHAVIORS (MANDATORY for mobile app requirements)
- Extract every Android/iOS permission required (e.g., READ_MEDIA_IMAGES, camera, biometric)
- Extract every device hardware feature invoked (camera open, gallery picker, biometric prompt, PIN entry)
- Extract every DataStore/SharedPreferences persistence requirement
- Extract every app lifecycle behavior (backgrounding, foreground resume, app kill/relaunch)
- Extract every feature explicitly marked as "not functional", "Phase N", "deferred to Sprint N", "visual only", or "no API call" — list these as SPRINT CONSTRAINTS with the exact prose from the requirement

### SPRINT CONSTRAINTS (MANDATORY when sprint-gating is present)
- For every feature or behavior that is explicitly blocked, deferred, or limited in the current sprint, extract it as:
  - BLOCKED: <feature> — <exact constraint from requirement>
  - DEFERRED: <feature> — planned for Sprint/Phase N
  - VISUAL ONLY: <feature> — no API call, toggle/UI only
- These drive negative test cases in the generator ("verify X does NOT fire / is NOT present")


## Output Format

TITLE:
<clean title>

SCREEN SEQUENCE:
- SCREEN: <screen name> — entry point: <what triggers navigation to this screen>
- SCREEN: <screen name> — navigates to: <screen name> via <tap target / action>
- BACK NAVIGATION: <screen name> → <previous screen> via <back button / gesture / close>
(List every screen mentioned, their entry triggers, and their exit/back paths. This drives navigation and flow tests in the generator.)

REQUIREMENTS:
- REQ-001: ...
  - sub-behavior: ...
  - sub-behavior: ...
- REQ-002: ...
  - sub-behavior: ...

ACCEPTANCE CRITERIA:
- ...
- ...

BUSINESS RULES:
- ...
- ...

ENTRY / EXIT CONDITIONS:
- REQ-XXX ENTRY: <condition that makes feature appear>
- REQ-XXX EXIT: <condition that makes feature disappear>
- REQ-XXX TRANSITION: <what appears when this feature exits>

APP LIFECYCLE CONDITIONS:
- REQ-XXX: <behavior on app kill/relaunch or session end>

PERSISTENCE SCOPE:
- REQ-XXX: FLOW-SCOPED — resets when user leaves the flow
- REQ-XXX: SESSION-SCOPED — persists during app session, resets on app kill
- REQ-XXX: APP-WIDE (DataStore) — persists across app restart
- REQ-XXX: SERVER-SYNCED — synced to backend (note if deferred to future sprint)
(Classify every persistence/state behavior. If the requirement says DataStore/SharedPreferences → APP-WIDE. If it says "once per session" → SESSION-SCOPED. If no persistence mentioned → FLOW-SCOPED.)

REMOVALS (features explicitly removed in this release):
- REMOVED: <feature name> — must NOT appear on <screen>

ANALYTICS EVENTS:
- EVENT: <event_name> — fires when <trigger> — properties: <name>=<value logic>

NON-FUNCTIONAL REQUIREMENTS:
- LOCALIZATION: <languages required, e.g. Hindi>
- ACCESSIBILITY: <resource IDs, screen reader requirements>

KNOWN GAPS / AMBIGUITIES:
- ...
- ...

## Output Rules
- Return only cleaned requirement content
- Do not generate test cases
- Do not generate tables
- Do not add assumptions unless clearly listed under KNOWN GAPS / AMBIGUITIES

## Limit Rule
- Simple features (single flow, few states): 2–6 Requirement_IDs
- Complex features (multiple sections, cards, states): up to 15 Requirement_IDs
- Do NOT merge two sections just to stay under a limit if they have different entry/exit criteria
- Each section/card with its own conditional visibility logic = its own REQ-ID

### Added Rules:

- Dependency Mapping: Identify if a requirement has a prerequisite (e.g., REQ-002 depends on REQ-001).

- Data Constraint Extraction: Explicitly list data types, lengths, and formats (e.g., "Email: max 50 chars, must contain @") to fuel boundary testing.

- Environment Context: Identify if a requirement is specific to a platform (Mobile vs. Web) based on the text.

- Design Screenshot Analysis (When Provided):
  - If a UI design screenshot is provided, extract additional testable requirements from it:
    - UI element inventory (buttons, input fields, labels, icons, carousels, banners)
    - Layout and navigation structure
    - Content/copy visible on screen (exact text, translations)
    - Visual states (active/inactive, selected/unselected, error states visible)
    - Any URLs, deep links, or CTAs visible in the design
  - Cross-reference the design against the requirement text to identify gaps.
  - Flag any discrepancies between written requirements and visual design under KNOWN GAPS / AMBIGUITIES.

