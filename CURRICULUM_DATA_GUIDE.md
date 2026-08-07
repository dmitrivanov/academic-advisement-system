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

### 12. Review the diff and open a draft PR

```bash
git status
git diff --check
git diff -- docs/ds_as_courses.csv docs/ds_as_sources.md
git add docs/ds_as_courses.csv docs/ds_as_sources.md
git commit -m "Add BMCC Data Science curriculum"
git push -u origin intern/issue-24-ds-as-curriculum
```

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
- `exclude_course_codes` to remove otherwise approved courses;
- program-specific required credits or course count.

Use pipe-separated course codes in both adjustment columns. Do not edit the base
Pathways pool to enforce a restriction that applies to only one major.

The database seeder materializes derived groups after loading the shared Pathways
groups and before importing major curricula.
