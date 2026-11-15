# Safe counterpart to vulnerable.py.
# The host must be one the product registered. Redirects are not followed.
"""Delivers a webhook to an allowlisted HTTPS host."""

import urllib.parse

import requests

ALLOWED_HOSTS = {"hooks.partner.example"}


def deliver(url: str, payload: dict) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("webhook must use https")
    if parsed.username or parsed.password:
        raise ValueError("webhook URL must not embed credentials")
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("webhook host is not registered")
    if parsed.port not in (None, 443):
        raise ValueError("webhook port is not allowed")
    requests.post(url, json=payload, timeout=5, allow_redirects=False)
