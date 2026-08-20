# CUNY Beyond - Phase 2 Implementation Record

**Reviewed career taxonomy and explainable program matching**  
Version 1.0 - August 2026

## 1. Stage outcome

Phase 2 turns the anonymous intake into a working, source-backed program exploration tool. A student can enter a supported career goal, select skills, receive up to three reproducible BMCC recommendations, understand every score component, open official sources, and enter the existing interactive degree planner without selecting the program again.

The matching engine is deterministic. Generative AI does not create, rank, or alter career-to-program relationships.

## 2. Implemented data architecture

Four relational tables were added:

- `careers` - normalized career identity, aliases, pathway type, source, review date, and active status;
- `skills` - reusable controlled skills;
- `career_skills` - many-to-many career and skill relationships; and
- `program_careers` - reviewed program relationships, evidence level, points, explanation, sources, and review date.

The existing numeric `Program.id` remains the foreign key. CSV imports refer to institution plus program code so campus-scoped program identity is preserved during seeding.

Seed sources:

- `docs/cuny_beyond_skills.csv`
- `docs/cuny_beyond_careers.csv`
- `docs/cuny_beyond_program_careers.csv`

Seeding is idempotent. It updates stable career and skill records, rebuilds managed relationships, rejects unknown references, and runs only after program curricula have been seeded.

## 3. Curated starter dataset

The stage includes:

- 12 reusable student-facing skills;
- Data Analyst with aliases and five reviewed skills;
- 23 normalized Computer Science career-family entries supplied by the BMCC program page;
- cleaned, complete occupational names rather than truncated labels;
- 26 program-career mappings; and
- official source URLs and review dates for every record.

Data Analyst currently produces three reviewed BMCC starting points:

1. Data Science A.S. - strong direct evidence;
2. Computer Science A.S. - related computing and analytic evidence; and
3. Computer Information Systems A.A.S. - exploratory applied-systems evidence.

The differences are visible in the scoring and evidence labels. The UI does not present all three as equivalent.

Official starter sources:

- BMCC Data Science: https://www.bmcc.cuny.edu/academics/departments/math/data-science/
- BMCC Data Science career announcement: https://www.bmcc.cuny.edu/news/math-departments-new-data-science-program-prepares-graduates-for-high-demand-careers-in-science-business-and-more/
- BMCC Computer Science: https://www.bmcc.cuny.edu/academics/departments/cis/computer-science/
- BMCC Computer Information Systems: https://www.bmcc.cuny.edu/academics/departments/cis/computer-information-systems-cis/

## 4. Matching behavior

Career resolution normalizes punctuation, capitalization, and spacing, then checks the reviewed career name and aliases. It supports phrases such as:

```text
I want to become a data analyst
software engineer
BI analyst
systems analyst
```

Default scoring:

```text
Reviewed career-to-program relationship     38-50 points
Each matching selected skill                    6 points
Maximum recommendations shown                       3
Minimum evidence threshold                         38
```

The career points reflect the reviewed evidence level. Skill points reward overlap between the student's selected skills and the matched career profile. Stable tie-breaking uses program name and program code.

Administrators can adjust safe deployment-wide scoring bounds:

```text
CUNY_BEYOND_SKILL_POINTS=6
CUNY_BEYOND_MINIMUM_SCORE=38
```

The service excludes inactive mappings, inactive careers, low-evidence results, and every program without a populated curriculum.

## 5. Public API

Endpoint:

```text
POST /api/db/cuny-beyond/recommendations
```

Request:

```text
{
  "career_goal": "I want to become a data analyst",
  "skills": ["Analyzing data", "Working with numbers"]
}
```

The server limits the career goal to 240 characters and skills to five. Results include:

- resolved reviewed career;
- top recommendations;
- total score and career/skill components;
- matched skills;
- evidence and advising labels;
- plain-language explanation;
- review date;
- official evidence source;
- institution, program, degree, and catalog metadata; and
- official BMCC program URL.

An unsupported goal returns a safe no-match response and examples. It does not invent a program relationship.

## 6. Results experience

The fifth intake step now includes **Find my BMCC program matches**. Each result card shows:

- program and degree name;
- department and catalog year;
- fit points;
- strong, related, or exploratory evidence;
- selected skills that contributed points;
- a plain-language reason;
- exact scoring components;
- source and review date;
- official BMCC program page; and
- **Open interactive degree planner**.

Opening the planner writes the selected campus, program, catalog year, and CUNY Beyond origin into the existing `selectedProgramContext` browser session. The current degree-progress page therefore opens the correct curriculum without program reselection.

## 7. Verification results

Focused Phase 1 and Phase 2 tests:

```text
11 passed
```

Full repository unit suite:

```text
296 passed, 1 skipped
```

Isolated production-style seed:

```text
24 careers
26 program mappings
database seed completed
```

Real API smoke test for Data Analyst plus three skills:

```text
HTTP 200
Data Science A.S.                  68
Computer Science A.S.              62
Computer Information Systems A.A.S. 56
```

The test suite also verifies unique IDs, valid skill references, official HTTPS sources, existing populated program references, stable ranking, threshold filtering, empty-curriculum filtering, and degree-planner handoff.

## 8. Deployment and rollback

No separate service is required. The normal deployment seed creates the new tables and imports the reviewed CSV records.

Recommended variables:

```text
CUNY_BEYOND_ENABLED=true
CUNY_BEYOND_SESSION_TTL_HOURS=24
CUNY_BEYOND_SKILL_POINTS=6
CUNY_BEYOND_MINIMUM_SCORE=38
```

To hide the public experience while retaining the data, set `CUNY_BEYOND_ENABLED=false` and redeploy. Existing authenticated advising routes do not depend on the new tables.

## 9. Scope boundary and remaining work

Phase 2 is a functional starter taxonomy, not a complete career catalog. It does not yet include:

- all BMCC programs and career families;
- student-specific transfer scoring;
- education-level warnings;
- completed-course or CPL scoring;
- an admin mapping editor;
- comparison/download actions in the public results;
- prior-learning screening;
- CUNY Global Search schedule handoff; or
- advising referral storage.

These remain independent future stages. Additional career-family research can proceed in parallel without blocking CPL, transfer, schedule, or referral architecture.

## 10. Intern participation model

Intern work should save research and regression time without sitting on the critical path.

Appropriate parallel tasks:

- expand reviewed career aliases and occupational families from official sources;
- prepare new program-career CSV batches using the existing schema;
- audit source freshness and broken links;
- add accessibility/browser regression scenarios;
- validate controlled skills for consistency; and
- prepare source summaries for professor review.

Core schema, scoring contracts, authorization, admin publishing, privacy boundaries, and stage integration remain lead-developer responsibilities.
