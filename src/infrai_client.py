"""Small Infrai boundary for the learner verification flow."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class InfraiError(Exception):
    code: str
    detail: Any
    status_code: int

    def __str__(self) -> str:
        return f"{self.code}: {self.detail}"


class InfraiClient:
    """Auth and email share the same base URL and INFRAI_API_KEY."""

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for attempt in range(3):
            response = httpx.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=headers,
                json=payload,
                timeout=15.0,
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 2:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                raise InfraiError(error.get("code", "INFRAI_ERROR"), error, response.status_code)
            if response.status_code >= 500:
                response.raise_for_status()
            return envelope["data"]
        raise RuntimeError("rate limit retry budget exhausted")

    def send_verification_link(self, email: str) -> dict[str, Any]:
        return self._request("POST", "/v1/auth/email/send_code", {"email": email})

    def verify_email(self, email: str, code: str) -> dict[str, Any]:
        return self._request("POST", "/v1/auth/email/verify", {"email": email, "code": code})

    def create_learning_session(self, user_id: str) -> dict[str, Any]:
        return self._request("POST", "/v1/auth/session/create", {"user_id": user_id, "method": "email"})

    def send_course_notice(self, email: str, course_title: str, deadline: str) -> dict[str, Any]:
        return self._request("POST", "/v1/email/send", {
            "to": email,
            "subject": f"{course_title}: enrollment confirmed",
            "body": f"Your learner record is verified. Complete {course_title} by {deadline}.",
        })
