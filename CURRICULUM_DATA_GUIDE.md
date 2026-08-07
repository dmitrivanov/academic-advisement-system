# Curriculum Data Contribution Guide

This guide explains how to add one academic major without changing application code
or database models. It is intended for supervised curriculum-data contributions.
Every major must be submitted in its own issue, branch, and pull request.

## Accuracy and approval boundary

Curriculum CSV files drive degree progress, prerequisite locking, semester plans,
and transfer comparisons. Treat them as academic rules, not ordinary content.

The contributor may research, transcribe, validate, and test data. The project
maintainer must review and approve all interpretations before merging, especially:

- elective and “choose one” requirements;
- prerequisites that are not themselves part of the degree;
- STEM variants and credits counted in more than one published area;
- catalog-year differences;
- transfer or articulation claims.

Never guess. Record an ambiguity in the source notes and pull request instead.

## Allowed sources

Use sources in this order:

1. The official college program map for the applicable catalog year.
2. The official college program-requirements page.
3. Official college course listings for titles, credits, and prerequisites.
4. The official CUNY catalog or CUNY Global Search when college documentation is
   incomplete.

Do not use search-result summaries, commercial course websites, student plans,
unofficial advising pages, or AI-generated curriculum information as evidence.

Use the effective year printed by the source. Do not label a curriculum `2026`
merely because the file is being created in 2026.

## One-major workflow

### 1. Confirm the assigned program identity

Find the program in `docs/programs.csv` and copy its values exactly:

- `institution_code`
- `department_code`
- `program_code`
- `program_name`
- `degree_type`

If the program is missing or disagrees with the official source, stop and comment on
the issue. Do not invent a new code or edit `programs.csv` without approval.

### 2. Create a branch

Use the issue number and program code:

```bash
git fetch upstream
git switch -c intern/issue-24-ds-as-curriculum upstream/main
```

### 3. Copy the blank template

For a program with code `DS_AS`:

```bash
cp docs/templates/curriculum_courses_template.csv docs/ds_as_courses.csv
cp docs/templates/curriculum_source_notes_template.md docs/ds_as_sources.md
```

The curriculum filename must be the lowercase program code followed by
`_courses.csv`. The seeder discovers files matching `docs/*_courses.csv`.

Do not start from the legacy `cis_courses.csv` or `cnt_courses.csv` format. New
programs must use the full template.

### 4. Record source notes before entering data

In the source-notes file, record:

- direct official URLs;
- page/document titles;
- effective catalog year;
- date accessed;
- published program-credit total;
- unresolved questions and assumptions.

If the program map is a PDF, link the official PDF. Do not copy a third-party PDF.
Only add the PDF to the repository when the issue explicitly requests it and the
official source permits redistribution.

### 5. Convert the official requirements into groups

Use these supported `group_type` values:

| Group type | Meaning | Default order |
| --- | --- | ---: |
| `common_core` | Required Common Core | 10 |
| `flexible_core` | Flexible Core / Pathways | 20 |
| `program_required` | Required courses for the major | 30 |
| `program_elective` | Approved major electives | 40 |

Use the official group name as `group_name`. Repeat the same `group_name`,
`group_type`, `required_credits`, and `display_order` on every course row in that
group. Those values must remain identical within a group.

The sum of the distinct group requirements should reconcile to the official program
total. Most associate degrees total 60 credits, but use the official source rather
than forcing a total.

### 6. Fill every column

| Column | Required content |
| --- | --- |
| `institution_code` | Official code such as `BMCC` |
| `department` | Official department name |
| `department_code` | Code already used in `docs/programs.csv` |
| `program_code` | Exact code from `docs/programs.csv` |
| `program_name` | Exact official program name |
| `degree_type` | `AA`, `AS`, `AAS`, `BA`, `BS`, `BBA`, or approved certificate type |
| `catalog_year` | Effective year, such as `2024-2025` |
| `group_name` | Published requirement-area name |
| `group_type` | One of the four supported values above |
| `required_credits` | Credits required from the group, not the sum of all elective options |
| `display_order` | Usually 10, 20, 30, or 40 |
| `course_code` | Uppercase official code, such as `MAT 301` |
| `title` | Official course title |
| `credits` | Whole-number course credits supported by the current seeder |
| `prerequisites` | Structured prerequisite codes, or blank |
| `alternatives` | Equivalent ways to satisfy this course row, or blank |
| `choice_group_code` | Approved choice-group identifier, or blank |
| `source` | Direct official HTTPS URL supporting the row |

Do not leave identity, group, course, credit, catalog, or source fields blank.

### 7. Encode prerequisites correctly

The current seeder uses:

- `|` for AND;
- lowercase ` or ` for OR.

Examples:

```text
MAT 301
CSC 111|MAT 301
CSC 110 or CSC 111
ENG 201|MAT 200 or MAT 301
```

The final example means `ENG 201` AND either `MAT 200` OR `MAT 301`.

Only enter course codes in these fields. Placement, GPA, permission, co-requisite,
minimum-grade, and departmental-admission rules are not fully modeled. Record those
rules in source notes and flag them for maintainer review rather than translating
them inaccurately.

If a prerequisite course is not included in the program CSV, the validator warns
because the progress UI may not give the student a way to mark it complete.

### 8. Model choices cautiously

Do not list every elective as individually required. When a source says “choose one”
or “choose N credits,” ensure `required_credits` reflects only the required amount.

The current data model has limited support for complex rules such as:

- one course from each of several elective subgroups;
- an approved sequence plus an additional course;
- credits that satisfy both a Pathways area and a program requirement;
- alternatives selected according to placement or specialization.

List the official options, use an existing approved `choice_group_code` only when its
definition is present in the project, and explain the rule in source notes. Do not
create a new choice-group code without approval. The validator reports when listed
course credits exceed group-required credits so the reviewer can inspect the rule.

#### Published OR-course pairs

When the official curriculum prints named courses separated by `OR`, add every named
course as its own row in the same requirement group. Make the `alternatives`
relationship reciprocal so the progress screen renders one visual "Choose one" card:

```text
PSY 240 ... alternatives: PSY 250
PSY 250 ... alternatives: PSY 240
```

Do not preserve a published alternative only as hidden text on another course row.
Selecting one option satisfies the card and hides the other option until the student
chooses to change the selection.

A course may legitimately appear in both a required OR pair and an official elective
pool. Repeat it in both groups when the source does. The progress calculation allocates
the completion to the required group first, preventing the same completion from also
satisfying elective credits. A separately completed alternative may count as an
elective when the official pool permits it.

Use a descriptive placeholder only when the source itself publishes an open category
such as `XXX xxx - Liberal Arts Elective` or `General Elective`. Do not use a
placeholder instead of a finite list of named OR options. Every open-category row must
also set `choice_group_code`; otherwise it renders as a fictitious checkbox rather than
a course selector. Reuse `BMCC_GENERAL_ELECTIVE` for any-credit-bearing BMCC elective,
`BMCC_LIBERAL_ARTS_ELECTIVE` for a liberal-arts elective, and
`BMCC_MODERN_LANGUAGE_CONTINUATION` for the second course in a language sequence.
Selectors accept multiple courses and apply their credits up to the placeholder's
published credit requirement.

### 9. Validate before seeding

Run the validator on the new file:

```bash
python3 scripts/validate_curriculum_csv.py docs/ds_as_courses.csv
```

Expected successful result:

```text
OK      docs/ds_as_courses.csv — ... curriculum rows validated.

Validated 1 file(s): 0 error(s), 0 warning(s).
```

Errors must be fixed. Warnings must either be fixed or explained in the source notes
and pull request. To make warnings return a failing exit status during a final audit:

```bash
python3 scripts/validate_curriculum_csv.py --strict docs/ds_as_courses.csv
```

You can inspect all existing major files with:

```bash
python3 scripts/validate_curriculum_csv.py --all
```

Some older project curricula produce legacy-schema or modeling warnings. Do not
modify those unrelated files as part of a new-major issue.

### 10. Seed a local database

After the validator reports no errors:

```bash
python3 seed_database.py
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

This uses the local SQLite database unless `DATABASE_URL` is set. Never run seeding
commands against Render or another production database.

### 11. Test the program in the browser

Verify all of the following:

1. The program can be selected under the correct campus.
2. The program name, degree type, and catalog year are correct.
3. Every requirement group appears once.
4. Group-required credit totals match the official source.
5. Required courses are not treated as optional.
6. Elective options are not all treated as required.
7. Courses with unmet prerequisites are locked.
8. Selecting prerequisites unlocks the correct later courses.
9. The semester planner produces the requested number of semesters.
10. No new error appears in the browser console or server terminal.

Attach screenshots of Program Selector, Academic Progress, and the semester plan to
the pull request.

### 12. Programs with a standard and an alternate degree map

Some majors publish two official maps for the same catalog year: a standard
four-semester (two-year) sequence and a lighter-load alternate, commonly five
semesters. Treat the standard four-semester map as the default planning
sequence. Record the alternate as a secondary pathway rather than a second
program — both maps describe the same 60-credit requirement set, just paced
differently. Compare both maps course-by-course; if a course only appears on
one map (for example, a placement-gated alternate like an intensive
composition course), do not add it as an interchangeable equivalent — record
it as a placement limitation in source notes instead (see step 7 and the
"Encode prerequisites correctly" rules).

### 13. Retain official degree-map PDFs (only when the issue permits)

By default, link to the official source rather than copying it. Only add a
PDF to the repository when the assigned issue explicitly requests retaining
it and the official source permits redistribution.

When retention is permitted:

1. Save each official PDF under `docs/degree_maps/` using a descriptive,
   stable filename that encodes the institution, program, map variant, and
   catalog year, for example `bmcc_mathematics_2_year_2025_2026.pdf` and
   `bmcc_mathematics_5_semester_2025_2026.pdf`.
2. Do not rename or overwrite another program's retained PDF.
3. Record both source PDF URLs and both retained repository paths in the
   source-notes file.

### 14. Create and register a degree-map JSON file

A degree-map JSON file drives official semester-sequencing guidance and
source-PDF links shown on the Academic Progress screen. It is optional — add
one only when the issue asks for official sequencing guidance or retained
PDF links.

1. Create `docs/bmcc_<program>_degree_map_<catalog_year>.json` (for example
   `docs/bmcc_ds_as_degree_map_2024_2025.json`), following the structure of
   an existing file such as `docs/bmcc_mat_degree_map_2025_2026.json`.
2. Required top-level fields: `institution_code`, `program_code`,
   `program_name`, `degree_type`, `catalog_year`, `default_semesters`,
   `total_credits`, `source_pdf`, `faculty_override_note`, `semesters`
   (an array with `number`, `target_credits`, `course_codes`, and optionally
   `program_elective_slots`), and `sequence_notes` (a plain-language list of
   the same placement rules, footnotes, and limitations recorded in source
   notes).
3. `course_codes` in each semester must use the exact `course_code` values
   from the program's curriculum CSV, including placeholder codes such as
   `FC-INDIVIDUAL` — not the names of specific pool courses like `SOC 100`,
   unless that specific course is the only literal, non-placeholder row in
   the CSV (see step 8 and step 15 below).
4. When retaining more than one official PDF (step 13), add a `source_pdfs`
   array of `{"label": ..., "url": ...}` objects alongside the single
   `source_pdf` field. `source_pdf` keeps existing single-PDF consumers
   working; `source_pdfs` is what the Academic Progress screen renders as
   labeled links. Always add both fields together — do not remove
   `source_pdf` to avoid breaking programs that only ever had one map.
5. When an alternate pathway exists (step 12), add an `alternate_pathways`
   array with a `name` and `semester_credit_targets` list. The values are
   advisory pacing targets, not hard constraints — they do not need to sum
   exactly to the literal credits of every course listed in that semester
   when a group's published total absorbs credits across categories (see
   the STEM-variant note in step 15).
6. Register the new file in `frontend/db_progress_graph.html` by adding one
   line to the `mapFiles` lookup inside `loadOfficialDegreeMap()`:
   `PROGRAM_CODE: "/docs/bmcc_<program>_degree_map_<catalog_year>.json"`.
   This is the only application-code change a curriculum-data issue should
   make. The source-PDF links, "Official maps" label, safe
   `target="_blank" rel="noopener"` attributes, and mobile layout are
   already generic and apply automatically to any program with a
   `source_pdfs` array — do not duplicate that rendering logic per program.

### 15. Use `program_choice_group_adjustments.csv` for major-specific footnotes

Many degree maps restrict a shared Pathways category (Common Core or
Flexible Core) to a specific course, or add a second required slot in a
category that is normally a single course. Before writing a restriction,
classify the footnote:

- **A stated requirement or restriction** ("students are required to take
  X," "X satisfies this area," a specific course shown on every version of
  the map with no other option offered) — add a row to
  `docs/program_choice_group_adjustments.csv` with a program-prefixed
  `derived_group_code` (for example `MAT_AS_LIFE_PHYSICAL`,
  `ECO_AA_MATH_QUANT`) referencing the shared `base_group_code`, and use
  that derived code — not the base code — as the `choice_group_code` on the
  matching curriculum-CSV row.
- **An advising recommendation** ("students are strongly encouraged to
  take X," "consult an advisor") — do not restrict the shared pool. Use the
  base group code directly (for example `FC_INDIVIDUAL`, `FC_US_EXPERIENCE`)
  with a generic placeholder course code, and record the suggested default
  course in source notes instead. Restricting a pool to a merely-recommended
  course accidentally makes an elective mandatory (see step 8).

If a major requires more credits in a Flexible Core category than the
standard single-course allocation (for example two U.S. Experience in Its
Diversity courses instead of one), add multiple curriculum-CSV rows that
share the same `choice_group_code` with distinct, unique `course_code`
values (for example `FC-US-EXP-1` and `FC-US-EXP-2`). Each row becomes an
independent selectable slot in the progress UI; the underlying shared pool
is unaffected.

If a footnote describes a STEM-variant course (4 credits) filling a
nominally 3-credit Common Core or Flexible Core slot, and the official
source explains that the resulting excess credit rolls into a General
Elective or similar catch-all requirement, do not attempt to move credits
between groups — the current schema does not support that. Model the
catch-all requirement as a single `program_elective`-type row sized to the
full published total (see `MAT-AS-GENERAL` / `ECO-AA-GENERAL` for the
pattern) and explain the mechanism in source notes.

Never invent a new shared Pathways choice-group (a new pool of courses
usable by multiple future majors) without maintainer approval. If a
footnote describes an open-ended pool that has no existing shared group code
(for example "any History course, or one course from several other
departments"), add a single documented placeholder row with no
`choice_group_code`, and flag it under "Ambiguities requiring maintainer
review" in source notes rather than guessing at pool membership.

### 16. Add focused automated tests for the new curriculum

Add a test file under `tests/` named for the program (for example
`tests/test_ds_as_curriculum.py`). Follow the structure of an existing
curriculum test file. At minimum, cover:

1. `validate_file(...)` from `scripts/validate_curriculum_csv.py` returns no
   errors for the new CSV.
2. Every row has the exact program identity and catalog year.
3. The distinct group `required_credits` values reconcile to the official
   published total.
4. Key required courses (and their prerequisites) are present with the
   correct group and credits.
5. Elective groups list more credits than `required_credits`, and required
   core courses are excluded from the elective pool, so a choice cannot be
   mistaken for a mandatory list.
6. Program-specific `program_choice_group_adjustments.csv` rows match what
   the degree map actually restricts.
7. No duplicate `(group_name, course_code)` rows, and every `source` URL is
   a well-formed official HTTPS URL.
8. If a degree-map JSON file was added (step 14): both the default and any
   alternate sequence total the published credits, and any retained PDFs
   (step 13) are both present on disk and referenced in `source_pdfs`.
9. `frontend/db_progress_graph.html` registers the new program in
   `mapFiles`, if a degree-map JSON file was added.

When reading `frontend/db_progress_graph.html` or other repository text
files from a test, always pass `encoding="utf-8"` explicitly. Relying on the
platform default encoding fails on Windows, where Python's default text
encoding is not UTF-8 and the file contains non-ASCII punctuation elsewhere
in the page.

### 17. Review the diff and open a draft PR

```bash
git status
git diff --check
git diff -- docs/ds_as_courses.csv docs/ds_as_sources.md
git add docs/ds_as_courses.csv docs/ds_as_sources.md
git commit -m "Add BMCC Data Science curriculum"
git push -u origin intern/issue-24-ds-as-curriculum
```

If the issue also asked for a degree-map JSON file, retained PDFs, Pathways
adjustments, or automated tests (steps 13-16), stage only the additional
files those steps actually created — for example
`docs/bmcc_ds_as_degree_map_2024_2025.json`,
`docs/degree_maps/bmcc_data_science_2_year_2024_2025.pdf`,
`docs/program_choice_group_adjustments.csv`,
`frontend/db_progress_graph.html`, and `tests/test_ds_as_curriculum.py`.
Review `git diff -- frontend/db_progress_graph.html` line by line — it should
contain only the one new `mapFiles` entry, nothing else.

The pull request must identify the issue, official sources, effective year, validator
result, warnings/ambiguities, local seed result, and manual tests. Only the
maintainer merges curriculum data.

## Maintainer review checklist

- Program identity matches `docs/programs.csv` and official sources.
- Catalog year is supported by the cited source.
- Distinct group requirements reconcile to the published program total.
- Course titles and credits match official course listings.
- Prerequisite AND/OR logic is correct.
- External prerequisites can be represented in the current progress UI.
- Elective options are not accidentally made mandatory.
- Choice-group codes already exist and mean what the CSV claims.
- Validator has no errors; every warning is resolved or documented.
- Clean local seeding succeeds.
- Program Selector, progress, prerequisite unlocking, and semester plan were tested.
- The PR changes only the assigned curriculum and its source notes.

## Shared BMCC Pathways groups

Do not copy the complete BMCC Common Core and Flexible Core course lists into every
major CSV. The college-wide pools are maintained once in:

- `docs/pathways_groups.csv` - group metadata;
- `docs/pathways_courses.csv` - approved course membership and official source URL.

A major CSV references a pool by placing its code in `choice_group_code`. The
placeholder course code must still be unique and descriptive, for example
`FC-WORLD-CULTURES`.

When a program permits only a subset of a college-wide pool, add a row to
`docs/program_choice_group_adjustments.csv`. A derived group may use:

- `include_course_codes` as an allow-list;
- `include_subject_codes` as a subject-prefix allow-list for rules such as
  "any ACC, BUS, CIS, CSC, GIS, or MMP course";
- `exclude_course_codes` to remove otherwise approved courses;
- program-specific required credits or course count.

Use pipe-separated course codes in both adjustment columns. Do not edit the base
Pathways pool to enforce a restriction that applies to only one major.

The database seeder materializes derived groups after importing the major curricula
and building broad institutional elective pools. This permits an adjustment to derive
from either a Pathways area or an institutional elective pool. Base and derived group
codes are institution-scoped; BMCC and CCNY memberships must never be mixed.

The adjustment `notes` value is student-facing. Keep it to one short sentence that
explains the major-specific restriction, because the progress screen displays it at
the top of the course-choice modal. The modal globally groups options by subject and
orders each subject by catalog number; do not duplicate presentation groupings in
individual major CSV files.

# Major Constructor workflow

Administrators can open **Admin → Major Constructor** to assemble a curriculum without changing live program data. The constructor is a draft-first companion to the CSV workflow described below.

1. Create a draft and select the campus and department.
2. Enter the program name, code, degree type, catalog year, and official source URL.
3. Add one concentration tab for each independently selectable curriculum. A program with no official concentrations should keep the default `General` tab.
4. Search the canonical course catalog and add courses to Major Requirements, Major Electives, Common Core, or Flexible Core. Each bin displays its current credit total.
5. Add OR alternatives, prerequisites, and any major-specific Core adjustment note. The note must translate the official footnote into student-facing language.
6. Save frequently and create named version snapshots at meaningful review points.
7. Preview and validate. Missing metadata, empty curricula, and missing course references block submission.
8. Submit for review. A reviewer may approve it or request changes. Only an approved draft can be published.
9. Publishing creates new program and requirement records in one database transaction. It refuses to overwrite an existing program with the same department, code, and catalog year.

Draft lifecycle:

```text
draft → in_review → approved → published
                    ↘ changes_requested → in_review
```

Version restore returns an unpublished draft to editable `draft` status. Published records are immutable in this first constructor release; revise them by creating a new draft/catalog version. This prevents rollback from silently changing requirements already used by student records.

The source CSV files remain the repository's reviewable curriculum record. Until constructor export is added, a published constructor curriculum should also be represented in the appropriate CSV files before the next full database reseed. Major-specific Core adjustments are preserved in the draft/version document, but their base-group include/exclude editor and CSV export are a subsequent constructor stage.
