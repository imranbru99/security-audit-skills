# Agent notes

The canonical skills live in `skills/<name>/SKILL.md`. When the user asks for a security review, audit, threat model, or triage of a suspected vulnerability, read `skills/security-audit/SKILL.md` first, then the specialist skill that matches the surface.

`examples/` contains intentionally vulnerable teaching fixtures. Do not deploy them, do not treat them as production code, and do not extend them into exploits. Read `examples/<name>/NOTES.md` for the expected conclusion.

A review reports confirmed findings, needs-validation items, and coverage gaps. It does not claim the target is secure because a search came back empty.
