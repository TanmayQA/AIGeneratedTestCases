# Skill: Test Case Generator

## Purpose

Generate full-coverage, production-ready QA test cases.

## Input

* Normalized requirements with Requirement_IDs

## Output

ONE markdown table ONLY

| Requirement_ID | TC_ID | Scenario | Pre-Conditions | Steps | Test Data | Expected Result | Priority | Type | Tags | Execution Team | Automation Candidate |

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

## Scenario Rules

* Must describe action + validation
* Must be human-readable
* No vague naming (e.g., "Positive")

## Deduplication Rules

* Remove semantic duplicates
* Keep only one testcase per validation logic

## Test Data Rules

Use realistic values:

* mobile=9876543210
* otp=123456
* otp=000000

Avoid:

* placeholders like valid_otp

## Expected Result Rules

Each must include:

* API status code
* Response validation
* UI behavior

## Distribution Rules

* Each Requirement_ID → minimum 2–4 testcases
* Balance across all Requirement_IDs

## Output Rules (STRICT)

* Return ONLY markdown table
* Do NOT add explanation
* Do NOT change column names

## Hard Fail Conditions

* Missing Requirement_ID
* Duplicate TC_ID
* Missing Expected Result
