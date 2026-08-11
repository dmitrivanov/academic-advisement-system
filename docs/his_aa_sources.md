# Curriculum Source Notes: History (A.A.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Social Sciences and Human Services (SSH) — the issue text says
  "Social Sciences, Human Services and Criminal Justice"; `docs/departments.csv`
  registers the SSH code under the shorter name "Social Sciences and Human
  Services." Per the issue's own instruction to confirm against existing
  naming conventions, this submission uses the repository's existing
  department name rather than introducing a second, slightly different name
  for the same department code.
- Program code: HIS_AA
- Program name: History
- Degree type: AA
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-11

Note: `docs/programs.csv` previously listed HIS_AA's `catalog_year` as `2026`,
not `2025-2026` — the same mismatch found and corrected for ECO_AA. Per that
precedent, this was corrected to `2025-2026` in this pull request rather than
left as a silent bug: `seed_database.py` keys a program by
`(department_id, code, catalog_year)`, so the mismatch would have created an
orphaned, empty duplicate program row instead of attaching History's courses
to the row `programs.csv` already defines. Confirmed the seeder's stale-row
cleanup removes the old placeholder after the fix (`Removed stale empty
program placeholder: HIS_AA (2026)`).

## Official sources

1. Program map (two-year)
   - Title: History (HIS) Two Year Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/kddujcitjz7acmi/his2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_history_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Title: History (HIS) Five Semester Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/wf55ek41p32m0uz/his3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_history_5_semester_2025_2026.pdf`

3. Program requirements page
   - Title: History (A.A.) - BMCC
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/social-sciences/history/
   - Effective year shown: matches the 2025-2026 degree maps

4. Course listings
   - History: https://www.bmcc.cuny.edu/academics/departments/social-sciences/history-courses/
   - Anthropology: https://www.bmcc.cuny.edu/academics/departments/social-sciences/anthropology/
   - Geography: https://www.bmcc.cuny.edu/academics/departments/social-sciences/geography-courses/
   - Ethnic and Race Studies (AFN, AFL, ASN, ETH, LAT): https://www.bmcc.cuny.edu/academics/departments/ethnic-studies/course-listings/
   - Economics: https://www.bmcc.cuny.edu/academics/departments/social-sciences/economics-courses/
   - Used for: verified titles and credits of every History elective and
     every Social Science/Ethnic Studies elective option.

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Program page "Required Common Core" |
| Flexible Core | 18 | Program page "Flexible Core" |
| History Sequence | 6 | Program page "History Sequence" (choose one pair) |
| Program Requirements (HIS 275) | 3 | Both degree maps |
| History Electives | 9 | Program page + degree-map footnote |
| Social Science or Ethnic Studies Electives | 6 | Program page + degree-map footnote |
| General Elective | 6 | Program page + degree-map footnote |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

Unlike Economics, neither degree map attaches a "required"-style footnote to
MAT 161 (Mathematical and Quantitative Reasoning) or to the Life and Physical
Sciences slot — both are shown as open, undecorated placeholders (Life and
Physical Sciences literally prints as "XXX xxx" with only a "consult an
advisor" footnote). No `program_choice_group_adjustments.csv` restriction was
added for either; both use the standard shared `RC_MATH_QUANT` and
`RC_LIFE_PHYSICAL` pools, with MAT 161 noted below as the map's shown
default. Required Common Core course credits therefore sum to exactly 12
(3+3+3+3) with no STEM-variant overage, unlike Economics or Mathematics.

## Choices and alternatives

- **History Sequence (6 credits) — the required linked-pair choice.** See
  "KNOWN LIMITATION" in "Ambiguities requiring maintainer review" below. This
  is the most significant modeling decision in this submission.
- **MAT 161 (Common Core, Mathematical and Quantitative Reasoning).** Shown
  as the default on both maps with no restrictive footnote. Left as the
  standard, unrestricted `RC_MATH_QUANT` pool (placeholder `HIS-AA-MATHQUANT`).
- **Life and Physical Sciences.** Both maps show an open "XXX xxx" slot with
  only a "consult an advisor" footnote. Left as the standard, unrestricted
  `RC_LIFE_PHYSICAL` pool (placeholder `HIS-AA-LPS`).
- **PHI 100 / ECO 100 (Flexible Core, Individual and Society).** Both maps
  show PHI 100 with the footnote "ECO 100 is an alternate course option" —
  an explicit substitution, not a recommendation. Modeled as a literal row,
  `alternatives=ECO 100`.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression, first course).**
  Modeled as a literal row, `alternatives=SPE 102`, matching the identical
  pattern already used for the same course in `mat_as_courses.csv` and
  `eco_aa_courses.csv`.
- **Creative Expression, second course.** Footnote: "Select any Creative
  Expression Pathways course except SPE 100 or SPE 102." An explicit
  exclusion, not a recommendation. Modeled with a new derived group,
  `HIS_AA_CREATIVE` (base `FC_CREATIVE`, `exclude_course_codes=SPE 100|SPE
  102`), matching the identical pattern in `mat_as_courses.csv`
  (`MAT_AS_CREATIVE`).
- **Scientific World, U.S. Experience in Its Diversity, World Cultures and
  Global Issues.** All three footnotes use advisory language ("consult an
  advisor," "students are advised," "strongly encouraged") rather than
  required-restriction language. All three are left as the standard,
  unrestricted shared pools. The specific advised/encouraged defaults (a
  7-course list for U.S. Experience; a modern-language course for World
  Cultures) are recorded here and in the degree-map JSON `sequence_notes`
  rather than encoded as restrictions, consistent with how Economics treated
  "strongly encouraged" footnotes.
- **History Electives (9 credits).** Footnote: "A maximum of 9 credits is
  required. Choose any HIS courses, excluding courses completed in the
  History Sequence or AFN 121, AFN 122, AFN 124, AFN 126, ASN 114, ASN 129,
  LAT 127, LAT 128, LAT 130, or LAT 131." The excluded courses are the
  cross-listed equivalents of HIS 121, HIS 122, HIS 124, HIS 126, HIS 114,
  HIS 129, HIS 127, HIS 128, HIS 130, and HIS 131 under other departments'
  prefixes — the intent is not to double-count the same course content under
  two different subject codes. This is satisfied by construction: only the
  HIS-prefixed courses are listed as History Electives; the AFN/ASN/LAT
  cross-listed versions are never added to this group. All 14 non-sequence,
  non-HIS-275 HIS courses (HIS 111, 114, 121, 122, 123, 124, 126, 127, 128,
  129, 130, 131, 225, 226) are listed, `required_credits=9` — the validator
  is expected to warn that listed credits (42) exceed required (9), the
  intended "choose 3 of 14" behavior.
- **Non-Western History requirement.** See "KNOWN LIMITATION" below.
- **Social Science or Ethnic Studies Electives (6 credits, 2 courses).**
  Footnote: "Choose from AFL, AFN, ANT, ASN, ECO, GEO, HIS, LAT, PHI, POL,
  PSY, or SOC." `BMCC_GENERAL_ELECTIVE` already exists as a canonical shared
  group (`docs/pathways_groups.csv`), auto-populated by
  `seed_database.py`'s `seed_institutional_elective_groups()` from every
  real course across all curricula and Pathways pools after all majors are
  seeded. `HIS_AA_SOCSCI_ETHNIC` is a derived group
  (`program_choice_group_adjustments.csv`, `base_group_code=
  BMCC_GENERAL_ELECTIVE`) narrowed via `include_subject_codes=AFL|AFN|ANT|
  ASN|ECO|GEO|HIS|LAT|PHI|POL|PSY|SOC` — the same subject-prefix-allow-list
  pattern already established by `ECO_AA_HISTORY`,
  `CIS_DEPARTMENT_ELECTIVE`, and `CNT_DEPARTMENT_ELECTIVE`. This is a live,
  automatically-maintained selector (96 real courses at seed time), not a
  static hand-curated list, so it stays complete and accurate as more
  curricula are added to the repository without requiring manual updates.
  An earlier draft of this file manually enumerated 62 course codes via
  `include_course_codes` before this was corrected to the subject-code
  pattern for consistency with the rest of the codebase.
- **General Elective (6 credits, 2 courses).** Footnote: "Students are
  recommended to take a 300 level English course, a Health Education course,
  and/or Modern Language course(s)" — a recommendation, not a restriction,
  so the full `BMCC_GENERAL_ELECTIVE` pool is referenced directly and
  unrestricted (no `program_choice_group_adjustments.csv` row needed). The
  progress-screen selector reads each row's own `credits` value ("Choose
  approved courses totaling 6 credits"), so `HIS-AA-GENERAL-1`/`-2` each
  correctly prompt for 3 of the requirement's 6 credits regardless of the
  base group's own blank `required_credits`/`required_course_count`
  metadata.

## Prerequisite review

- **HIS 275 (History Research and Writing Methods).** Officially requires
  "ENG 201 & (HIS 101 and HIS 102) or (HIS 115 and HIS 116) or (HIS 120 and
  HIS 125)." The prerequisite grammar (`|` for AND, ` or ` for OR) has no
  grouping/parentheses, so the grouped "(A and B) or (C and D) or (E and F)"
  structure cannot be expressed. Only `ENG 201` is encoded as HIS 275's
  prerequisite; the sequence-completion portion is unenforced. **Flagged for
  maintainer review.**
- **ECO 202 note (reused from Economics).** Not applicable here; ECO 100 is
  only referenced as PHI 100's alternate and carries no prerequisite of its
  own in this program.
- **HIS 225 (History of Women).** Official prerequisite: "Any history course
  or GWS 100." "Any history course" is not a single enumerable course code
  and GWS 100 is outside this program's CSV. Left blank rather than
  translated inaccurately. **Flagged for maintainer review.**
- **HIS 226 (Conflict in the Middle East).** Official prerequisite: "Any
  Social Science course." Same issue as HIS 225 — left blank. **Flagged for
  maintainer review.**
- **ENG 100.5 / MAT 161.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 161 respectively (reading-exemption and
  algebra-combination courses). Not added as additional required/alternative
  rows, consistent with how the identical ENG 100.5 pattern was handled for
  Economics. **Flagged for maintainer review** if placement-track students
  need explicit support.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive course
  is needed to graduate." Graduation-wide flag, not a course row; recorded
  here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. **KNOWN LIMITATION — linked History Sequence pairs are not enforced.**
   The degree requires choosing exactly one pair: HIS 101 & HIS 102, or
   HIS 115 & HIS 116, or HIS 120 & HIS 125. I investigated the schema
   directly (`models.py`'s `ChoiceGroup`/`ChoiceGroupCourse` tables, the
   `program_choice_group_adjustments.csv` mechanism, and the frontend's
   choice-selection logic in `frontend/db_progress_graph.html`) and
   confirmed it only supports flat "pick any N courses/credits from a pool"
   selection — there is no concept of a linked, mutually-exclusive
   multi-course bundle. Building true enforcement would require a schema
   change (a new grouping concept, new validator logic, new UI, new
   completion-checking logic) beyond a single curriculum-data submission, so
   per this issue's explicit instruction I did not force an inaccurate model.
   Instead: all 6 sequence courses are listed under a single "History
   Sequence" requirement group (`required_credits=6`), each second-course
   (HIS 102, HIS 116, HIS 125) has its own pair's first course as a
   prerequisite as a partial safeguard, and the limitation is documented
   here, in the degree-map JSON's `sequence_notes`, and should be called out
   prominently in the pull request. **A student could currently mark courses
   from two different pairs as complete without the UI blocking it — that
   would not satisfy the real degree requirement.**
2. **Non-Western History requirement is not mechanically enforced.** Neither
   degree map nor the official course-listing page publishes an authoritative
   "these specific courses count as non-Western" list — only the requirement
   text itself ("at least one course must be a non-western History course").
   I labeled the courses whose titles clearly indicate non-Western/global
   regional content — HIS 114 (Asian American History), HIS 121/122
   (African Civilization/Africa 1500-Present), HIS 129 (Middle East), HIS 226
   (Middle East Conflict) — with "(non-Western)" in the curriculum data as an
   advisory aid. Several other courses (HIS 123/124 African American
   History, HIS 126 Caribbean History, HIS 127/128 Puerto Rico, HIS 130
   Latin America, HIS 131 Dominican Republic) plausibly also qualify
   depending on BMCC's specific classification, but I did not label them
   without an authoritative source, to avoid guessing. **The system does not
   block a student from completing zero non-Western electives.** Recommend
   the maintainer confirm an authoritative non-Western course list with the
   History department.
3. `docs/programs.csv` listed HIS_AA's catalog year as `2026`; corrected to
   `2025-2026` per the issue and both official maps (see "Program identity").
4. `HIS_AA_SOCSCI_ETHNIC` is a subject-prefix-restricted view over the
   canonical `BMCC_GENERAL_ELECTIVE` pool (auto-populated from every real
   course in the system at seed time — 96 courses across the 12 relevant
   departments as of this submission). Its completeness depends on which
   curricula have been added to the repository so far, so it will grow (not
   require manual editing) as more majors are added.
5. HIS 275's sequence-completion prerequisite and HIS 225/HIS 226's
   "any history course" / "any Social Science course" prerequisites are not
   encoded (see "Prerequisite review").
6. ENG 100.5 / MAT 161.5 placement-track alternates (five-semester map only)
   are not modeled as additional course rows (see "Prerequisite review").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/his_aa_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/his_aa_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 4 warning(s).`
- Warnings explained (all 4):
  1. `alternatives` references `SPE 102` — expected; already exists in other
     curriculum files (Mathematics, Economics).
  2. `alternatives` references `ECO 100` — expected; already exists in
     `eco_aa_courses.csv`.
  3. `History Sequence` lists 18 credits but requires 6 — expected; see the
     linked-pair limitation above. This is the closest safe approximation of
     "choose one pair," not a true "choose any 2" elective.
  4. `History Electives` lists 42 credits but requires 9 — expected
     "choose 3 of 14" elective pool.
- Local seed completed: `python seed_database.py` — confirmed the stale
  `HIS_AA (2026)` placeholder was removed and 35 courses are now linked to
  the corrected `HIS_AA (2025-2026)` program row.
- Choice-group population confirmed via `/api/db/choice-groups/<code>/courses`:
  `HIS_AA_CREATIVE` (22 courses), `HIS_AA_SOCSCI_ETHNIC` (96 courses,
  subject-prefix-derived from `BMCC_GENERAL_ELECTIVE`), `BMCC_GENERAL_ELECTIVE`
  (382 courses, auto-populated), `RC_MATH_QUANT` (includes MAT 161),
  `RC_LIFE_PHYSICAL` (includes AST 110/PHY 110) — no empty selectors.
- Full test suite: `python -m pytest -q` — passes except the one
  pre-existing, unrelated `test_psychology_curricula.py` Windows-encoding
  failure (confirmed identical on `main` before this branch). One regression
  was found and fixed: `test_mat_as_curriculum.py`'s
  `test_shared_pathways_are_complete_and_group_scoped` hardcoded the full set
  of canonical Pathways group codes; updated to include the new
  `BMCC_GENERAL_ELECTIVE` group, since Mathematics' own behavior is
  otherwise unchanged.
- Program Selector checked: pending manual/automated browser pass.
- Academic Progress checked: pending manual/automated browser pass.
- Paired-sequence, elective, and mobile-layout checks: pending manual/automated browser pass.
