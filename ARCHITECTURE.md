# Application Architecture

This document describes the current system, the Smart Onboarding integration, and a
safe incremental path toward a clearer advising architecture. Production deploys
from `main`, so architectural work should be divided into independently testable
pull requests rather than performed as a single rewrite.

## Current request flow

```text
Browser
  -> FastAPI application (`faq_fallback_api.py`)
       -> page routes and authentication
       -> database API router (`api_db_routes.py`)
            -> SQLAlchemy models (`models.py`)
            -> database connection (`database.py`)
       -> optional Gemini advisor requests
  -> HTML/CSS/JavaScript pages (`frontend/`)
       -> REST requests to `/api/db/...`
       -> per-tab workflow state in `sessionStorage`
```

`seed_database.py` builds curriculum records from CSV files in `docs/`. Local
development defaults to SQLite. Render supplies PostgreSQL through `DATABASE_URL`.

## Advising entry paths

The established selector remains available and unchanged:

```text
Campus + program -> prior-course question -> Academic Progress
```

Smart Onboarding is an alternative deterministic entry path:

```text
Prior college coursework?
  |-- No
  |     -> advising goal
  |     -> desired campus/program
  |     -> timeline/workload
  |     -> Academic Progress with locked completed-course selection
  |
  |-- Yes, at CUNY
  |     -> continue major / change major / transfer
  |     -> current or desired campus/program
  |     -> completed-course input preference
  |     -> Academic Progress
  |          -> semester plan, Major Change, or Transfer Analysis
  |
  `-- Yes, outside CUNY
        -> transfer goal
        -> desired CUNY campus/program
        -> completed-course input preference
        -> Academic Progress -> Transfer Analysis
```

The wizard uses choices and selectors only. It does not call an AI model. AI is
reserved for explaining or refining a plan after validated structured context and
curriculum data are available.

## Frontend state contracts

The pages currently share transient state through browser `sessionStorage`.

### `selectedProgramContext`

Existing contract used to load Academic Progress:

```json
{
  "institutionCode": "BMCC",
  "institutionName": "Borough of Manhattan Community College",
  "programCode": "CS",
  "programName": "Computer Science",
  "catalogYear": "2026-2027",
  "studentStatus": "first_semester",
  "onboardingSource": "smart"
}
```

The legacy selector continues to write its existing fields. Smart Onboarding adds
`onboardingSource` so consumers can opt into the extended context safely.

### `smartOnboardingContext`

Versioned context produced only by Smart Onboarding:

```json
{
  "version": 1,
  "source": "smart_onboarding",
  "academicHistory": "cuny",
  "advisingIntent": "change_major",
  "inputMethod": "manual",
  "planningMode": "manual",
  "requestedPlanningMode": "manual",
  "targetSemesters": 4,
  "workloadPattern": "balanced"
}
```

Academic Progress uses this record to customize its guidance and planner defaults.
It is also included as structured context when the student explicitly asks the AI
advisor a question. The onboarding interview itself consumes no AI tokens.

### `transferSnapshot`

Created by Academic Progress after completed-course selection. Transfer Analysis
uses it as its source-program and completed-course input.

## Why every branch currently passes through Academic Progress

Major-change and transfer calculations require a normalized set of completed
courses. Academic Progress already owns that selection and creates
`transferSnapshot`. Routing directly from onboarding to Transfer Analysis would
either lose coursework or duplicate this responsibility. A future transcript
pipeline should normalize and confirm imported courses before producing the same
snapshot contract.

## Transcript upload boundary

Transcript upload is intentionally displayed as planned, not active. A safe
implementation requires:

1. A restricted upload endpoint and file-size/type validation.
2. Text extraction/OCR isolated from curriculum matching.
3. Institution-aware course-code normalization.
4. Equivalency matching with confidence and provenance.
5. A student confirmation screen before any course is marked completed.
6. Retention and deletion rules for student records and uploaded files.

AI may suggest uncertain matches, but it must not silently award course credit.

## Recommended incremental revision

### Phase 1 — stabilize contracts

- Add browser-level tests for every onboarding branch.
- Define and validate versioned frontend context objects.
- Add a clear “resume or start over” rule for interrupted onboarding.
- Measure exits and failures without storing sensitive student data.

### Phase 2 — separate frontend modules

- Move shared API and storage functions out of the large HTML files.
- Extract Smart Onboarding into its own JavaScript and CSS modules.
- Extract the progress calculator and semester planner into testable modules.
- Keep the existing page URLs and backend APIs stable during extraction.

### Phase 3 — normalize academic records

- Scope course identity by institution instead of relying on course code alone.
- Introduce a normalized student-course record with source institution, grade,
  credits, term, and verification status.
- Make manual entry, transcript import, and transfer equivalencies produce the same
  normalized record type.

### Phase 4 — persistent advising sessions

- Replace browser-only state with authenticated advising sessions when privacy and
  retention requirements are established.
- Store consent, provenance, and confirmation state separately from AI conversation
  logs.
- Allow students to resume a saved plan across devices.

## Important current constraints

- Frontend pages contain substantial inline CSS and JavaScript, which makes isolated
  testing and reuse difficult.
- Browser session state disappears when the session ends and is not a student record.
- Course codes are not yet fully institution-scoped.
- CSV seeding refreshes curriculum data and must not be casually run against the
  production database.
- AI output is advisory and must not override official curriculum, prerequisite, or
  transfer-equivalency data.
