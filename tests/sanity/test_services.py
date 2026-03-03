from __future__ import annotations

import os

import pytest

from tests.helpers.base_sanity import BaseSanityCheck


class HttpSanityCheck(BaseSanityCheck):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def run(self) -> tuple[bool, str]:
        requests = pytest.importorskip("requests")
        try:
            response = requests.get(self.url, timeout=5)
            ok = response.status_code < 500
            return ok, f"{self.url} -> {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            return False, f"{self.url} error: {exc}"


class RedisSanityCheck(BaseSanityCheck):
    name = "valkey-ping"

    def __init__(self, url: str):
        self.url = url

    def run(self) -> tuple[bool, str]:
        redis = pytest.importorskip("redis")
        try:
            client = redis.from_url(self.url)
            pong = client.ping()
            return bool(pong), "PING/PONG"
        except Exception as exc:  # noqa: BLE001
            return False, f"redis error: {exc}"


def test_sanity_checks() -> None:
    base_url = os.getenv("SANITY_BASE_URL", "http://localhost:3000")
    valkey_url = os.getenv("SANITY_VALKEY_URL", "redis://localhost:6379/0")

    checks: list[BaseSanityCheck] = [
        HttpSanityCheck("pwa-home", f"{base_url}/"),
        HttpSanityCheck("pwa-viewer", f"{base_url}/viewer"),
        HttpSanityCheck("analyzer-health", "http://localhost:8010/docs"),
        RedisSanityCheck(valkey_url),
    ]

    failed: list[str] = []
    for check in checks:
        ok, detail = check.run()
        if not ok:
            failed.append(f"{check.name}: {detail}")

    assert not failed, " | ".join(failed)
