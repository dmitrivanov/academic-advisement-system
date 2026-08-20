# CUNY Beyond — Phase 1 Implementation Record

**Public shell and anonymous intake**  
Version 1.0 — August 2026

## 1. Stage outcome

Phase 1 establishes CUNY Beyond as a second, public entry point inside the existing Academic Advisement System. Prospective students can begin career-first exploration without creating an account. The authenticated degree-planning application and its database remain unchanged.

Implemented routes:

- `/cuny-beyond` — public, responsive intake experience
- `/api/cuny-beyond/config` — public non-sensitive runtime configuration
- `/login` — now includes a public **Explore careers and BMCC majors** entry point

The module is enabled by default and can be disabled without a code change:

```text
CUNY_BEYOND_ENABLED=false
```

## 2. Implemented student journey

The incoming/prospective-student intake contains five accessible steps:

1. Select one of six student profiles.
2. Describe a career or life goal in plain language.
3. Indicate whether the student currently works, or decline to answer.
4. Choose one to five skills from a controlled starter list.
5. Review a concise starting profile and see what the next stage will add.

Supported profiles:

- High-school student
- Working adult
- Adult with some college
- Transfer student
- Returning student
- Adult who already holds a degree

The page also provides a clearly separated current-student path. It hands the student to the existing program selector with `intent=major-change`. A dedicated what-if workflow remains a later phase.

## 3. Privacy and anonymous continuity

Phase 1 deliberately does not request or transmit a name, email address, CUNY ID, transcript, employer, or course history.

The draft is stored only in the current browser under a versioned local-storage key. It includes:

- selected profile code;
- career-goal text;
- employment answer;
- up to five selected skills;
- current step; and
- expiration timestamp.

The default expiration is 24 hours. Administrators can set a value from 1 through 168 hours:

```text
CUNY_BEYOND_SESSION_TTL_HOURS=24
```

Expired drafts are deleted during the next page load. **Restart** asks for confirmation and deletes only the CUNY Beyond draft. The page tells students not to enter personally identifying information.

## 4. Accessibility and responsive behavior

Implemented accessibility features include:

- a skip link;
- semantic headings, form controls, labels, and fieldsets;
- visible keyboard focus;
- error and save-status live regions;
- focus movement to the next step heading;
- native radio and checkbox keyboard behavior;
- prevention of a sixth skill selection;
- reduced-motion support; and
- single-column layouts on narrow screens.

The experience requires no pointer drag-and-drop and remains usable at mobile widths.

## 5. Technical design

```text
Public browser
  |
  +-- GET /cuny-beyond
  |     -> frontend/cuny_beyond.html
  |     -> frontend/cuny_beyond.css
  |     -> frontend/cuny_beyond.js
  |
  +-- GET /api/cuny-beyond/config
        -> enabled flag
        -> anonymous draft lifetime

Authenticated application
  +-- unchanged program, progress, transfer, and admin routes
```

`cuny_beyond.py` owns feature-flag and session-lifetime parsing. Keeping this policy outside the FastAPI entrypoint makes it independently testable and prevents the browser from controlling privacy limits.

No database tables or migrations were added. This is intentional: career mappings, CPL screens, recommendation results, and staff publishing controls require reviewed models in subsequent phases.

## 6. Files changed

- `cuny_beyond.py` — bounded public configuration
- `faq_fallback_api.py` — public page and configuration routes
- `frontend/cuny_beyond.html` — accessible intake structure
- `frontend/cuny_beyond.css` — responsive public design
- `frontend/cuny_beyond.js` — validation, steps, storage, expiration, and restart
- `frontend/login.html` — public entry point
- `tests/test_cuny_beyond_phase_one.py` — Phase 1 regressions

## 7. Verification

The focused automated suite verifies:

- the public route does not invoke login enforcement;
- the feature flag can disable the module;
- the anonymous lifetime is bounded and has a safe fallback;
- all six required profiles are present;
- selections are limited to five skills;
- privacy, expiration, restart, and accessibility controls remain present; and
- current students are handed off with major-change intent.

Command:

```text
pytest tests/test_cuny_beyond_phase_one.py -q
```

Expected result: **6 passed**.

## 8. Deployment configuration

No new service is required. The existing Render start command continues to serve `faq_fallback_api:app`.

Recommended deployment values:

```text
CUNY_BEYOND_ENABLED=true
CUNY_BEYOND_SESSION_TTL_HOURS=24
```

Smoke-test checklist after deployment:

1. Open `/cuny-beyond` in a private browser window without logging in.
2. Complete all five steps using only the keyboard.
3. Refresh and confirm the draft is restored.
4. Restart and confirm the draft is cleared.
5. Open the current-student action and confirm login protection still applies.
6. Confirm existing `/program-selector`, `/db-progress`, `/transfer-analysis`, and `/admin` behavior is unchanged.

## 9. Deferred to later stages

Phase 1 does not yet rank programs or make academic claims. The following remain explicitly deferred:

- reviewed career-to-major and skill-to-major mappings;
- program explanations and official source links;
- prior-learning/CPL questions and referrals;
- four-year transfer recommendations;
- authenticated major-change what-if planning;
- guided CUNY Global Search handoff;
- downloadable pre-advisement summary and email referral;
- admin review, versioning, and publishing controls; and
- privacy-safe aggregate analytics.

## 10. Recommended next stage

Phase 2 should introduce a source-backed career taxonomy and deterministic recommendation service. Every relationship must have an official source, review status, reviewer, and review date. Generative AI may later explain reviewed matches, but it must not invent them.

Two intern-sized tasks accompany this implementation:

1. prepare a reviewed starter career/skills dataset for Data Analyst and BMCC Computer Science; and
2. add end-to-end browser accessibility and persistence coverage for the public intake.

Both tasks should arrive through pull requests and must not modify protected production data directly.
