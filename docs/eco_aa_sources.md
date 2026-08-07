# Curriculum Source Notes: Economics (A.A.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Social Sciences and Human Services (SSH)
- Program code: ECO_AA
- Program name: Economics
- Degree type: AA
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-07

Note: `docs/programs.csv` previously listed ECO_AA's `catalog_year` as `2026`,
not `2025-2026`. This was corrected to `2025-2026` in this pull request,
because it is not only a documentation mismatch: `seed_database.py`'s
`get_or_create(Program, ..., catalog_year=...)` keys a program by
`(department_id, code, catalog_year)`. With the mismatch in place, seeding
`eco_aa_courses.csv` (catalog_year `2025-2026`) created a second, orphaned
`ECO_AA` program row instead of attaching courses to the row `programs.csv`
already defined (catalog_year `2026`), and the API served the original,
empty row — Economics appeared selectable but showed zero courses in every
requirement group. `2025-2026` matches this issue's assigned identity and
the year printed on both official degree maps, so `programs.csv` was
corrected rather than changing the curriculum CSV to the stale placeholder
value. **Flagged for maintainer confirmation** since the guide advises not
to edit `programs.csv` without approval; this one-cell change is necessary
for the feature to function and is fully explained here for review.

## Official sources

1. Program map (two-year)
   - Title: Economics (ECO) Two Year Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/dxk7n1ueszc9841/eco2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_economics_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Title: Economics (ECO) Five Semester Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/fu2p20rclhmmlh0/eco3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_economics_5_semester_2025_2026.pdf`

3. Program requirements page
   - Title: Economics (A.A.) - BMCC
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/social-sciences/economics/
   - Effective year shown: matches the 2025-2026 degree maps

4. Course listings
   - Department/page: Economics Courses - BMCC
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/social-sciences/economics-courses/
   - Used for: verified titles, credits, and prerequisites of ECO 215, ECO 221,
     ECO 223, ECO 225, ECO 226, ECO 229, ECO 230, ECO 235, ECO 240, ECO 245,
     ECO 250, and ECO 202.

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Program page "Required Common Core" |
| Flexible Core | 18 | Program page "Flexible Core" |
| Program Requirements | 17 | Program page "Curriculum Requirements" (core courses + History) |
| Economics Electives | 9 | Program page "Curriculum Requirements" (3 upper-level electives) |
| General Elective | 4 | Program page "Curriculum Requirements" (General Elective line) |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

The "Curriculum Requirements" 30-credit line on the program page is split into
three CSV groups (Program Requirements 17 + Economics Electives 9 + General
Elective 4 = 30) to keep required courses, the elective pool, and the STEM
excess-credit placeholder separately reviewable, matching the pattern already
used in `mat_as_courses.csv`.

Course-level credits in `Required Common Core` sum to 14 (ENG 101 3 + ENG 201 3
+ MAT 206 4 + AST 110/PHY 110 4), 2 credits above the group's published
`required_credits` of 12. This is expected: see "STEM excess credit" below.

## Choices and alternatives

- **MAT 206 (Common Core, Mathematical and Quantitative Reasoning).** Both
  degree maps require MAT 206 specifically. Modeled with
  `choice_group_code=ECO_AA_MATH_QUANT`, a derived group in
  `program_choice_group_adjustments.csv` restricted to MAT 206 (4 credits).
- **AST 110 / PHY 110 (Common Core, Life and Physical Sciences).** Both degree
  maps show AST 110 with PHY 110 listed as the alternate ("PHY 110 is an
  alternate option"). Modeled as a placeholder `ECO-AA-LPS` with
  `choice_group_code=ECO_AA_LIFE_PHYSICAL`, a derived group restricted to
  `AST 110|PHY 110` (4 credits). Both courses already exist in the shared
  `RC_LIFE_PHYSICAL` pool at 4 credits.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression).** SPE 100 is shown
  on both maps with no "encouraged"-style qualifier; footnote text only
  clarifies SPE 102 as the option "for non-native speakers of English."
  Modeled as a literal required row, `alternatives=SPE 102`, matching the
  pattern used for the same course in `mat_as_courses.csv`.
- **SOC 100 (Flexible Core, Individual and Society).** Both maps say students
  are only "strongly encouraged" to take SOC 100 — a recommendation, not a
  restriction. Modeled as the unrestricted shared `FC_INDIVIDUAL` pool
  (placeholder `FC-INDIVIDUAL`), so the full Pathways pool remains selectable.
  SOC 100 is already a member of `FC_INDIVIDUAL` in `pathways_courses.csv`.
- **POL 100 (Flexible Core, U.S. Experience in Its Diversity — 6 credits / 2
  courses).** Both maps say students are "strongly encouraged" to take POL 100
  for "one of" the two required U.S. Experience courses — again a
  recommendation. Modeled as two unrestricted `FC_US_EXPERIENCE` pool slots
  (`FC-US-EXP-1`, `FC-US-EXP-2`), each 3 credits, since this program requires
  double the standard single-slot allocation used by other majors in this
  repository. POL 100 is already a member of `FC_US_EXPERIENCE`.
- **PSY 100 / PHY 110 (Flexible Core, Scientific World).** Both maps say
  students are "strongly encouraged" to take PSY 100 for Scientific World —
  a recommendation, not a restriction. Modeled as the unrestricted shared
  `FC_SCIENTIFIC_WORLD` pool (placeholder `FC-SCIWORLD`). PSY 100 is already a
  member of that pool. (PHY 110 is separately the Common Core Life and
  Physical Sciences alternate, described above — the same course code
  legitimately appears in two different Pathways pools in the shared data.)
- **History requirement (Program Requirements, 3 credits).** Both maps state:
  "Choose any History course or 1 course from ANT, GEO, PHI, POL, PSY, or
  SOC." This is not an existing shared choice-group in this repository, and
  the guide instructs not to create a new choice-group code without approval.
  Modeled as a single documented placeholder row, `ECO-AA-HISTORY`, with no
  `choice_group_code` (left blank). **Flagged for maintainer review** — see
  "Ambiguities" below.
- **Economics electives (9 credits, 3 courses).** Both maps: "Total of 3
  upper-level economics courses are required. ECO 201 and ECO 202 CANNOT be
  taken to satisfy this requirement." All 11 official options (ECO 215, 221,
  223, 225, 226, 229, 230, 235, 240, 245, 250) are listed as
  `program_elective` rows with `required_credits=9`. The validator is
  expected to warn that listed elective credits (33) exceed the 9 required —
  this is the intended "choose 3 of 11" behavior described in the guide.
- **General Elective / STEM excess credit (4 credits).** Footnote: "A total
  of 4 credits is required. These credits can be satisfied by taking STEM
  variants in the Common Core." Only 2 credits appear as an explicit "General
  Elective" line item on the map (Semester 4). The other 2 credits are the
  excess generated because MAT 206 and AST 110/PHY 110 are each 4-credit
  courses filling nominally 3-credit Common Core slots (+1 credit each = +2).
  Modeled as a single 4-credit placeholder, `ECO-AA-GENERAL`, matching the
  identical pattern and even the same title text already used in
  `mat_as_courses.csv` (`General Elective or Common Core STEM excess
  credits`). The current data model cannot move credits between groups, so
  this placeholder represents the full published 4-credit requirement as one
  program-elective-type row rather than splitting 2 explicit + 2 implied.

## Prerequisite review

- **ECO 202 and MAT 206 eligibility.** Footnote: "Students must be eligible
  to take MAT 206 in order to take ECO 202." This is a placement/eligibility
  rule, not a course-completion prerequisite — a student could be
  MAT-206-eligible via placement without having completed MAT 206 as a
  course. Per the guide, placement rules are not translated into the
  `prerequisites` column. `ECO 202` has no `prerequisites` value in the CSV.
  **Flagged for maintainer review.**
- **ENG 100.5 (five-semester map only).** The five-semester map places
  `ENG 100.5 Intensive English Composition` in Semester 1 instead of
  `ENG 101`, with the footnote: "ENG 100.5 is a combination of Intensive
  Writing and English Composition. Students must be exempt reading (ACR) in
  order to take this course. Once this course is passed, students will be
  able to move on to ENG 201." This is a placement-based alternate path
  (reading-exemption dependent), not an interchangeable equivalent course, so
  it was not added as an additional required/alternative course row. The
  CSV models the two-year map's `ENG 101` path only. **Flagged for
  maintainer review** if ENG 100.5 placement students need explicit support.
- **External elective prerequisites.** Several Economics elective
  prerequisites reference courses outside this program's CSV: ECO 215 and
  ECO 221 ("ECO 100 or ECO 201 or ECO 202"), ECO 250 ("FNB 100 or ECO 100 or
  ECO 201 or ECO 202"). ECO 100 and FNB 100 are not part of the ECO_AA
  requirement set, so the validator is expected to warn about external
  prerequisites for these three rows. Documented here per the guide rather
  than silently dropped, since ECO 201/ECO 202 (both in this program) already
  satisfy each OR-chain for an ECO_AA student.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive course
  is needed to graduate." This is a graduation-wide flag rather than a
  specific course row and is not represented as a CSV row. Recorded here and
  in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. `docs/programs.csv` lists ECO_AA's catalog year as `2026`; this submission
   uses `2025-2026` per the issue and both official maps. Please confirm
   whether `programs.csv` should be updated.
2. The History-or-social-science elective (footnote: "Choose any History
   course or 1 course from ANT, GEO, PHI, POL, PSY, or SOC") has no existing
   shared choice-group in this repository. It is currently a single
   undifferentiated 3-credit placeholder with no selectable pool. Formalizing
   a real choice-group (e.g., listing every eligible HIS/ANT/GEO/PHI/POL/PSY/
   SOC course code) requires enumerating BMCC's History department course
   listings, which was out of scope for this pass without further approval.
3. ECO 202's MAT-206-eligibility placement rule and the ENG 100.5
   reading-exemption placement rule are both advisory-only in the current
   data model (see "Prerequisite review").
4. The 4-credit General Elective / STEM-excess-credit mechanism is
   represented as a single flat 4-credit placeholder rather than literally
   modeling 2 explicit + 2 credits absorbed from Common Core overage, because
   the current schema cannot move credits between groups. This mirrors the
   identical, already-approved pattern in `mat_as_courses.csv`.

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/eco_aa_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/eco_aa_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 8 warning(s).`
- Warnings explained (all 8):
  1. `SPE 100` alternative `SPE 102` is listed in another curriculum file —
     expected; both courses already exist in the shared course catalog from
     other majors.
  2. `MAT 209` prerequisite references `MAT 206.5` — reused verbatim from the
     already-approved `mat_as_courses.csv` prerequisite text for the same
     course.
  3-4. `ECO 215` and `ECO 221` prerequisites reference `ECO 100` — external
     course, not part of ECO_AA; see "External elective prerequisites" above.
  5-6. `ECO 250` prerequisite references `FNB 100` and `ECO 100` — external
     courses, not part of ECO_AA; see "External elective prerequisites"
     above.
  7. `Required Common Core` lists 14 credits but requires 12 — the expected
     2-credit STEM-variant overage from MAT 206 and AST 110/PHY 110 (see
     "Credit reconciliation" and "General Elective / STEM excess credit"
     above).
  8. `Economics Electives` lists 33 credits but requires 9 — the expected
     "choose 3 of 11" elective pool (see "Choices and alternatives" above).
- Local seed completed: `python seed_database.py`
- Program Selector checked: yes (BMCC → Economics A.A. selectable)
- Academic Progress checked: yes (requirement groups, credits, degree-map
  links)
- Prerequisite unlocking checked: yes (MAT 206 → MAT 301/MAT 209; ECO
  201/202 → electives)
- Semester planner checked: yes (default four-semester and alternate
  five-semester sequences)
