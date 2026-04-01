# Skill: Finalizer

## Purpose
Produce one final, clean, production-ready markdown table from the current repaired suite.

## Input
- Current final markdown table
- Expected Requirement_ID list

## Output
Return ONLY ONE markdown table with EXACTLY these columns and EXACTLY this order:

| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate |

## Instructions
- Preserve all valid rows
- Remove exact duplicates
- Remove semantic duplicates if they validate the same logic
- Keep one testcase = one validation
- Do NOT invent new Requirement_IDs
- Do NOT drop any Requirement_ID from input
- Expand Expected Result if vague
- Keep schema fully consistent

## Strict Rules
- No prose before or after table
- No JSON
- No comments
- No extra columns
- No missing columns
- No blank Requirement_ID
- No blank TC_ID
- No blank Expected Result

## Coverage Rules
For each Requirement_ID:
- keep at least 2 meaningful rows where logically applicable
- do not over-focus on one Requirement_ID while others remain weak

## Expected Result Rules
Each Expected Result must be verifiable and include:
- API status code where applicable
- response validation where applicable
- UI behavior where applicable

## Output Rule
Return ONLY the final corrected markdown table.