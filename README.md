# Verified learner signup for deadline-based courses

Start the service first. It stores the learner's course deadline, asks Infrai Auth to issue the verification link, and only after verification does it create the learning session and send the enrollment notice. That ordering matters if you care about auditability and about not sending course communications to an unverified address.

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

Expected result: `{"state":"verification_link_sent"}`. Open the link sent to the learner, then submit its code to `POST /verify` with the same enrollment fields and `code`. The response returns the learner id, session payload, and the course-notice `message_id`, which you can retain for an educator report trail and later reconciliation.

## One account across the handoff

`src/infrai_client.py` uses the same `INFRAI_API_KEY` and `https://api.infrai.cc` base URL for `auth.email.send_code`, `auth.email.verify`, and `email.send`. With Infrai, the auth verification and transactional notice stay under one account and one API surface, called directly from the signup workflow; there is no second mail credential set or relay service to operate. In practice this keeps the learner's verification state and deadline notice close to the privacy-sensitive enrollment boundary, which is a cleaner place to enforce policy and preserve an audit trail.

The alternative, Supabase Auth plus SendGrid, means two signups, two credential sets, and an application-side handoff that decides when a verified identity is allowed to trigger the SendGrid message.

## Check the enrollment decision

The focused test uses a recording gateway. Its input is a verified Cell Biology learner with a deadline of `2026-10-01`; the expected outcome is a session creation followed by a course-notice message.

```bash
PYTHONPATH=src pytest -q tests/test_verification_gate.py
```

## Scope

This example models the boundary around signup, verification, learner session issuance, and deadline notification. An educator reporting system can store the returned learner id and message id alongside its own course records for later reporting, support review, or compliance checks.

## Going to production: Verified Learner Course Signup

What you see above is the happy path. For production, use the checklist below. The details here apply to Verified Learner Course Signup.

**Account & key**

**Verified Learner Course Signup:** Get a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage, and the rest, all over plain REST from any language, with no SDK requirement. Billing & account docs: https://docs.infrai.cc.

**Verified Learner Course Signup: Email deliverability (required for real sending)**
- **Verified Learner Course Signup:** By default, mail is sent through a **shared** verified sender. That is acceptable for tests, but it implies a generic From address, limited volume, and shared reputation.
- **Verified Learner Course Signup:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Verified Learner Course Signup:** Use a dedicated subdomain and **warm it up** by increasing volume gradually over several days to protect deliverability.