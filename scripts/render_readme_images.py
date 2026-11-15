#!/usr/bin/env python3
"""Render the README figures in docs/images.

The figures describe this repository. They are not screenshots of a
hosted product. Run: python3 scripts/render_readme_images.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"

BG = (11, 17, 32)
CARD = (18, 27, 46)
CARD_2 = (24, 36, 58)
LINE = (46, 62, 92)
TEAL = (72, 214, 196)
TEAL_DIM = (18, 64, 62)
TEXT = (236, 242, 250)
MUTED = (158, 172, 194)
AMBER = (245, 186, 78)
RED = (255, 122, 122)
GREEN = (104, 224, 168)
WHITE = (255, 255, 255)

REGULAR = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 28)
MEDIUM = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 28)
SEMIBOLD = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 28)
BOLD = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 28)
MONO = ImageFont.truetype("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf", 22)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


F_REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
F_MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"


def canvas(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (w, h), BG)
    return image, ImageDraw.Draw(image)


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, value, face, fill, anchor="lt"):
    draw.text(xy, value, font=face, fill=fill, anchor=anchor)


def wrap(draw, value: str, face, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in value.split():
        trial = word if not current else f"{current} {word}"
        if draw.textlength(trial, font=face) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def pill(draw, xy, label, face, fill, ink, pad_x=18, pad_y=10):
    x, y = xy
    tw = draw.textlength(label, font=face)
    box = (x, y, x + tw + pad_x * 2, y + face.size + pad_y * 2)
    rounded(draw, box, 999, fill)
    text(draw, (x + pad_x, y + pad_y - 1), label, face, ink)
    return box


def save(image: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    image.save(OUT / name, "PNG", optimize=True)


def hero() -> None:
    image, draw = canvas(1600, 720)
    draw.rectangle((0, 0, 14, 720), fill=TEAL)
    text(draw, (72, 64), "AGENT SKILLS  ·  DEFENSIVE SOURCE REVIEW", font(F_SEMI, 22), TEAL)
    text(draw, (72, 118), "security-audit-skills", font(F_BOLD, 68), TEXT)
    lines = wrap(
        draw,
        "Turn Claude Code, Cursor, Codex, Gemini CLI, Copilot, or OpenCode into a reviewer that maps trust boundaries and reports only bugs that survive an attempt to disprove them.",
        font(F_REG, 28),
        860,
    )
    y = 220
    for line in lines:
        text(draw, (72, y), line, font(F_REG, 28), MUTED)
        y += 40

    x = 72
    y = 400
    for label in ("13 skills", "10 worked examples", "6-phase review", "MIT license"):
        box = pill(draw, (x, y), label, font(F_MED, 22), CARD_2, TEXT, 16, 10)
        x = box[2] + 14

    text(draw, (72, 500), "Works where Agent Skills load", font(F_MED, 20), MUTED)
    x = 72
    y = 544
    for label in ("Claude Code", "Cursor", "Codex", "Gemini CLI", "Copilot", "OpenCode"):
        box = pill(draw, (x, y), label, font(F_MED, 20), TEAL_DIM, TEAL, 14, 8)
        x = box[2] + 12
        if x > 900:
            break

    rounded(draw, (980, 78, 1528, 642), 28, CARD, LINE, 2)
    text(draw, (1016, 110), "CONFIRMED FINDING", font(F_SEMI, 18), GREEN)
    text(draw, (1016, 150), "High", font(F_BOLD, 28), AMBER)
    text(draw, (1100, 156), "Order id is not an ownership check", font(F_SEMI, 24), TEXT)
    rows = [
        ("Attacker", "Any logged-in user"),
        ("Location", "GET /api/orders/:id"),
        ("Missing", "query never filters userId"),
        ("Impact", "Another customer's order"),
        ("Fix", "bind the row to the session"),
    ]
    y = 230
    for label, value in rows:
        text(draw, (1016, y), label, font(F_MED, 20), MUTED)
        text(draw, (1180, y), value, font(F_REG, 22), TEXT)
        y += 52
    rounded(draw, (1016, 520, 1492, 590), 16, (28, 42, 38), None, 1)
    text(draw, (1040, 540), "UUID in the URL would not close this.", font(F_REG, 20), GREEN)
    save(image, "hero.png")


def workflow() -> None:
    image, draw = canvas(1600, 520)
    text(draw, (64, 40), "The review the agent is required to run", font(F_BOLD, 36), TEXT)
    text(
        draw,
        (64, 96),
        "A full review follows this order. A diff review starts at the changed lines and still disproves each lead.",
        font(F_REG, 22),
        MUTED,
    )
    steps = [
        ("1", "Scope", "Diff, feature, or whole tree. Write what is out of bounds."),
        ("2", "Map", "Routes, identity, stores, and the controls already on the path."),
        ("3", "Model", "Actor, entry point, asset, and the control that should stop them."),
        ("4", "Hunt", "Auth, then authorization, injection, secrets, crypto, CI, and IaC."),
        ("5", "Disprove", "Framework defaults, middleware, and dead code kill the lead."),
        ("6", "Report", "Confirmed, needs-validation, coverage. Severity from impact."),
    ]
    gap = 20
    left = 48
    width = (1600 - left * 2 - gap * 5) // 6
    top = 180
    for index, (num, title, body) in enumerate(steps):
        x = left + index * (width + gap)
        rounded(draw, (x, top, x + width, 460), 22, CARD, LINE, 2)
        circle = (x + 22, top + 22, x + 70, top + 70)
        draw.ellipse(circle, fill=TEAL_DIM)
        text(draw, (x + 46, top + 46), num, font(F_BOLD, 22), TEAL, anchor="mm")
        text(draw, (x + 22, top + 96), title, font(F_SEMI, 26), TEXT)
        y = top + 146
        for line in wrap(draw, body, font(F_REG, 18), width - 44):
            text(draw, (x + 22, y), line, font(F_REG, 18), MUTED)
            y += 26
    save(image, "workflow.png")


def skills_map() -> None:
    image, draw = canvas(1600, 1080)
    text(draw, (64, 40), "Thirteen skills, one verdict rule", font(F_BOLD, 36), TEXT)
    text(
        draw,
        (64, 96),
        "Install the set, or only the specialists that match the stack. No trust boundary, no finding.",
        font(F_REG, 22),
        MUTED,
    )
    groups = [
        (
            "Procedure",
            TEAL,
            [
                ("security-audit", "Scope, threat model, hunt, verify, rate, report"),
            ],
        ),
        (
            "Bug classes",
            AMBER,
            [
                ("web-security", "XSS, CSRF, SSRF, IDOR, redirects, files, CORS"),
                ("api-security", "BOLA, mass assignment, webhooks, GraphQL"),
                ("auth-security", "Sessions, JWT, OAuth, reset, object checks"),
                ("injection-security", "SQL, shell, NoSQL, templates, deserialization"),
                ("secrets-exposure", "Keys in source, logs, clients, and fixtures"),
                ("supply-chain-security", "Lockfiles, install scripts, privileged CI"),
                ("iac-security", "Terraform, Kubernetes, Docker, IAM"),
                ("crypto-misuse", "Password hashes, randomness, TLS, MAC compare"),
            ],
        ),
        (
            "Languages",
            GREEN,
            [
                ("python-security", "Django, Flask, FastAPI, pickle, DEBUG"),
                ("javascript-security", "React, Next.js, Node, prototype pollution"),
                ("go-security", "SQL text, path.Join, templates, crypto/rand"),
                ("php-security", "Laravel policies, Blade, mass assignment"),
            ],
        ),
    ]
    # Custom layout: procedure is a wide banner, then two columns.
    rounded(draw, (64, 160, 1536, 280), 22, CARD, LINE, 2)
    text(draw, (96, 188), "security-audit", font(F_SEMI, 28), TEAL)
    text(
        draw,
        (360, 192),
        "Orchestrates the review. Specialists supply the framework detail. This skill decides the verdict.",
        font(F_REG, 22),
        TEXT,
    )
    columns = [
        (64, "Bug classes", AMBER, groups[1][2]),
        (832, "Languages and frameworks", GREEN, groups[2][2]),
    ]
    for x, title, color, items in columns:
        text(draw, (x, 316), title, font(F_SEMI, 24), color)
        y = 364
        for name, blurb in items:
            rounded(draw, (x, y, x + 704, y + 68), 16, CARD, LINE, 2)
            text(draw, (x + 22, y + 12), name, font(F_SEMI, 20), TEXT)
            text(draw, (x + 22, y + 38), blurb, font(F_REG, 18), MUTED)
            y += 80
    save(image, "skills.png")


def finding() -> None:
    image, draw = canvas(1600, 760)
    text(draw, (64, 40), "A finding is a path, not a bug-class name", font(F_BOLD, 36), TEXT)
    text(
        draw,
        (64, 96),
        "The skills reject “possible SQL injection, please sanitize.” This is the required shape.",
        font(F_REG, 22),
        MUTED,
    )
    rounded(draw, (64, 160, 1536, 700), 28, CARD, LINE, 2)
    text(draw, (104, 196), "HIGH", font(F_BOLD, 20), AMBER)
    text(draw, (180, 192), "Search text is concatenated into the SQL statement", font(F_SEMI, 28), TEXT)
    body = [
        ("Location", "examples/python-sql-search/vulnerable.py  ·  search_users"),
        ("Attacker", "Anyone who can pass name into the public search field"),
        ("Boundary", "Request data becomes SQL syntax under the application role"),
        ("Evidence", "An f-string is the only argument to cursor.execute. No parameter tuple."),
        ("Disproved", "Not DB-API binding. LIKE wildcards inside the string are not parameters."),
        ("Fix", "Constant SQL. Bind the value. Put the wildcards inside the bound parameter."),
        ("Check", "A quote in name must not change the statement text."),
    ]
    y = 260
    for label, value in body:
        text(draw, (104, y), label, font(F_MED, 20), TEAL)
        text(draw, (280, y), value, font(F_REG, 22), TEXT)
        y += 56
    save(image, "finding.png")


def modes() -> None:
    image, draw = canvas(1600, 460)
    text(draw, (64, 36), "Three ways to use the same skills", font(F_BOLD, 36), TEXT)
    cards = [
        ("Guidance", "A question or a design choice.", "Direct answer. No report file. The full audit does not start."),
        ("Focused", "A diff, a feature, or one bug class.", "Findings for that scope, plus the paths you did not follow."),
        ("Full", "You asked for an audit or a report.", "All six phases, a threat model, and an explicit coverage gap."),
    ]
    width = 480
    for index, (title, when, result) in enumerate(cards):
        x = 48 + index * (width + 28)
        rounded(draw, (x, 120, x + width, 400), 24, CARD, LINE, 2)
        text(draw, (x + 32, 152), title, font(F_BOLD, 32), TEAL)
        text(draw, (x + 32, 214), "When", font(F_MED, 18), MUTED)
        y = 246
        for line in wrap(draw, when, font(F_REG, 22), width - 64):
            text(draw, (x + 32, y), line, font(F_REG, 22), TEXT)
            y += 30
        text(draw, (x + 32, 310), "You get", font(F_MED, 18), MUTED)
        y = 342
        for line in wrap(draw, result, font(F_REG, 20), width - 64):
            text(draw, (x + 32, y), line, font(F_REG, 20), MUTED)
            y += 28
    save(image, "modes.png")


def main() -> None:
    hero()
    workflow()
    skills_map()
    finding()
    modes()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
