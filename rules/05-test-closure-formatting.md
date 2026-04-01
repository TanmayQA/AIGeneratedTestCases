# 05. TEST CLOSURE & FORMATTING RULES – STRICT EXECUTION

==================================================
1. EXECUTION TEAM ENFORCEMENT

Assign EXACTLY ONE functional execution team per case.
Allowed Teams:
- Mobile QA
- Web QA
- API QA
- Shared QA

Mapping context:
- Mobile UI/Device specific → Mobile QA
- Web UI/Browser specific → Web QA
- Backend/API only → API QA
- Cross-layer/End-to-End → Shared QA

==================================================
2. TEST TYPE NORMALIZATION

Ensure every test specifies exactly one matching Type from STLC conventions:
- Positive (UI)
- Negative (UI)
- Edge/Timeout (UI)
- State management (UI)
- Performance (UI)
- Integration (UI)
- API validation (Positive)
- API validation (Negative)
- Security (API)
- Security (UI)

==================================================
3. FORMAT & OUTPUT RULE

Formatting is strictly enforced to ensure pipeline integrity:
- Strict markdown table format ONLY.
- NO missing columns (Must match the exact requested table schema from prompt).
- NO duplicate rows.
- NO extra markdown text, introductions, subjective explanations, or conclusions outside of the generated table.
- Produce CSV-compatible table structure.
==================================================
