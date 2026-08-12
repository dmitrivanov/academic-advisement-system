# Curriculum Source Notes: Sociology (A.A.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Social Sciences and Human Services (SSH)
- Program code: SOC_AA
- Program name: Sociology
- Degree type: AA
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-11

Note: `docs/programs.csv` previously listed SOC_AA's `catalog_year` as `2026`,
not `2025-2026` — the same mismatch already found and corrected for ECO_AA
and HIS_AA. Corrected here for the same reason: `seed_database.py` keys a
program by `(department_id, code, catalog_year)`, so the mismatch would
create an orphaned, empty duplicate program row instead of attaching
Sociology's courses to the row `programs.csv` already defines. Confirmed the
seeder's stale-row cleanup removed the old placeholder after the fix
(`Removed stale empty program placeholder: SOC_AA (2026)`).

## Official sources

1. Program map (two-year)
   - Title: Sociology (SOC) Two Year Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/o3t5fpzv35yxdsz/soc2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_sociology_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Title: Sociology (SOC) Five Semester Degree Map, 2025-2026
   - Direct URL: https://www.dropbox.com/s/ze0zrx7gmqzgjh7/soc3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_sociology_5_semester_2025_2026.pdf`

3. Program requirements page
   - Title: Sociology (A.A.) - BMCC
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/social-sciences/sociology/
   - Effective year shown: matches the 2025-2026 degree maps

4. Course listings
   - Sociology: https://www.bmcc.cuny.edu/academics/departments/social-sciences/sociology-courses/
   - Criminal Justice (CRJ 102/202/204): https://www.bmcc.cuny.edu/academics/departments/criminal-justice/course-listings/
   - Human Services (HUM 101): https://www.bmcc.cuny.edu/academics/departments/social-sciences/human-services-courses/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Program page "Required Common Core" |
| Flexible Core | 18 | Program page "Flexible Core" |
| Program Requirements (SOC 100 + SOC 350) | 7 | Both degree maps |
| Sociology Electives | 9 | Program page + degree-map footnote |
| Social Science Electives | 6 | Program page + degree-map footnote |
| Ethnic and Race Studies Elective | 3 | Program page + degree-map footnote |
| Liberal Arts Elective | 5 | Program page + degree-map footnote |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

Unlike Economics or Mathematics, neither Sociology degree map attaches a
"required"-style footnote to MAT 161 (Mathematical and Quantitative
Reasoning) or Life and Physical Sciences — both are shown as open,
undecorated placeholders on the map (Life and Physical Sciences literally
prints as "XXX xxx" with only a "consult an advisor" footnote, matching the
same pattern already found for History). No `program_choice_group_adjustments.csv`
restriction was added for either; both use the standard, unrestricted shared
`RC_MATH_QUANT` and `RC_LIFE_PHYSICAL` pools. Required Common Core course
credits therefore sum to exactly 12 (3+3+3+3), no STEM-variant overage.

## Choices and alternatives

- **MAT 161 / Life and Physical Sciences (Common Core).** Shown as open
  defaults with no restrictive footnote. Left as the standard, unrestricted
  `RC_MATH_QUANT` / `RC_LIFE_PHYSICAL` pools.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression, first course).**
  Modeled as a literal row, `alternatives=SPE 102`, matching the identical
  pattern already used in `mat_as_courses.csv`, `eco_aa_courses.csv`, and
  `his_aa_courses.csv`.
- **Creative Expression, second course.** Footnote: "Select any Creative
  Expression Pathways course except SPE 100 or SPE 102." An explicit
  exclusion. Modeled with a new derived group, `SOC_AA_CREATIVE` (base
  `FC_CREATIVE`, `exclude_course_codes=SPE 100|SPE 102`), matching the
  identical pattern already used by `MAT_AS_CREATIVE` and `HIS_AA_CREATIVE`.
- **Individual and Society, Scientific World, U.S. Experience in Its
  Diversity, World Cultures and Global Issues.** All footnotes use advisory
  language ("please consult an advisor," "students are strongly
  encouraged") rather than required-restriction language. All four are left
  as the standard, unrestricted shared pools.
- **KNOWN LIMITATION — Flexible Core "no more than two courses from one
  discipline" cap.** Both degree maps state: "No more than two courses in
  any discipline or interdisciplinary field can be used to satisfy Flexible
  Common Core requirements." This constraint spans multiple independent
  Flexible Core selectors (two Creative Expression slots, Individual and
  Society, Scientific World, U.S. Experience, World Cultures). Re-checked
  against the current schema, including the newer bundle/set-enforcement
  mechanism added for History (`RequirementGroup.completion_options` /
  `required_course_sets` / `required_course_set_count`, and
  `CourseRequirementGroupPrerequisite`/`prerequisite_groups`): both
  primitives operate on courses *within a single requirement group* (one
  group's own `courses` list). Neither can count a student's selections
  across *multiple different* groups and cap them by shared subject prefix,
  so this remains genuinely unsupported by the schema, not just
  undocumented. Enforcing it would require new cross-group validation logic
  beyond a single curriculum-data submission. **The system does not
  currently block a student from selecting, for example, three ANT courses
  across different Flexible Core categories.** Flagged for maintainer
  review.
- **Sociology Electives (9 credits, 3 courses, at least 2 at the 200
  level).** Footnote: "Choose three courses from SOC xxx (except SOC 100);
  please note two course must be 200-level." All 17 non-SOC-100,
  non-SOC-350 SOC courses are offered as a 9-credit choice pool (8 at the
  100 level, 9 at the 200 level) — the validator is expected to warn that
  listed credits (51) exceed required (9), the intended "choose 3 of 17"
  behavior. The "at least two must be 200-level" sub-constraint **is now
  machine-enforced**, using the same `required_course_sets` /
  `required_course_set_count` mechanism the maintainer added for History's
  linked-sequence rule (see lesson 1 in the curriculum-data feedback notes):
  each of the nine 200-level courses (SOC 200, 210, 220, 230, 234, 240, 250,
  256, 260) is encoded as its own single-code set on the SOC 110 row
  (`required_course_sets=SOC 200||SOC 210||SOC 220||SOC 230||SOC 234||SOC
  240||SOC 250||SOC 256||SOC 260`, `required_course_set_count=2`), so
  `groupRequirementSatisfied()` in `frontend/db_progress_graph.html` now
  requires at least 2 of those 9 sets to have a completed course *and* the
  group's normal 9-credit total, before the Sociology Electives requirement
  reads as satisfied. Verified live via
  `GET /api/db/programs/SOC_AA/requirements` after restarting the API
  process (the CSV/JSON encoding alone is not sufficient evidence — see
  lesson 4).
- **Social Science Electives (6 credits, 2 courses).** Footnote: "Choose two
  social science courses from the following disciplines: ANT xxx, CRJ 102,
  CRJ 202, CRJ 204, ECO xxx, GEO xxx, GWS xxx, HIS xxx, HUM 101, PHI xxx,
  POL xxx, or PSY xxx." This list mixes whole-discipline wildcards (ANT,
  ECO, GEO, GWS, HIS, PHI, POL, PSY) with four specific individual courses
  (CRJ 102, CRJ 202, CRJ 204, HUM 101) that are not whole-department
  allowances (CRJ and HUM otherwise have many courses not on this list). I
  checked `seed_database.py`'s `seed_program_choice_group_adjustments()`:
  `include_course_codes` and `include_subject_codes` combine with **AND**,
  not OR, so one derived group cannot express "any of these 8 disciplines,
  OR these 4 specific courses" — a course would need to satisfy both an
  exact-code match and a subject-prefix match simultaneously, which is
  impossible for this mixed list. Modeled instead as: one placeholder,
  `SOC-AA-SOCSCI` (6 credits, `choice_group_code=SOC_AA_SOCIAL_SCIENCE`, a
  derived group narrowing `BMCC_GENERAL_ELECTIVE` to
  `include_subject_codes=ANT|ECO|GEO|GWS|HIS|PHI|POL|PSY`), plus four
  literal rows (CRJ 102, CRJ 202, CRJ 204, HUM 101) in the same
  `Social Science Electives` requirement group. All five options contribute
  toward the same 6-credit total, so a student can satisfy the requirement
  through any accurate combination (for example one wildcard-discipline
  course plus one specific course), matching the official rule exactly
  without inventing a new schema capability.
- **Ethnic and Race Studies Elective (3 credits, 1 course).** Footnote:
  "Choose one course from AFN xxx, ASN xxx, ETH xxx or LAT xxx." Modeled as
  a single placeholder, `SOC-AA-ETHNICRACE`, with a new derived group
  `SOC_AA_ETHNIC_RACE` (base `BMCC_GENERAL_ELECTIVE`,
  `include_subject_codes=AFN|ASN|ETH|LAT`) — a pure subject-wildcard list
  with no individual-course exceptions, so no combination problem here.
  **Flagged ambiguity (cross-listed double-counting, not an exclusion
  rule):** unlike History's elective footnote, neither the Sociology program
  page nor either degree map states an exclusion for cross-listed
  equivalents. But several courses genuinely are cross-listed per the
  official course-listings page: SOC 125 = AFL 125, SOC 129 = AFN 129,
  SOC 150 = LAT 150, SOC 152 = LAT 152, SOC 154 = AFN 154, SOC 161 = AFL
  161, SOC 234 = LAT 234, SOC 256 = AFN 256 (verified against
  https://www.bmcc.cuny.edu/academics/departments/social-sciences/sociology-courses/
  on 2026-08-12). `AFN 129` and `AFL 161` are already present in
  `docs/pathways_courses.csv` (tagged `FC_US_EXPERIENCE`) and therefore
  already flow into the auto-populated `BMCC_GENERAL_ELECTIVE` pool that
  `SOC_AA_ETHNIC_RACE` narrows by subject prefix. This means a student could
  select, e.g., SOC 129 as a Sociology Elective and its cross-listed twin
  AFN 129 as the Ethnic and Race Studies Elective — same course content
  counted twice toward two different requirement groups. Since Sociology's
  own footnotes don't mandate excluding this (History's did, explicitly, by
  course code), no exclusion was added here — inventing one would be
  guessing at a rule the source doesn't state (see lesson 3 in the
  curriculum-data feedback notes: exclude only what the source actually
  excludes). Flagged for maintainer review instead.
- **Liberal Arts Elective (5 credits).** Footnote: "Students are recommended
  to take a 300-level ENG course, HED 100 or a Modern Language course" — a
  recommendation, not a restriction. `BMCC_LIBERAL_ARTS_ELECTIVE` is an
  existing canonical shared group (`docs/pathways_groups.csv`), so the
  requirement references it directly and unrestricted (no
  `program_choice_group_adjustments.csv` row needed), matching the same
  pattern as `BMCC_GENERAL_ELECTIVE` usage in `eco_aa_courses.csv` and
  `his_aa_courses.csv`. Modeled as a single 5-credit row (the map splits
  this 3+2 across two semesters, but the progress-screen selector reads
  each row's own `credits` value for its "Choose approved courses totaling
  N credits" prompt, so one 5-credit row is accurate and simpler than an
  uneven 3/2 split across two rows).

## Prerequisite review

- **SOC 350 (Sociology Capstone).** Official prerequisite (confirmed from
  the course-listings page): "[ENG 100.5 or ENG 101] and SOC 100 and two
  (2) SOC major electives of which one (1) must be a 200-level course."
  The flat prerequisite grammar (`|` for AND, ` or ` for OR) still has no
  grouping/parentheses or "any N of a pool" primitive, so the elective-count
  portion cannot live in the `prerequisites` column alone. It is now instead
  encoded via `prerequisite_groups=Sociology Electives`
  (`CourseRequirementGroupPrerequisite`), so SOC 350 additionally requires
  `groupRequirementSatisfied()` to return true for the Sociology Electives
  group — same pattern as HIS 275's `prerequisite_groups=History Sequence`.
  Combined with `prerequisites=SOC 100|ENG 100.5 or ENG 101`, the encoded
  rule is: SOC 100 AND (ENG 100.5 OR ENG 101) AND the Sociology Electives
  group satisfied.
  **This is not a perfect match to the official rule and is flagged for
  maintainer review:** "group satisfied" means the *entire* Sociology
  Electives requirement (all 3 electives, 9 credits, ≥2 at the 200 level, per
  the bullet above), not the official rule's smaller "2 electives, ≥1 at the
  200 level" (6 credits). This makes SOC 350 unlock somewhat *later* than
  the official requirement allows — the reverse of the previous encoding's
  problem (unlocking too early with no elective check at all), and a safer
  direction, but still not exact. There is no schema primitive today for "N
  of a group's courses, independent of the group's own full-completion
  threshold," so an exact encoding is not currently possible.
- **SOC 110 (Sociology of Urban Education).** Official prerequisite:
  "Permission of department." Not a course-based prerequisite; left blank
  and documented here rather than translated inaccurately.
  **Flagged for maintainer review.**
- **SOC 220 (Art, Culture & Society).** Official prerequisite: "Any
  100-level social science course." Not a single enumerable course code;
  left blank. **Flagged for maintainer review.**
- **SOC 154, SOC 161, SOC 234, SOC 250, SOC 256.** Official prerequisite:
  "SOC 100 or ANT 100." Encoded as `SOC 100 or ANT 100`. ANT 100 is not
  part of this program's curriculum CSV, so the validator is expected to
  warn about an external prerequisite for these five rows — expected and
  documented, same pattern as Economics' and History's external-prerequisite
  warnings.
- **CRJ 202 (Corrections).** Official prerequisite: CRJ 101. CRJ 101 is not
  part of this program's CSV (only CRJ 102/202/204 are, per the official
  Social Science elective list) — external prerequisite, validator warning
  expected and documented.
- **CRJ 204 (Criminal Justice and the Urban Community).** Official
  prerequisite: CRJ 101 and CRJ 102. Encoded as `CRJ 101|CRJ 102` — CRJ 102
  is internal (also listed in this program's Social Science Electives), CRJ
  101 is external, same expected warning as CRJ 202.
- **ENG 100.5 / MAT 161.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 161 respectively, identical pattern to
  Economics and History. Not added as additional required/alternative rows.
  **Flagged for maintainer review** if placement-track students need
  explicit support.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive course
  is needed to graduate." Graduation-wide flag, not a course row; recorded
  here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. **KNOWN LIMITATION — Flexible Core two-courses-per-discipline cap is not
   enforced.** Re-confirmed against the newer `completion_options` /
   `required_course_sets` mechanism (see "Choices and alternatives" above) —
   still genuinely unsupported because it spans multiple independent
   requirement groups and the new primitives only operate within one group.
2. **Sociology electives' "at least two 200-level" sub-constraint is now
   machine-enforced** via `required_course_sets` /
   `required_course_set_count` on the Sociology Electives group. See
   "Choices and alternatives" above for the encoding and how it was verified
   live via the API.
3. **SOC 350's elective-count prerequisite sub-condition is now
   machine-enforced, but not exactly** — `prerequisite_groups=Sociology
   Electives` requires the *entire* 9-credit/3-course Sociology Electives
   group (not just 2 of the 3 electives) before SOC 350 unlocks, which is
   stricter/later than the official 2-elective rule. See "Prerequisite
   review" above for detail.
4. `docs/programs.csv` listed SOC_AA's catalog year as `2026`; corrected to
   `2025-2026` per the issue and both official maps (see "Program identity").
5. `SOC_AA_SOCIAL_SCIENCE` and `SOC_AA_ETHNIC_RACE` are subject-prefix
   restricted views over the canonical `BMCC_GENERAL_ELECTIVE` pool
   (auto-populated at seed time from every real course in the system), so
   their completeness depends on which curricula have been added to the
   repository so far — they will grow automatically as more majors are
   added, not require manual editing.
6. SOC 110's "permission of department" and SOC 220's "any 100-level social
   science course" prerequisites are not encoded (see "Prerequisite
   review").
7. **Cross-listed course double-counting is possible but not excluded** —
   SOC 125/129/150/152/154/161/234/256 are officially cross-listed with
   AFL/AFN/LAT equivalents, some of which are already selectable in the
   auto-populated `BMCC_GENERAL_ELECTIVE` pool that `SOC_AA_ETHNIC_RACE`
   draws from. No exclusion was added because, unlike History, Sociology's
   own footnotes don't state one. See "Choices and alternatives" above.

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/soc_aa_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/soc_aa_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 11 warning(s).`
- Warnings explained (all 11):
  1. `alternatives` references `SPE 102` — expected; already exists in
     other curriculum files.
  2. `prerequisites` references `ENG 100.5` — expected; already exists in
     other curriculum files.
  3-7. `prerequisites` references `ANT 100` (SOC 154, 161, 234, 250, 256) —
     external course, not part of SOC_AA; see "Prerequisite review" above.
  8-9. `prerequisites` references `CRJ 101` (CRJ 202, CRJ 204) — external
     course, not part of SOC_AA; see "Prerequisite review" above.
  10. `Sociology Electives` lists 51 credits but requires 9 — expected
      "choose 3 of 17" elective pool.
  11. `Social Science Electives` lists 18 credits but requires 6 — expected
      (6-credit placeholder + 4 literal 3-credit alternatives, "choose
      enough to reach 6" behavior).
- Local seed completed: `python seed_database.py` — confirmed the stale
  `SOC_AA (2026)` placeholder was removed and 36 courses are now linked to
  the corrected `SOC_AA (2025-2026)` program row.
- Choice-group population confirmed via `/api/db/choice-groups/<code>/courses`:
  `SOC_AA_SOCIAL_SCIENCE` (71 courses), `SOC_AA_ETHNIC_RACE` (20 courses),
  `BMCC_LIBERAL_ARTS_ELECTIVE` (294 courses) — no empty selectors.
- Full test suite: `python -m pytest -q` — 129 passed, 1 pre-existing,
  unrelated `test_psychology_curricula.py` Windows-encoding failure
  (confirmed identical on `main` before this branch). `tests/test_sociology_curriculum.py`:
  17/17 passed. No regressions to existing majors' structures.
- `completion_options`/`required_course_sets`/`required_course_set_count`/
  `prerequisite_groups` verified live, not just in the CSV: fetched
  `GET /api/db/programs/SOC_AA/requirements` after reseeding and confirmed
  `Sociology Electives`' `required_course_sets` is nine single-code sets
  with `required_course_set_count: 2`, and `SOC 350`'s course object has
  `prerequisite_groups: ["Sociology Electives"]`. First attempt showed these
  fields missing entirely — root cause was a stale `uvicorn` process still
  running the pre-merge `api_db_routes.py` from before this session's
  syncs (Python module code doesn't hot-reload on file change without
  `--reload`/a restart, unlike the static CSV/HTML/JS files the same
  process re-reads per request). Restarting the server against the current
  code resolved it. Recorded here per lesson 4 (verify real behavior, not
  just the CSV encoding) — the CSV/JSON encoding alone would not have
  caught this class of bug.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`), driving the actual
  `groupRequirementSatisfied()` / prerequisite logic rather than just
  reading the CSV/JSON encoding, per lesson 4:
  1. Baseline (nothing completed): SOC 350 card is `locked`.
  2. SOC 100 + ENG 101 completed, no electives: SOC 350 still `locked`
     (correctly still gated on the Sociology Electives group).
  3. SOC 100 + ENG 101 + 3 electives totaling 9 credits, but only **one**
     at the 200 level (SOC 111, SOC 125, SOC 200): SOC 350 still `locked`
     -- confirms the 200-level sub-constraint is genuinely blocking, not
     just decorative.
  4. Same, but swapping in a second 200-level elective (SOC 111, SOC 200,
     SOC 210): SOC 350 becomes `available` -- confirms the group's full
     required-credits-plus-set-count condition unlocks it once actually
     met.
  All group cards (Program Requirements, Program Electives, Common Core,
  Flexible Core) render with clean titles (no "(200-level)" suffix
  anywhere on the page) and correct credit targets; no console errors.
