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

## Coverage Repair

Ensure each Requirement_ID includes:

* positive, negative
* blank/null, whitespace
* boundary, invalid format
* expiry, retry, rate limit
* server failure, auth failure
* security, dependency failure
* network failure

## Deduplication

Remove:

* Exact duplicates
* Semantic duplicates

## Value Normalization

Priority:

* P0 / P1 / P2

Execution Team:

* Mobile QA / Web QA / API QA / Shared QA

Automation Candidate:

* Yes / No

Tags:

* Exactly 3 uppercase values

## Final Rules

* No duplicate scenarios
* Balanced distribution across Requirement_IDs
* Output ONLY markdown table
* No prose
