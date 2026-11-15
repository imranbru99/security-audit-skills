# Contributing

This collection is a set of instructions agents follow during a defensive review. A change should make those reviews more accurate.

## What to send

- A specialist for a stack or bug class that is not covered, with the same verification bar as the existing skills.
- A correction when a skill describes an API wrong, recommends a fix that is still vulnerable, or tells the agent to report something the framework already closes.
- A fixture under `examples/` when a new pattern is easier to learn from code than from a paragraph.

## What not to send

- Exploit payloads, bypass cookbooks, gadget chains, or steps for attacking a live system.
- Scanner-output dumps restated as a skill.
- A new skill that only says "be careful about X" without sinks, safe APIs, and false positives.

## Skill shape

Create `skills/<name>/SKILL.md`. `name` is lowercase words separated by hyphens, at most 64 characters, and it matches the directory name.

```yaml
---
name: example-security
description: >-
  What the skill reviews, in third person. Use when <the files, features,
  and words that should trigger it>.
license: MIT
---
```

The description is what clients put in the skill catalog. It has to say what the skill does and when to use it, in 1024 characters or fewer. Start the trigger clause with `Use when`.

The body stays under 500 lines. Put long worksheets in `references/` next to the skill and link them once from `SKILL.md`. Those links must keep working after the skill directory is copied by itself, so do not link to `../../other-skill`. Mention sibling skills by name.

Every skill includes these headings:

- `## When to use`
- `## Verify before you report`
- `## False positives`

Also include the patterns to look for, how to rate them, and a short vulnerable snippet beside the safe pattern. The safe pattern has to actually close the bug. If the safe pattern is subtle (`filepath.Join` does not contain traversal; DB-API `%s` is sometimes a placeholder), say so.

Verdicts match `security-audit`: a confirmed finding has an attacker, a path, a broken control, and an outcome. If the decisive control is outside the repo, the status is needs-validation.

## Examples

Fixtures live in `examples/<case>/`:

- `vulnerable.*` with `INTENTIONALLY VULNERABLE` in the first lines
- `secure.*` implementing the fix
- `NOTES.md` with the rating, the fix, and the false positive this case exists to prevent

Keep fixtures inert. A function or a fragment is enough. Do not add a listening server, a real credential, or a weaponized request.

## Reviewer checklist

Before you open the pull request, run:

```bash
make check
```

That runs `scripts/check_skills.py`. It checks frontmatter, the required headings, the line limit, example banners, and that the README skills table names every skill. Update the table between the `skills-table` markers when you add a skill.

In the pull request, say which false positive the change is meant to prevent, or which real bug it was missing.

## Reports

Use [SECURITY.md](SECURITY.md) for skill content that would cause an unsafe review. Use a normal issue for everything else.
