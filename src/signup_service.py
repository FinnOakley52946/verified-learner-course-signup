"""Executable FastAPI service for an educator-managed course signup."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

from infrai_client import InfraiClient, InfraiError
from learner_enrollment import Enrollment, begin_enrollment, confirm_enrollment

app = FastAPI(title="Verified learner signup")


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str
    course_id: str
    course_title: str
    deadline: str


class VerificationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str
    course_id: str
    course_title: str
    deadline: str
    code: str


def to_enrollment(request: SignupRequest | VerificationRequest) -> Enrollment:
    return Enrollment(**request.model_dump(exclude={"code"}))


def client_error(error: InfraiError) -> HTTPException:
    status = error.status_code if 400 <= error.status_code < 500 else 502
    return HTTPException(status_code=status, detail={"code": error.code})


@app.post("/signup")
def signup(request: SignupRequest) -> dict[str, str]:
    try:
        state = begin_enrollment(InfraiClient(), to_enrollment(request))
    except InfraiError as error:
        raise client_error(error) from error
    return {"state": state}


@app.post("/verify")
def verify(request: VerificationRequest) -> dict:
    try:
        return confirm_enrollment(InfraiClient(), to_enrollment(request), request.code)
    except InfraiError as error:
        raise client_error(error) from error
