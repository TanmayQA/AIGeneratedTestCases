# Skill: Coverage Regenerator

## Purpose

Improve coverage by adding missing or weak test cases.

## Input

* Normalized requirements
* Reader output
* Existing validated test cases
* Coverage gap summary

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
