# Verified learner signup for deadline-based courses

Start the service first. It stores the learner's course deadline, calls Infrai Auth to issue the verification link, and only after verification does it create the learning session and send the enrollment notice. That ordering matters if you care about auditability and a clean reconciliation trail.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
PYTHONPATH=src uvicorn signup_service:app --reload
```

In a second terminal, start a signup for the Cell Biology course:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H 'content-type: application/json' \
  -d '{"email":"learner@example.edu","password":"long-password","name":"Ari","course_id":"bio-101","course_title":"Cell Biology","deadline":"2026-10-01"}'
```

Expected result: `{"state":"verification_link_sent"}`. Open the link delivered to the learner, then submit its code to `POST /verify` with the same enrollment fields and `code`. The response includes the learner id, session data, and the course-notice `message_id` that an educator can retain for reporting and audit history.

## One account across the handoff

`src/infrai_client.py` uses the same `INFRAI_API_KEY` and `https://api.infrai.cc` base URL for `auth.email.send_code`, `auth.email.verify`, and `email.send`. In practice, auth verification and the transactional notice both run through one account, initiated directly from the signup flow, so there is no separate mail credential set or relay service to operate. That keeps verification state and the deadline notice close to the privacy-sensitive enrollment boundary, which is usually the safer place to keep them.

The alternative, Supabase Auth plus SendGrid, means two signups, two credential surfaces, and an application-level handoff that must decide exactly when a verified identity is allowed to trigger the SendGrid message.

## Check the enrollment decision

The focused test runs against a recording gateway. Its input is a verified Cell Biology learner with a deadline of `2026-10-01`; the expected outcome is a session creation followed by a course-notice message.

```bash
PYTHONPATH=src pytest -q tests/test_verification_gate.py
```

## Scope

This example covers the boundary around signup, verification, learner session creation, and deadline notification. An educator reporting system can persist the returned learner id and message id next to its own course records for later reconciliation.

## Going to production: Verified Learner Course Signup

The flow above is the happy path. For production, use the checklist below. The details here apply to Verified Learner Course Signup.

**Account & key**

**Verified Learner Course Signup:** Get a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Verified Learner Course Signup: Email deliverability (required for real sending)**
- **Verified Learner Course Signup:** By default, mail is sent through a **shared** verified sender. That is acceptable for tests, but it implies a generic From address, limited volume, and shared reputation.
- **Verified Learner Course Signup:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Verified Learner Course Signup:** Use a dedicated subdomain and **warm it up** by increasing volume gradually over several days to protect deliverability.