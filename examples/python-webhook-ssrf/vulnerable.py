# INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
# Do not deploy. Do not run against real networks.
"""Delivers a webhook to whatever URL the caller submits."""

import requests


def deliver(url: str, payload: dict) -> None:
    requests.post(url, json=payload, timeout=5)
