# Curriculum Source Notes: Criminal Justice (A.A.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Criminology and Criminal Justice (CRJ)
- Program code: CRJ_AA
- Program name: Criminal Justice
- Degree type: AA
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-12

Note: `docs/programs.csv` previously listed CRJ_AA's `catalog_year` as `2026`,
not `2025-2026` — the same mismatch already found and corrected for ECO_AA,
HIS_AA, and SOC_AA. Corrected here for the same reason: `seed_database.py`
keys a program by `(department_id, code, catalog_year)`, so the mismatch
would create an orphaned, empty duplicate program row instead of attaching
Criminal Justice's courses to the row `programs.csv` already defines.
Confirmed the seeder's stale-row cleanup removed the old placeholder after
the fix (`Removed stale empty program placeholder: CRJ_AA (2026)`).

## Official sources

1. Program map (two-year)
   - Title: Criminal Justice (CRJ) Two Year Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/t9z2ol91c6xblhh/crj2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_criminal_justice_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Title: Criminal Justice (CRJ) Five Semester Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/6qfy5875mjbzgoi/crj3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_criminal_justice_5_semester_2025_2026.pdf`

3. Program requirements page
   - Title: Criminal Justice (A.A.) - BMCC
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/criminal-justice/criminal-justice/
   - Effective year shown: matches the 2025-2026 degree maps

4. Course listings
   - Criminal Justice: https://www.bmcc.cuny.edu/academics/departments/criminal-justice/course-listings/
   - Mathematics (MAT 150): https://www.bmcc.cuny.edu/academics/departments/math/mathematics-program/
   - Economics (ECO 201): https://www.bmcc.cuny.edu/academics/departments/social-sciences/economics-courses/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Program page "Required Common Core" |
| Flexible Core | 18 | Program page "Flexible Core" |
| Program Requirements | 27 | Both degree maps, "Curriculum Requirements" minus General Elective |
| General Elective | 3 | Program page "Curriculum Requirements" (General Elective line) |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

The program page's "Curriculum Requirements: 30 credits" line is split into
two CSV groups (Program Requirements 27 + General Elective 3 = 30) to keep
the fixed required courses separate from the STEM-excess-credit placeholder,
matching the identical pattern used in `eco_aa_courses.csv`.

Course-level credits in `Required Common Core` sum to 13 (ENG 101 3 + ENG 201
3 + MAT 150 4 + Life and Physical Sciences 3), 1 credit above the group's
published `required_credits` of 12. This is expected: see "STEM excess
credit" below.

## Choices and alternatives

- **Statistics (Common Core, Mathematical and Quantitative Reasoning).** The
  two-year map uses MAT 150 and the five-semester map uses MAT 150.5. Both
  four-credit statistics variants are selectable through
  `CRJ_AA_MATH_QUANT`.
- **Life and Physical Sciences (Common Core).** Footnote: "Please consult
  with an academic or faculty advisor" — advisory language, not a
  restriction. Left as the standard, unrestricted `RC_LIFE_PHYSICAL` pool.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression, first course).**
  Modeled as a literal row, `alternatives=SPE 102`, matching the identical
  pattern already used in `mat_as_courses.csv`, `eco_aa_courses.csv`,
  `his_aa_courses.csv`, and `soc_aa_courses.csv`.
- **Creative Expression, second course.** Footnote: "Select any Creative
  Expression Pathways course except SPE 100 or SPE 102." An explicit
  exclusion. Modeled with a new derived group, `CRJ_AA_CREATIVE` (base
  `FC_CREATIVE`, `exclude_course_codes=SPE 100|SPE 102`), matching the
  identical pattern already used by `MAT_AS_CREATIVE`, `HIS_AA_CREATIVE`,
  and `SOC_AA_CREATIVE`.
- **Individual and Society (SOC 100) / U.S. Experience in Its Diversity
  (POL 100).** Footnotes: "SOC 100 is a prerequisite course for CRJ 102.
  Students are strongly recommended to take SOC 100 to satisfy the
  Individual and Society requirement." / "POL 100 is a pre-requisite course
  for CRJ 200. Students are strongly recommended to take POL 100 to satisfy
  the area of U.S. Experience in Its Diversity." Both are advisory
  ("strongly recommended"), not restrictive requirements, so both Flexible
  Core slots are left as the standard, unrestricted `FC_INDIVIDUAL` /
  `FC_US_EXPERIENCE` pools rather than being locked to SOC 100 / POL 100 —
  matching how Sociology and History treated identically-worded advisory
  footnotes. SOC 100 and POL 100 remain required as prerequisites for CRJ
  102 and CRJ 200 respectively (see "Prerequisite review" below), which is
  a separate, independently-encoded relationship from the Flexible Core
  slot itself.
- **Scientific World, World Cultures and Global Issues.** Both footnoted
  only with advisory "consult an advisor" language. Left as the standard,
  unrestricted shared pools.
- **Modern Language Course.** Footnote: "Students are required to complete
  two semesters of the same Modern Foreign Language in order to graduate,
  one of which can be satisfied in the World Cultures and Global Issues
  requirement." Modeled as a placeholder, `CRJ-AA-MODLANG`, with a new
  derived group `CRJ_AA_MODERN_LANGUAGE` (base `FC_WORLD_CULTURES`,
  restricted to the same continuation-course list already used by
  `WAL_MODERN_LANGUAGE` in `wal_aa_courses.csv` / `wal_jrn_aa_courses.csv`)
  — reusing the identical, already-reviewed course list rather than
  re-deriving it. As with WAL's implementation, the system cannot detect
  that a student's *specific* language course instance was already used to
  satisfy World Cultures, so it cannot prevent double-counting the same
  single course toward both slots. **Flagged for maintainer review**
  (pre-existing limitation, not new to this submission).
- **English Elective or LIN 250 (Forensic Linguistics).** The selector uses
  `CRJ_AA_ENGLISH_OR_LIN` and contains LIN 250 plus the complete cataloged
  300-level ENG pool already audited for the Writing and Literature majors.
- **General Elective / STEM excess credit (3 credits).** Footnote: "A total
  of 3 credits is required for degree completion. Some of these credits may
  be satisfied by taking STEM variant in the Common Core." Only 2 credits
  appear as an explicit "General Elective" line item on the map (Semester
  4). The other credit is the excess generated because MAT 150 is a
  4-credit course filling a nominally 3-credit Common Core slot. Modeled as
  a single 3-credit placeholder, `CRJ-AA-GENERAL`, matching the identical
  pattern and title text already used in `eco_aa_courses.csv`
  (`General Elective or Common Core STEM excess credits`). The current data
  model cannot move credits between groups, so this placeholder represents
  the full published 3-credit requirement as one program-elective-type row
  rather than splitting 2 explicit + 1 implied.

## Prerequisite review

- **CRJ 102 (Criminology).** Official prerequisite (course-listings page,
  quoted exactly): "Prerequisite: SOC 100." Encoded as `SOC 100`. SOC 100 is
  not part of this program's curriculum CSV (only advisory for the
  Individual and Society Flexible Core slot — see "Choices and
  alternatives" above), so the validator is expected to warn about an
  external prerequisite for this row.
- **CRJ 200 (Constitutional Law).** Official prerequisite: "Prerequisite:
  POL 100." Encoded as `POL 100`. Same external-prerequisite pattern as
  CRJ 102/SOC 100 above; expected validator warning.
- **CRJ 201 (Policing) / CRJ 202 (Corrections).** Official prerequisite for
  both: "Prerequisite: CRJ 101." Encoded as `CRJ 101`. Internal to this
  curriculum; no warning expected. Note the degree maps' footnote 1
  ("CRJ 101 is a prerequisite course to all 200-level CRJ courses") is a
  looser, generic summary — the course-listings page shows CRJ 200's own
  specific prerequisite is POL 100, not CRJ 101, so the specific per-course
  catalog listing was used over the map's generic footnote wording.
- **CRJ 204 (Criminal Justice and the Urban Community).** Official
  prerequisite (course-listings page, quoted exactly): "Prerequisite: CRJ
  101 and CRJ 102." Encoded as `CRJ 101|CRJ 102`. Both degree map PDFs and
  the course-listings page agree on this exact wording (confirmed by
  reading the actual PDF text directly, not just the degree-map images —
  an initial image-based read misattributed one footnote as "CRJ 101 and
  CRJ 200," which the source PDF itself does not say).
- **CRJ 204's official title discrepancy.** Both degree maps print this
  course as "Crime and Justice in the Urban Community," but the official
  course-listings page (quoted exactly, verified twice) prints "Criminal
  Justice and the Urban Community." Per lesson 2 in the curriculum-data
  feedback notes (titles must match the official course listing, not an
  interpretive or map-specific variant), the course-listings page's title
  was used. **Flagged for maintainer review** in case this reflects a
  genuine title change the degree maps haven't caught up to yet.
- **LIN 250 (Forensic Linguistics).** Could not locate LIN 250 on the
  English department's or Modern Languages department's official
  course-listings pages to independently verify a prerequisite or exact
  department home. Title and credits are sourced from the degree maps only
  (both agree: "Forensic Linguistics," 3 credits). No prerequisite was
  encoded (left blank) rather than guessing. **Flagged for maintainer
  review.**
- **ENG 100.5 (five-semester map only).** This placement-based developmental
  companion is not a separate degree requirement. MAT 150.5, by contrast,
  is explicitly available in the statistics selector.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive course
  is needed to graduate." Graduation-wide flag, not a course row; recorded
  here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. The Modern Language continuation slot and the World Cultures slot can
   both legitimately be satisfied by the same specific language course in
   real life, but the system cannot detect that reuse and prevent
   double-counting. Pre-existing limitation, inherited from the identical
   `WAL_MODERN_LANGUAGE` pattern, not new to this submission.
2. LIN 250's prerequisite could not be independently verified against a
   department course-listing page; left blank rather than guessed (see
   "Prerequisite review" above).
3. `docs/programs.csv` listed CRJ_AA's catalog year as `2026`; corrected to
   `2025-2026` per the issue and both official maps (see "Program
   identity").
4. CRJ 204's title differs between the degree maps ("Crime and Justice in
   the Urban Community") and the official course-listings page ("Criminal
   Justice and the Urban Community"); the course-listings page's wording was
   used (see "Prerequisite review" above).

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/crj_aa_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/crj_aa_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 4 warning(s).`
- Warnings explained (all 4):
  1. `alternatives` references `SPE 102` — expected; already exists in
     other curriculum files.
  2. `prerequisites` references `SOC 100` (CRJ 102) — external course, not
     part of CRJ_AA; see "Prerequisite review" above.
  3. `prerequisites` references `POL 100` (CRJ 200) — external course, not
     part of CRJ_AA; see "Prerequisite review" above.
  4. `Required Common Core` lists 13 credits but requires 12 — the expected
     1-credit STEM-variant overage from MAT 150 (see "Credit reconciliation"
     and "General Elective / STEM excess credit" above).
- Local seed completed: `python seed_database.py` — confirmed the stale
  `CRJ_AA (2026)` placeholder was removed and 20 courses are now linked to
  the corrected `CRJ_AA (2025-2026)` program row.
- Full test suite: `python -m pytest -q` — passes except the one
  pre-existing, unrelated `test_psychology_curricula.py` Windows-encoding
  failure (confirmed identical on `main` before this branch). No
  regressions to existing majors' structures.
- Browser verification (Playwright, logged in as `admin`, program selector
  -> onboarding -> `/db-progress`): all four requirement columns (Program
  Requirements, Program Electives, Common Core, Flexible Core) render with
  correct titles and credit targets, including the corrected "Criminal
  Justice and the Urban Community" title for CRJ 204 (not the degree maps'
  "Crime and Justice..." wording) and "Second semester of the same Modern
  Foreign Language" for the modern-language placeholder. No console errors.
  CRJ 102 and CRJ 200 correctly render as locked (prerequisites SOC 100 /
  POL 100 are external to this curriculum and can never be marked complete
  within this major's own progress view) -- same accepted, already-documented
  external-prerequisite pattern used elsewhere in the system.
