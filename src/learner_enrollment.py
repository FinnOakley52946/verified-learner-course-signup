"""Domain decisions for an educator's verification-gated enrollment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class EnrollmentGateway(Protocol):
    def send_verification_link(self, email: str) -> dict: ...
    def verify_email(self, email: str, code: str) -> dict: ...
    def create_learning_session(self, user_id: str) -> dict: ...
    def send_course_notice(self, email: str, course_title: str, deadline: str) -> dict: ...


@dataclass(frozen=True)
class Enrollment:
    email: str
    password: str
    name: str
    course_id: str
    course_title: str
    deadline: str


def begin_enrollment(gateway: EnrollmentGateway, enrollment: Enrollment) -> str:
    gateway.send_verification_link(enrollment.email)
    return "verification_link_sent"


def confirm_enrollment(gateway: EnrollmentGateway, enrollment: Enrollment, code: str) -> dict:
    verified = gateway.verify_email(enrollment.email, code)
    user_id = verified["user_id"]
    session = gateway.create_learning_session(user_id)
    notice = gateway.send_course_notice(enrollment.email, enrollment.course_title, enrollment.deadline)
    return {"user_id": user_id, "session": session, "message_id": notice["message_id"]}
