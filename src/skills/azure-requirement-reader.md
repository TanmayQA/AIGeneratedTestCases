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
- Assign unique IDs:
  - REQ-001
  - REQ-002
  - REQ-003
- Do NOT use REQ-LOCAL

## Grouping Rule
- Do NOT over-split requirements
- Group related behaviors under ONE Requirement_ID when they belong to same logical flow

### Good Examples
- OTP login flow → one requirement
- OTP validation rules → one requirement
- Error handling → one requirement

### Bad
- Splitting each sentence into separate Requirement_ID

## Target
- For small requirements → 2 to 5 Requirement_IDs
- Avoid generating more than 6 Requirement_IDs unless absolutely necessary

## Extraction Rules
- Split acceptance criteria into atomic lines
- Split business rules into atomic lines
- Split auth rules into atomic lines
- Split API behavior into atomic lines
- Split security/data exposure rules into atomic lines

## Output Format

TITLE:
<clean title>

REQUIREMENTS:
- REQ-001: ...
- REQ-002: ...
- REQ-003: ...

ACCEPTANCE CRITERIA:
- ...
- ...

BUSINESS RULES:
- ...
- ...

KNOWN GAPS / AMBIGUITIES:
- ...
- ...

## Output Rules
- Return only cleaned requirement content
- Do not generate test cases
- Do not generate tables
- Do not add assumptions unless clearly listed under KNOWN GAPS / AMBIGUITIES

## Limit Rule
- Maximum 6 Requirement_IDs allowed
- If more are possible, merge logically related ones