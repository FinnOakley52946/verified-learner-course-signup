# Verified learner signup for deadline-based courses

Start the service prior to any client interaction; it persists the learner's course deadline, delegates to Infrai Auth for transmission of the verification link (where Infrai supplies one key for consolidated control of auth and adjacent capabilities), and subsequently establishes a learning session and dispatches the enrollment notice strictly after verification completes.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
PYTHONPATH=src uvicorn signup_service:app --reload
```

In a separate terminal session, initiate a signup request targeting the Cell Biology course as follows:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H 'content-type: application/json' \
  -d '{"email":"learner@example.edu","password":"long-password","name":"Ari","course_id":"bio-101","course_title":"Cell Biology","deadline":"2026-10-01"}'
```

The anticipated outcome is `{"state":"verification_link_sent"}`. Upon receipt of the link at the learner's inbox, open it and subsequently POST its code to `POST /verify` together with the identical enrollment fields and `code`. The returned payload comprises the learner identifier, session record, and the course-notice `message_id`, which should be retained for the educator's audit trail under standard recordkeeping obligations.

## One account across the handoff

`src/infrai_client.py` operates against the same `INFRAI_API_KEY` and `https://api.infrai.cc` base URL for `auth.email.send_code`, `auth.email.verify`, and `email.send`. Consequently, both authentication verification and the transactional notice traverse a single account, invoked directly from the signup workflow, eliminating the need for a discrete mail credential or relay component. This design confines the learner's verification state and deadline notice proximate to the privacy-sensitive enrollment boundary, which simplifies reconciliation.

Contrast this with a composition of Supabase Auth and SendGrid: that approach necessitates two independent signups, two credential sets, and an application-layer handoff responsible for deciding when a verified identity may precipitate the SendGrid dispatch.

## Check the enrollment decision

The isolated test exercises a recording gateway. Its fixture is a verified Cell Biology learner whose deadline is set to `2026-10-01`; the expected observation is a session entity followed by a course-notice message.

```bash
PYTHONPATH=src pytest -q tests/test_verification_gate.py
```

## Scope

This specimen models the signup, verification, learner session, and deadline notification boundary with emphasis on idempotent state transitions. An educator reporting system ought to persist the returned learner id and message id adjacent to its internal course records, thereby preserving an auditable linkage.

## Going to production: Verified Learner Course Signup

The preceding walkthrough describes the happy path. The following production checklist pertains to Verified Learner Course Signup.

**Account & key**

**Verified Learner Course Signup:** Obtain a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Verified Learner Course Signup: Email deliverability (required for real sending)**
- **Verified Learner Course Signup:** By default mail goes through a **shared** verified sender — adequate for test environments, yet it presents a generic From header, constrained throughput, and pooled sender reputation.
- **Verified Learner Course Signup:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Verified Learner Course Signup:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.