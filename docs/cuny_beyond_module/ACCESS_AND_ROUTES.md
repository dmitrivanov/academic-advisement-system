# CUNY Beyond - Access, Credentials, and Page Addresses

## Base addresses

- Hosted application: `https://academic-advisement-system.onrender.com`
- Local application: `http://127.0.0.1:8000`

Append a page path from this guide to either base address. For example, the local CUNY Beyond address is `http://127.0.0.1:8000/cuny-beyond`.

## Access model

CUNY Beyond exploration is intentionally public and does not require login. It stores a short-lived anonymous draft in the visitor's browser. Name, email, and optional last-four ID digits are requested only when the visitor intentionally opens the referral workflow.

The existing degree-planning application is protected by login. Administrator pages require the administrator role.

## Demonstration credentials

Default local development accounts are:

- Administrator: username `admin`, password `admin`
- Student tester: username `tester`, password `tester`

The tester can use authenticated student pages but cannot access administrator pages or administrator APIs. Hosted credentials may be overridden by the deployment environment. Never assume the default passwords are appropriate for a public deployment.

Environment variables:

- `APP_USERNAME` and `APP_PASSWORD`: administrator account
- `TESTER_USERNAME` and `TESTER_PASSWORD`: non-administrator tester account
- `SESSION_SECRET`: session-signing secret

## Public CUNY Beyond pages

- `/cuny-beyond` - chatbot-style anonymous career and prior-learning onboarding
- `/cuny-beyond/referral` - downloadable pre-advisement summary and consented referral preparation
- `/health` - basic service health check

## Authenticated student pages

- `/login` - sign in
- `/logout` - sign out
- `/program-selector` - select campus and program; supports `?intent=major-change`
- `/db-progress` - completed-course selector, requirements, progress, and degree plan
- `/transfer-analysis` - transfer and equivalency comparison
- `/schedule-handoff` - verified guided handoff to CUNY Global Search

The root `/` redirects authenticated users to the program selector and unauthenticated users to login.

## Administrator pages

- `/admin` - administrator dashboard
- `/admin/major-constructor` - draft curriculum builder and publishing workflow
- `/admin/ai-settings` - AI advisor configuration
- `/admin/schedule-settings` - terms and governed schedule-provider configuration
- `/admin/cuny-beyond-governance` - career, program-career, CPL, transfer, and source governance

## Main CUNY Beyond API addresses

All database API paths begin with `/api/db`.

- `GET /api/cuny-beyond/config` - public anonymous-session settings
- `GET /api/db/cuny-beyond/careers` - reviewed career catalog
- `POST /api/db/cuny-beyond/recommendations` - explainable career-to-program matching
- `POST /api/db/cuny-beyond/cpl-screening` - nonbinding prior-learning preparation
- `GET /api/db/cuny-beyond/schedule/terms` - active verified terms
- `POST /api/db/cuny-beyond/schedule/sections` - governed section lookup with safe handoff fallback

Administrator governance APIs are protected even when their addresses are known.

## Suggested demonstration sequence

1. Open `/cuny-beyond` without logging in.
2. Complete the chatbot onboarding using `Data Analyst`, `Registered Nurse`, `Accounting Clerk`, or another reviewed career.
3. Open a recommended official source or degree planner.
4. Sign in as `tester` to demonstrate student-only access.
5. Sign out, then sign in as `admin` to demonstrate governance and curriculum tools.

## Security note

Change all passwords and `SESSION_SECRET` for hosted or shared environments. Do not place credentials, API keys, or production database URLs in source control, screenshots, student-facing documentation, or email.
