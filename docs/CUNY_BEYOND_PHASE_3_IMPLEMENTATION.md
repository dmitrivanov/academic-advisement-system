# CUNY Beyond - Phase 3 Implementation Record

**Safe Credit for Prior Learning screening and preparation**  
Version 1.0 - August 2026

## 1. Stage outcome

Phase 3 adds a source-backed Credit for Prior Learning (CPL) screening step to the public CUNY Beyond journey. Students can identify potentially relevant prior education and experience, receive nonbinding preparation guidance, see program-specific notes where reviewed information exists, and build a document checklist for an official BMCC evaluation.

The feature never claims credit has been earned, never marks a course completed, and never subtracts credits from a degree plan.

## 2. What the student can do

The intake now asks whether any of the following may apply:

- previous college coursework;
- AP, CLEP, IB, AICE, DSST, DLPT, or other recognized examinations;
- ACE- or NCCRS-reviewed learning;
- employer, union, industry, or continuing-education training;
- military education, training, or examinations;
- licenses and professional certifications;
- biliteracy or language proficiency; and
- portfolio or documented experiential learning.

Students may select more than one category. **Not sure** creates a general preparation path. **None of these** is mutually exclusive and lets the student continue without CPL suggestions.

After program recommendations load, CPL results appear in a separate section. Each result provides:

- the label **Possible CPL opportunity - evaluation required**;
- a plain-language description;
- documents or evidence to gather;
- the official next step;
- source and review date;
- selected-program guidance when available; and
- a combined document checklist.

## 3. Official policy boundary

BMCC states that students must provide documentation for evaluation and that CPL depends on the degree program and residency requirements. CUNY policy states that faculty and campus officials determine equivalency and program applicability.

The interface therefore displays this mandatory disclaimer:

```text
These are possible CPL opportunities only. BMCC must evaluate official
evidence, determine course equivalency and degree applicability, and award
any credit. Nothing here changes remaining credits or degree totals.
```

Official sources:

- BMCC Credit for Prior Learning: https://www.bmcc.cuny.edu/admissions/apply-now/credit-for-prior-learning-cpl/
- BMCC Transfer Students: https://www.bmcc.cuny.edu/admissions/transfer-students/
- CUNY Credit for Prior Learning policy: https://www.cuny.edu/academics/academic-policy/credit-prior-learning/

## 4. Data architecture

Two relational tables were added:

- `cpl_types` - code, name, description, evidence requested, next step, official source, review date, publishing status, and active status; and
- `program_cpl_guidance` - program-specific guidance, evidence, official source, review date, and publishing status.

Seed files:

- `docs/cuny_beyond_cpl_types.csv`
- `docs/cuny_beyond_program_cpl_guidance.csv`

The seed is idempotent, rejects unknown program or CPL references, and imports only after populated programs exist. Phase 3 seeds eight published CPL types and six reviewed notes covering standardized examinations and previous college coursework for Data Science, Computer Science, and Computer Information Systems.

## 5. Public API

Endpoint:

```text
POST /api/db/cuny-beyond/cpl-screening
```

Request example:

```text
{
  "selections": ["standardized-exams", "previous-college-credit"],
  "program_codes": ["DS_AS", "CS", "CIS"]
}
```

The server:

- accepts at most nine unique screening selections and three program codes;
- validates every CPL identifier;
- returns only active, published CPL types and guidance;
- treats **None** as an explicit no-op;
- supports a safe **Not sure** response;
- never accepts a proposed number of credits;
- never queries or edits course-completion state; and
- never alters degree totals.

## 6. Program-specific guidance

Program-specific notes are used only when an official source supports a useful preparation detail.

Examples:

- BMCC publishes AP Computer Science A as a possible CSC 110 equivalency; official score evaluation and degree applicability are still required.
- BMCC publishes AP Calculus and Statistics equivalencies that may be relevant to quantitative programs; the college decides their applicability.
- BMCC states that technical transfer courses require departmental approval, so computing and technical syllabi should be retained.

The UI does not convert these examples into completed courses or guaranteed equivalencies.

## 7. Privacy and safety

Phase 3 stores only selected category codes in the same expiring anonymous browser draft introduced in Phase 1. It does not ask for:

- transcript uploads;
- examination scores;
- credential numbers;
- military documents;
- employer names;
- portfolio files;
- student ID;
- name; or
- email.

Documents are listed as a future checklist for an official channel. They are not uploaded to this prototype.

## 8. Verification results

Focused CUNY Beyond tests:

```text
16 passed
```

Full repository unit suite:

```text
296 passed, 1 skipped
```

Production-style isolated seed:

```text
8 CPL types
6 program guidance records
database seed completed
```

Real API smoke test:

```text
HTTP 200
standardized-exams          3 program notes
previous-college-credit     3 program notes
2 document-checklist items
```

Automated checks cover published status, required content, HTTPS sources, valid program references, valid type references, unknown-selection rejection, mutually exclusive **None**, persistence fields, result separation, disclaimer language, and the prohibition against changing degree totals.

## 9. Deployment and rollback

No separate service or migration command is required. The normal seed creates and populates the new tables.

The existing public feature flag controls all CUNY Beyond stages:

```text
CUNY_BEYOND_ENABLED=true
```

Setting it to `false` hides the public route while leaving existing authenticated advisement features unchanged.

## 10. Remaining work

Phase 3 provides preparation guidance rather than a CPL award estimator. Later work may include:

- professor-reviewed guidance for additional programs;
- an authenticated admin editor and publishing history;
- official exam-equivalency imports with effective dates;
- consented referral delivery;
- transfer and prior-credit status tracking after official evaluation; and
- CPL freshness audits.

The next main implementation phase is the intentional current-student major-change workflow. Intern tasks can expand source-backed CPL guidance or audit official links without blocking that architecture.
