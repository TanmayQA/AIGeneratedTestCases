# 02. TEST PLANNING RULES – STRICT EXECUTION

==================================================
1. RISK ASSESSMENT & PRIORITY (NORMALIZED VALUES)

Priority mapping must follow STLC standards:
- P0 (Critical/Blocker): Core user flows, critical functionality, security boundaries.
- P1 (High): Important features but non-blocking, alternate paths.
- P2 (Medium/Low): Edge cases, UI cosmetics, minor validations.

==================================================
2. TAG MAPPING & TEST SELECTION

Assign tags reflecting test intent properly formatted as UPPERCASE.

Tags Structure MUST include EXACTLY 3 tags per case:
1. Suite: SMOKE / REGRESSION / SANITY
2. Layer: UI / API / SECURITY / NETWORK / STATE / CONCURRENCY / INTEGRATION
3. Risk/Category: AUTH / HIGH_RISK / P0_FLOW / ABUSE

Mapping Rules:
- UI interaction → UI
- API response validation → API
- Network issues (offline, slow connection) → NETWORK
- App/Browser cache, session state → STATE
- 3rd Party/Dependency failure → INTEGRATION
- Parallel submissions, race conditions → CONCURRENCY
- Authentication/Security bypass → AUTH / SECURITY

Automation Candidate:
- Yes: deterministic, stable data, repeatable.
- No: physical interaction required, highly dependent on manual setup, edge UX checks.
==================================================
