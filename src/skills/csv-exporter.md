# Skill: CSV Exporter

## Purpose

Convert markdown test case table into clean CSV format.

## Input

* Final markdown table

## Output

Valid CSV content

## Instructions

* Preserve column order exactly
* Preserve all rows
* Escape commas and quotes properly

## Column Order (STRICT)

Requirement_ID,TC_ID,Scenario,Pre-Conditions,Steps,Test Data,Expected Result,Priority,Type,Tags,Execution Team,Automation Candidate

## Rules

* Output ONLY CSV
* No markdown
* No explanation
* No extra headings

## Validation

* Ensure no data loss
* Ensure formatting is Excel-compatible
