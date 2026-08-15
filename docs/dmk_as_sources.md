# Curriculum Source Notes: Digital Marketing (A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Business Management (BUS)
- Program code: DMK_AS
- Program name: Digital Marketing
- Degree type: AS
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-13

Note: `docs/programs.csv` previously listed DMK_AS's `catalog_year` as
`2026`, not `2025-2026` — the same recurring mismatch already found and
corrected for every prior BMCC major added this way. Fixed before the
first seed on this branch, so no stale empty program placeholder was
ever created.

## Official sources

1. Program map (two-year)
   - Direct URL: https://www.dropbox.com/s/ewmc989xl8zocuf/dma2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_digital_marketing_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Direct URL: https://www.dropbox.com/s/j9qh03hf3co2r4n/dma3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_digital_marketing_5_semester_2025_2026.pdf`

   As with Nursing, VAT, and Cybersecurity Certificate, neither direct URL
   is currently linked from the live program page (which now links a newer
   2026-2027 map instead); both were recovered from a Wayback Machine
   snapshot of the page taken while 2025-2026 was current. **Flagged for
   maintainer review**: confirm these dropbox links remain stable.

3. Program requirements page
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/business-management/digital-marketing/

4. Course listings
   - Business Management (BUS, MAR courses): https://www.bmcc.cuny.edu/academics/departments/business-management/course-listings/
   - Computer Information Systems (CIS 200): https://www.bmcc.cuny.edu/academics/departments/cis/course-listings/
   - Media Arts and Technology (MMP 240): https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/course-listings/
   - Mathematics (MAT 150): https://www.bmcc.cuny.edu/academics/departments/math/mathematics-program/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Degree map (ENG 101, ENG 201, MAT 150, Life and Physical Science) |
| Flexible Core | 18 | Degree map (Creative Expression x2, Individual and Society, Scientific World, U.S. Experience, World Cultures) |
| Program Requirements | 15 | Degree map (BUS 104, MAR 100, MAR 330, MAR 340, BUS 110.5) |
| Program Elective | 9 | Degree map footnote 6, "choose from 7 courses" |
| General Elective | 6 | Degree map footnote 4 |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

Unlike Video Arts and Technology (which substitutes most Flexible Core
areas with program-specific required courses), Digital Marketing uses the
**full standard** Common Core / Flexible Core structure identical to
Economics, History, Sociology, and Criminal Justice — all 6 Flexible Core
slots (two Creative Expression, Individual and Society, Scientific World,
U.S. Experience, World Cultures) are present and unrestricted or
minimally restricted, matching the same pattern.

Course-level credits in `Required Common Core` sum to 13 (ENG 101 3 + ENG
201 3 + MAT 150 4 + Life and Physical Sciences 3), 1 credit above the
group's published `required_credits` of 12 — the expected STEM-variant
overage from MAT 150; see "General Elective" below.

## Choices and alternatives

- **Life and Physical Sciences, Individual and Society, Scientific World,
  U.S. Experience in Its Diversity, World Cultures and Global Issues.**
  All footnoted only with advisory "consult an advisor" language (footnote
  1 on both maps). Left as the standard, unrestricted shared pools.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression, first
  course).** Modeled as two reciprocal rows (`alternatives=SPE 102` /
  `alternatives=SPE 100`), matching the pattern established for
  `soc_aa_courses.csv`, `nur_aas_courses.csv`, and `vat_as_courses.csv`.
- **Creative Expression, second course.** Footnote: "Select any Creative
  Expression Pathways course except SPE 100 or SPE 102." Modeled with a
  new derived group, `DMK_AS_CREATIVE` (base `FC_CREATIVE`,
  `exclude_course_codes=SPE 100|SPE 102`), matching the identical pattern
  already used by `SOC_AA_CREATIVE`, `HIS_AA_CREATIVE`, and
  `CRJ_AA_CREATIVE`.
- **MAT 150 (Common Core, Mathematical and Quantitative Reasoning).** The
  five-semester map uses MAT 150.5 instead (a non-STEM-variant placement
  course) — not added as an additional row, matching the established
  ENG 100.5/MAT 161.5 handling in every other major so far.
- **Program Elective (9 credits, choose 3 of 7).** Footnote: "A total of 9
  credits is required to satisfy this area. Choose from MAR 210, MAR 220,
  MAR 230, BUS 150, CIS 200, COM 245 or MMP 240." All 7 courses modeled as
  literal rows in one `Program Elective` group (`required_credits=9`,
  listed credits 21 — expected "choose 3 of 7" overage warning).
- **General Elective / STEM excess credit (6 credits).** Footnote: "A
  total of 6 credits is required for degree completion. Some of these
  credits may be satisfied by taking STEM variants in the Common Core."
  Only 5 credits appear explicitly on the two-year map (3 credits in
  Semester 2, 2 credits in Semester 4) because MAT 150 is a 4-credit
  course filling a nominally 3-credit Common Core slot (+1 credit).
  Modeled as a single 6-credit placeholder, `DMK-AS-GENERAL`, matching the
  identical pattern and title text already used in `eco_aa_courses.csv`,
  `crj_aa_courses.csv`, and `vat_as_courses.csv` (`General Elective or
  Common Core STEM excess credits`).

## Prerequisite review

- **MAR 100 (Introduction to Marketing).** Footnote 2/3 on both maps:
  "MAR 100 is the pre-requisite course to all MAR courses." Confirmed by
  the course-listings page: MAR 100 itself has no prerequisites (it's the
  entry point). Encoded on each individual downstream MAR course rather
  than as a blanket rule, since the schema has no program-wide
  "prerequisite for all courses of this prefix" primitive.
- **MAR 210 (Consumer Motivation).** Official prerequisite: "MAR 100."
  Encoded as `MAR 100`.
- **MAR 220 (Essentials of Advertising) / MAR 230 (Essentials of Public
  Relations).** Official prerequisite for both: "ENG 101 and MAR 100."
  Encoded as `ENG 101|MAR 100`.
- **MAR 330 (Marketing Research and Analytics).** Official prerequisite
  (course-listings page, quoted exactly): "ENG 101 and MAT 150 and [MAR
  100 or PSY 100]" — the source itself uses bracket notation confirming
  the grouping. **This is fully and exactly expressible** in the current
  prerequisite grammar: `parse_relationships()` in `seed_database.py`
  splits the string on `|` into top-level AND groups first, and each
  `|`-separated group can independently contain an ` or ` OR-list. Encoded
  as `ENG 101|MAT 150|MAR 100 or PSY 100`, which parses to exactly (ENG
  101) AND (MAT 150) AND (MAR 100 OR PSY 100) — matching the official rule
  precisely, not an approximation. PSY 100 is external to this curriculum
  (not one of Digital Marketing's own courses), so the validator is
  expected to warn about it.
- **MAR 340 (Digital Marketing and Analytics).** Official prerequisite:
  "MAR 330." Encoded as `MAR 330`.
- **CIS 200 (Introduction Systems and Technologies).** Official
  prerequisite (course-listings page, quoted exactly): "Any ACC course or
  any BUS course and pass computer competency test or CIS 100" — a
  genuinely complex, only-partially-expressible condition. Encoded as
  `ACC 122 or BUS 104`, reusing the identical partial-encoding precedent
  already established for this same course in `bba_as_courses.csv`
  (rather than re-deriving a new interpretation). The computer-competency
  test alternative remains an advising check, not enforced. ACC 122 is
  external to this curriculum, so the validator is expected to warn.
- **MMP 240 (Web Design).** Official prerequisite: "CIS 180 or MMP 100."
  Encoded as `CIS 180 or MMP 100`. Neither CIS 180 nor MMP 100 is part of
  this curriculum's own course list; the validator is expected to warn
  about both as external references.
- **COM 245 (The Mass Media).** The official Digital Marketing curriculum
  lists `SPE 100` or departmental permission as the prerequisite. Encoded
  as `SPE 100`; the non-course departmental-permission alternate remains
  an advising check, consistent with other permission-based exceptions.
- **ENG 100.5 / MAT 150.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 150 respectively, identical pattern to
  every other major. Not added as additional rows.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive
  course is needed to graduate." Graduation-wide flag, not a course row;
  recorded here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. The two official degree-map dropbox links are no longer linked from
   the live Digital Marketing program page (which now serves a 2026-2027
   map instead) and were recovered via the Wayback Machine. See "Official
   sources" above.
2. CIS 200's full official prerequisite (ACC/BUS course plus a computer
   competency test or CIS 100) is only partially encoded, matching an
   existing precedent from `bba_as_courses.csv`.
3. COM 245 also permits enrollment with departmental permission. The
   course-based `SPE 100` prerequisite is enforced; permission remains an
   advising check because it cannot be represented as a course rule.
4. `docs/programs.csv` listed DMK_AS's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/dmk_as_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/dmk_as_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 6 warning(s).`
- Warnings explained (all 6):
  1. `prerequisites` references `PSY 100` (MAR 330) — external, not part
     of DMK_AS; see "Prerequisite review" above.
  2. `prerequisites` references `ACC 122` (CIS 200) — external, same
     reasoning.
  3-4. `prerequisites` references `CIS 180` and `MMP 100` (MMP 240) —
     external, same reasoning.
  5. `Required Common Core` lists 13 credits but requires 12 — expected
     1-credit STEM-variant overage from MAT 150.
  6. `Program Elective` lists 21 credits but requires 9 — expected
     "choose 3 of 7" pool.
- Local seed completed: `python seed_database.py` — `DMK_AS` seeded
  cleanly with 24 courses; no stale placeholder needed cleanup since
  `programs.csv` was corrected before the first seed on this branch.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: MAR 330 is `locked`.
  2. After ENG 101 + MAT 150 only (the two plain-AND requirements, without
     satisfying the MAR 100-or-PSY 100 branch): MAR 330 stays `locked` --
     confirms the OR-branch is genuinely required, not optional.
  3. After also completing MAR 100: MAR 330 becomes `available`.
  4. After MAR 330: MAR 340 becomes `available`.
  All group cards render with correct titles and credit targets; SPE
  100/SPE 102 render as an explicit "Alternative requirement - CHOOSE ONE"
  widget. No console errors.
