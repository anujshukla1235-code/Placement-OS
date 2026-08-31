# Placement Management Portal - AI + Data Science + Blockchain

## Quick Start
1. `pip install -r requirements.txt`
2. `cp .env.example .env` and fill (at minimum: `SECRET_KEY`, `DEBUG=True` for local dev)
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. `python manage.py runserver`

Frontend (Next.js, separate app): `cd placement-frontend && npm install --legacy-peer-deps && npm run dev`
(`--legacy-peer-deps` is needed because `@sentry/react` in package.json currently only
declares support up to React 18, while this project is pinned to React 19.)

## Running Tests
Backend: `python manage.py test accounts jobs companies interviews blockchain_module learn billing students`
(Run app labels explicitly — bare `python manage.py test` has a discovery quirk in some
environments and reports 0 tests found.)

Frontend type-check: `cd placement-frontend && npx tsc --noEmit`

CI: `.github/workflows/ci.yml` runs both on every push/PR.

## API Documentation
Auto-generated from the actual DRF views/serializers (drf-spectacular), so it can't go
stale the way a hand-written doc can:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Raw OpenAPI schema: `/api/schema/`

## API Base: /api/v1/
- Auth: /auth/register/, /auth/verify-otp/, /auth/login/, /auth/login/verify-mfa/,
  /auth/forgot-password/, /auth/reset-password/, /auth/me/delete/ (GDPR-style self-delete)
- Admin approvals: /auth/approvals/, /auth/approvals/<user_id>/action/ (approves COMPANY
  or COLLEGE accounts, sends a real email on approve/reject)
- Jobs: /jobs/ , /jobs/<id>/apply/
- Students: /students/me/ , /students/resume/upload/
- Companies: /companies/me/ , /companies/ (public approved list)
- College: /college/me/, /college/dashboard/, /college/bulk-upload/ (CSV student import)
- Interviews: /interviews/
- AI: /ai/applications/<id>/ats-score/
- Blockchain: /blockchain/generate/ , /verify/offer/<id>/ (public, no /api/v1 prefix —
  this is the URL embedded in every offer letter's QR code)
- Analytics: /analytics/overview/ , /analytics/skill-gap/ , /analytics/at-risk/
- Data Science: /ds/placement-probability/?job_id= , /ds/recommended-jobs/ , /ds/my-predictions/
- Billing: /billing/plans/, /billing/me/ (real); /billing/checkout/, /billing/webhook/
  (scaffolding only — see billing/models.py and billing/views.py docstrings for what's
  needed to go live with a real payment gateway)

## Security Features Implemented
- PBKDF2 password hashing, JWT short expiry, OTP 5min expiry + 3 attempts + rate limit 5/hour
- Account lockout 5 fails -> 15min
- Django ORM (no raw SQL) -> SQL injection safe
- CSRF, XSS sanitized
- Resume upload: PDF-only enforced by magic-byte check (not just filename), 5MB size cap
- Hash-chain for offers + QR verification + tamper detection (recomputes and compares the
  stored hash — a previous bug that always reported offers as valid regardless of tampering
  has been fixed and is covered by tests)
- RBAC enforced in all views, with tenant isolation (a company/college can only see and
  modify its own jobs/interviews/students — covered by automated tests)
- Per-tenant rate limiting on high-write endpoints (job posting, CSV bulk-upload) so one
  tenant can't exhaust another's quota
- Login history + verified_count audit logs
- No hardcoded insecure defaults: SECRET_KEY/DEBUG must be set explicitly in production

## Multi-Tenancy Model
Single shared-schema database; isolation is enforced at the application layer via
`company`/`college` foreign keys checked against `request.user` in every view that reads
or writes tenant data. This is verified by the automated tenant-isolation test suite
(companies can't see/edit each other's jobs, interviews, or applicants; colleges can't see
each other's students).

## Known Gaps (honest status, not yet done)
- Billing: scaffolding only, no live payment gateway (see above)
- WhatsApp (Feature 55): real Twilio integration is wired in (notifications/
  whatsapp_service.py, triggered on application status change) but needs your own
  Twilio account + `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`/`TWILIO_WHATSAPP_FROM` in
  `.env` to actually send — without them it safely no-ops and logs what it would have sent
- AI Feedback (Feature 57): wired in on resume upload via Gemini
  (`ai_module/feedback_generator.py`); needs `GEMINI_API_KEY` in `.env` to use the real
  model, otherwise falls back to a rule-based summary so the field is never empty
- Company/College logo upload: URL field only, no direct file upload yet
- AI/ML features are intentionally lightweight (TF-IDF similarity for ATS/recommendations,
  not an LLM for scoring — only the feedback text itself uses Gemini), and the
  "blockchain" is SHA-256 hash-chaining, not a distributed ledger — both work correctly
  for what they claim to do, just don't expect more than that from the naming

See docs/ folder for full spec.

