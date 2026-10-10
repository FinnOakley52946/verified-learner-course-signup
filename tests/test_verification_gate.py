from learner_enrollment import Enrollment, begin_enrollment, confirm_enrollment


class RecordingGateway:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def send_verification_link(self, email: str) -> dict:
        self.calls.append("send_verification_link")
        return {"message_id": "verify-17"}

    def verify_email(self, email: str, code: str) -> dict:
        self.calls.append("verify_email")
        return {"user_id": "learner-17"}

    def create_learning_session(self, user_id: str) -> dict:
        self.calls.append("create_learning_session")
        return {"session_id": "session-17"}

    def send_course_notice(self, email: str, course_title: str, deadline: str) -> dict:
        self.calls.append("send_course_notice")
        return {"message_id": "notice-17"}


def test_verified_learner_receives_course_notice_after_session_creation() -> None:
    enrollment = Enrollment("learner@example.edu", "long-password", "Ari", "bio-101", "Cell Biology", "2026-10-01")
    gateway = RecordingGateway()

    assert begin_enrollment(gateway, enrollment) == "verification_link_sent"
    result = confirm_enrollment(gateway, enrollment, "123456")

    assert result["message_id"] == "notice-17"
    assert gateway.calls == [
        "send_verification_link", "verify_email",
        "create_learning_session", "send_course_notice",
    ]
