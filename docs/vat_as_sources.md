# Curriculum Source Notes: Video Arts and Technology (A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Media Arts and Technology (MMA)
- Program code: VAT_AS
- Program name: Video Arts and Technology
- Degree type: AS
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-13

Note: `docs/programs.csv` previously listed VAT_AS's `catalog_year` as
`2026`, not `2025-2026` — the same recurring mismatch already found and
corrected for every prior BMCC major added this way. Fixed before the
first seed on this branch, so no stale empty program placeholder was ever
created.

## Official sources

1. Program map (two-year)
   - Direct URL: https://www.dropbox.com/s/iic5ptkm1t30k9s/vat2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_vat_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Direct URL: https://www.dropbox.com/s/qtorli5q2rqdu3z/vat3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_vat_3_year_2025_2026.pdf`

   As with Nursing, neither direct URL is currently linked from the live
   VAT program page (which now links a newer 2026-2027 map instead); both
   were recovered from a Wayback Machine snapshot of the page taken while
   2025-2026 was current. **Flagged for maintainer review**: confirm these
   dropbox links remain stable.

3. Program requirements page
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/video-arts-and-technology/
   - This page's own requirement-section summary describes the generic,
     boilerplate 12/18/30 Common-Core/Flexible-Core/Curriculum-Requirements
     split used across most BMCC AA/AS programs. It does **not** match
     VAT's actual degree map, which has no separate Individual and
     Society, Scientific World, World Cultures, or second Creative
     Expression slots — those Pathways areas are entirely replaced by
     specific required program courses in this curriculum. The group
     structure below is derived directly from the degree maps' own
     course-by-course content and credit totals, not from this generic
     page summary.

4. Course listings
   - Media Arts and Technology (VAT, MES, MMP, ANI, MEA courses): https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/course-listings/
   - Business Management (BUS 200): https://www.bmcc.cuny.edu/academics/departments/business-management/course-listings/
   - Mathematics (MAT 160): https://www.bmcc.cuny.edu/academics/departments/math/mathematics-program/
   - Science (PHY 110): https://www.bmcc.cuny.edu/academics/departments/science/science-program/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Degree map Semesters 1-2 (ENG 101, ENG 201, MAT 160, PHY 110) |
| Flexible Core | 6 | Degree map (SPE 100, U.S. Experience) |
| Program Requirements | 18 | Degree map (MES 153, VAT 100, MES 152, MMP 100, MES 140, COM 240) |
| VAT Production Courses | 12 | Degree map footnote 3, "choose 4 courses" |
| VAT Advised Elective | 3 | Degree map footnote 5, "one course needed" |
| VAT Program Elective | 3 | Degree map footnote 6, "choose 1 course" |
| Media Arts and Technology Internship | 2 | Degree map (MEA 371 / MEA 201) |
| General Elective | 4 | Degree map footnote 9 |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

Unlike the majors already in this system with a colored Common-Core/
Flexible-Core map layout, VAT's map is organized purely by semester with
no category color-coding, and the program page's generic 12/18/30
breakdown does not describe it (see "Official sources" above). The
8-group structure above was derived by reconciling every course and
credit value printed on both official degree maps, verified to sum to
exactly 60.

Course-level credits in `Required Common Core` sum to 14 (ENG 101 3 + ENG
201 3 + MAT 160 4 + PHY 110 4), 2 credits above the group's published
`required_credits` of 12 — the expected STEM-variant overage; see
"General Elective" below.

## Choices and alternatives

- **MAT 160 (Common Core, Quantitative Reasoning).** No alternate shown on
  the two-year map. The five-semester map uses MAT 161.5 instead (a
  non-STEM-variant placement course, 3 credits) — not added as an
  additional row, matching the established ENG 100.5/MAT 161.5 handling in
  every other major so far. **Flagged for maintainer review** if
  placement-track students need explicit support.
- **PHY 110 / PHY 400 (Common Core, Life and Physical Sciences).**
  Footnote: "PHY 400 is an alternate option." Modeled with
  `alternatives=PHY 400`; PHY 400 is not part of this curriculum's own
  course list, so the validator is expected to warn about an external
  reference — expected and documented, same pattern as other majors'
  external-alternative warnings.
- **SPE 100 / SPE 102 (Flexible Core).** Modeled as two reciprocal rows
  (`alternatives=SPE 102` / `alternatives=SPE 100`), matching the pattern
  established for `soc_aa_courses.csv` and `nur_aas_courses.csv`.
- **U.S. Experience in Its Diversity (Flexible Core).** Footnote: "Please
  consult with an academic or faculty advisor" — advisory, not
  restrictive. Left as the standard, unrestricted `FC_US_EXPERIENCE` pool.
- **VAT Production Courses (12 credits, choose 4 of 6).** Footnote: "A
  total of 12 credits needed. Choose 4 courses from: VAT 161, 165, 171,
  261, 265 or 271." The four map slots shown across Semesters 2-3 are one
  pooled requirement, not four independent ones. All 6 courses modeled as
  literal rows in one `VAT Production Courses` group
  (`required_credits=12`, listed credits 18 — expected "choose 4 of 6"
  overage warning).
- **VAT Advised Elective (3 credits, choose 1 of 10 named courses).**
  Footnote lists 10 courses across 6 different departments (Media Arts,
  Business, Communication Studies, Health Education, Music, Theatre).
  Because these are 10 *specific* courses from *different* departments
  (not a subject-prefix wildcard like Sociology's Social Science
  Electives), each needed independent verification rather than a
  subject-restricted derived group. Only 6 of the 10 could be verified
  against an accessible department course-listing page: ANI 401, BUS 200,
  MEA 211, MEA 300, MMA 100, MMP 270. The remaining 4 (COM 245, HED 250,
  MUS 225, THE 110) returned repeated HTTP 503 errors from their
  respective department pages and were **not added as rows** — guessing
  at their titles/credits would misrepresent unverified data as
  confirmed. **Flagged for maintainer review.**
- **VAT Program Elective (3 credits, choose 1 of 5 named courses).**
  Footnote: "Choose 1 course from: VAT 300 or VAT 301/ANI 301 or VAT 302
  or VAT 303 or VAT 306." Reconciled as follows:
  - VAT 302, VAT 303 — verified, added as literal rows.
  - VAT 301 and ANI 301 — the footnote's slash notation ("VAT 301/ANI
    301") reads as if these were one cross-listed course, but the
    official course-listings page states VAT 301 is actually cross-listed
    with **MMP 301** ("Introduction to Video Graphics"), while ANI 301 is
    a distinct, separately-titled course ("Introduction to Motion
    Graphics and Visual Effects") with its own different prerequisite.
    Both were added as **separate** selectable rows rather than assuming
    which one the map's footnote meant, since both are independently
    verified, real, distinct courses. **Flagged for maintainer review**
    to confirm the map's intended pairing.
  - VAT 300, VAT 306 — could not be found on the department's
    course-listings page. **Not added as rows** (see "VAT Advised
    Elective" above for the same reasoning). **Flagged for maintainer
    review.**
- **Media Arts and Technology Internship (2 credits): MEA 371 / MEA
  201.** Footnote: "MEA 201 is an alternate option." Modeled as two
  reciprocal rows (`alternatives=MEA 201` / `alternatives=MEA 371`),
  matching the SPE 100/102 pattern — both are independently verified at 2
  credits each.
- **General Elective / STEM excess credit (4 credits).** Footnote: "A
  total of 4 credits required. Some of these credits can be satisfied by
  taking STEM variants in the Common Core." Only 2 credits appear
  explicitly on the two-year map (Semester 4); the other 2 are the excess
  generated because MAT 160 and PHY 110 are each 4-credit courses filling
  nominally 3-credit Common Core slots (+1 credit each = +2). Modeled as a
  single 4-credit placeholder, `VAT-AS-GENERAL`, matching the identical
  pattern and title text already used in `eco_aa_courses.csv` and
  `crj_aa_courses.csv` (`General Elective or Common Core STEM excess
  credits`). The current data model cannot move credits between groups,
  so this placeholder represents the full published 4-credit requirement
  as one row rather than splitting 2 explicit + 2 implied.

## Prerequisite review

- **VAT 100's official title.** The course-listings page (verified twice)
  gives VAT 100's title as "Introduction to Video Technology"; both
  degree maps print "Introduction to Video Arts and Technology" instead.
  Per lesson 2 in the curriculum-data feedback notes (titles must match
  the official course listing, not a map-specific variant), the
  course-listings page's title was used. **Flagged for maintainer
  review.**
- **VAT 161 / VAT 165 / VAT 171.** Footnote: "VAT 100 & MES 153 must be
  passed in order to take VAT 161, VAT 165 & VAT 171." Encoded as `VAT
  100|MES 153` for all three. "MES 152 is a corequisite" for the same
  three courses — same-semester corequisites have no primitive in the
  current prerequisite grammar; documented, not encoded.
- **VAT 261 / VAT 271.** Official course-listing prerequisites: "VAT 161
  or permission of the department" / "VAT171 or DEPT. PERMIT". Encoded as
  `VAT 161` / `VAT 171` respectively — the "or permission of department"
  alternate path is not course-based and is not translated, matching the
  established practice for similar non-course alternates elsewhere in
  this repo.
- **VAT 265.** Official course-listing prerequisite: "VAT165 and
  MMP100". Encoded as `VAT 165|MMP 100`.
- **COM 240 (Interpersonal Communication).** Footnote: "SPE 100 must be
  passed in order to take COM 240." Encoded as `SPE 100`.
- **ANI 301, VAT 302, VAT 303.** Official prerequisites are pure OR
  expressions ("VAT 161 or VAT 171[, or MMA 100, or MMP 100]") and are
  fully expressible; encoded as `VAT 161 or VAT 171 or MMA 100 or MMP 100`
  and `VAT 161 or VAT 171` respectively.
- **VAT 301.** Official prerequisite: "VAT 161 or VAT 171, and CIS 100" —
  an AND-of-OR expression. **Correction from the initial draft:** this was
  first left blank on the assumption the flat prerequisite grammar
  couldn't represent grouping. That assumption was wrong: `parse_relationships()`
  in `seed_database.py` splits the string on `|` into top-level AND groups
  first, and each `|`-separated group can independently contain an ` or `
  OR-list — so an AND-of-ORs (though not an OR-of-ANDs) is fully
  expressible. Encoded as `VAT 161 or VAT 171|CIS 100`, confirmed via
  `parse_relationships("VAT 161 or VAT 171|CIS 100")` returning
  `[(1, ["VAT 161", "VAT 171"]), (2, ["CIS 100"])]` — exactly (VAT 161 OR
  VAT 171) AND CIS 100. CIS 100 is external to this curriculum, so the
  validator is expected to warn about it, and it also means CIS 100 can
  never be checked off within VAT_AS's own progress view (it has no
  course card there) — so VAT 301 will always render as `locked` in
  practice for VAT majors, matching the same external-prerequisite
  consequence already seen elsewhere in this repo (e.g. Sociology's
  SOC 154 requiring the external ANT 100). This is expected, not a bug.
- **ANI 401.** Official prerequisite: "MMP 100 or MMA 100" — pure OR,
  encoded as `MMP 100 or MMA 100`.
- **MEA 211.** Official prerequisite: "MMA 100 and MMP 100" — encoded as
  `MMA 100|MMP 100`.
- **MEA 300.** Official prerequisite: "Any 200-level or above MMP, MMA,
  VAT or ANI course" — not a single enumerable course code; left blank.
  **Flagged for maintainer review.**
- **MMP 270.** Official prerequisite: "MMP 100" — encoded directly.
- **MEA 371.** Official prerequisite: "Departmental Approval" — not a
  course-based prerequisite; left blank and documented here rather than
  translated inaccurately.
- **MEA 201.** Official prerequisite: "ANI 401 or two 200-level courses
  from specified departments" — the "any two of a pool" condition has no
  primitive in the current prerequisite grammar; left blank. **Flagged
  for maintainer review.**
- **ENG 100.5 / MAT 161.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 160 respectively, identical pattern to
  every other major. Not added as additional rows.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive
  course is needed to graduate." Graduation-wide flag, not a course row;
  recorded here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. The two official degree-map dropbox links are no longer linked from
   the live VAT program page (which now serves a 2026-2027 map instead)
   and were recovered via the Wayback Machine. See "Official sources"
   above.
2. VAT 100's official title ("Introduction to Video Technology") differs
   from both degree maps' wording ("Introduction to Video Arts and
   Technology"); the course-listings page's title was used.
3. Four of the ten "VAT Advised Elective" courses (COM 245, HED 250, MUS
   225, THE 110) could not be verified due to repeated HTTP 503 errors on
   their department pages and are not represented as rows.
4. VAT 300 and VAT 306 (two of the five "VAT Program Elective" options)
   could not be found on the department's course-listings page and are
   not represented as rows.
5. The degree map's "VAT 301/ANI 301" footnote notation may intend a
   single cross-listed course, but the official catalog cross-lists VAT
   301 with MMP 301, not ANI 301 — both VAT 301 and ANI 301 were added as
   separate options rather than assuming which one was meant.
6. MEA 201's official prerequisite contains an "any two of a pool"
   condition that cannot be represented in the current flat prerequisite
   grammar and is left unencoded. VAT 301's AND-of-OR prerequisite,
   initially thought to have the same problem, was found to be fully
   expressible and is now encoded (see "Prerequisite review" above).
7. `docs/programs.csv` listed VAT_AS's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/vat_as_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/vat_as_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 6 warning(s).`
- Warnings explained (all 6):
  1. `alternatives` references `PHY 400` — external, not part of VAT_AS;
     see "Choices and alternatives" above.
  2. `prerequisites` references `CIS 100` (VAT 301) — external, not part
     of VAT_AS; see "Prerequisite review" above.
  3. `Required Common Core` lists 14 credits but requires 12 — expected
     2-credit STEM-variant overage (MAT 160 + PHY 110).
  4. `VAT Production Courses` lists 18 credits but requires 12 — expected
     "choose 4 of 6" pool.
  5. `VAT Advised Elective` lists 18 credits but requires 3 — expected
     "choose 1 of 6 verified" pool.
  6. `VAT Program Elective` lists 12 credits but requires 3 — expected
     "choose 1 of 4 verified" pool.
- Local seed completed: `python seed_database.py` — `VAT_AS` seeded
  cleanly with 30 courses.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: VAT 161 and COM 240 are both `locked`.
  2. After completing VAT 100 + MES 153: VAT 161 becomes `available`
     (VAT 261 stays `locked`).
  3. After completing VAT 161: VAT 261 becomes `available`.
  4. After completing SPE 100: COM 240 becomes `available`.
  All group cards render with correct titles (including the corrected
  "Introduction to Video Technology" for VAT 100 and both distinct titles
  for VAT 301/ANI 301), and SPE 100/SPE 102 and MEA 371/MEA 201 both
  render as explicit "Alternative requirement - CHOOSE ONE" widgets. No
  console errors.
