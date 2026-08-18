# Curriculum Source Notes: Multimedia Programming and Design (A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Media Arts and Technology (MMA)
- Program code: MMP_AS
- Program name: Multimedia Programming and Design
- Degree type: AS
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-16

Note: `docs/programs.csv` previously listed MMP_AS's `catalog_year` as
`2026`, not `2025-2026` — the same recurring mismatch already found and
corrected for every prior BMCC major added this way. Fixed before the
first seed on this branch, so no stale empty program placeholder was
ever created.

## Official sources

1. Program map (two-year)
   - Direct URL: https://www.dropbox.com/s/fdcjdgb5wy3szva/mmd2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_mmd_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Direct URL: https://www.dropbox.com/s/8f9d5qi6pqd2et1/mmd3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_mmd_5_semester_2025_2026.pdf`

   As with most majors added this way, neither direct URL is currently
   linked from the live program page (which now links a newer 2026-2027
   map instead); both were recovered from a Wayback Machine snapshot of
   the page taken while 2025-2026 was current. **Flagged for maintainer
   review**: confirm these dropbox links remain stable.

3. Program requirements page
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/multimedia-programming-and-design/
   - This page's own requirement-section summary describes the generic,
     boilerplate 12/18/30 Common-Core/Flexible-Core/Curriculum-Requirements
     split used across most BMCC AA/AS programs. It does **not** match
     this degree map, the same finding already documented for Video Arts
     and Technology and Animation and Motion Graphics.

4. Course listings
   - Media Arts and Technology (MMP, MMA, ANI, MES, MEA courses): https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/course-listings/
   - Business Management (BUS 110.5, BUS 200): https://www.bmcc.cuny.edu/academics/departments/business-management/course-listings/
   - Computer Information Systems (CIS 165, CSC 101, CSC 110, CSC 111): https://www.bmcc.cuny.edu/academics/departments/cis/course-listings/
   - Speech, Communications and Theatre Arts (COM 240, COM 245): https://www.bmcc.cuny.edu/academics/departments/speech/course-listings/
   - Mathematics (MAT 161): https://www.bmcc.cuny.edu/academics/departments/math/course-listings/
   - Science (PHY 110): https://www.bmcc.cuny.edu/academics/departments/science/science-program/
   - ART 113 and ART 106 titles sourced from `docs/pathways_courses.csv`
     (already-vetted canonical Pathways data); ART 166's title reused from
     `amg_as_courses.csv` (map-sourced there, since the Art & Design
     department page was inaccessible — see "Choices and alternatives"
     below).

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Degree map (ENG 101, ENG 201, MAT 161, PHY 110) |
| Flexible Core | 6 | Degree map (SPE 100, U.S. Experience) |
| Program Requirements | 24 | Degree map (8 distinct required-course slots) |
| Multimedia Discipline Sequence | 6 | Degree map footnote 4, "choose 6 credits within one sequence" |
| Multimedia Program Elective | 6 | Degree map footnote 5, "choose 2 courses" |
| Multimedia Advised Elective | 3 | Degree map footnote 11, "choose 1 course" |
| General Elective | 3 | Degree map footnote 13 |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

Common Core is declared at the standard nominal 12 (actual listed 13, +1
credit STEM-variant overage from PHY 110), with the excess absorbed by
General Elective's full 3-credit declared value — the same pattern used
in `eco_aa_courses.csv`, `crj_aa_courses.csv`, `vat_as_courses.csv`, and
`dmk_as_courses.csv` (not the alternate "absorb it directly into Common
Core" pattern used for `amg_as_courses.csv`, which has no separate
General Elective line at all).

Flexible Core has only 2 slots (6 credits) — Creative Expression (SPE
100/102) and U.S. Experience in Its Diversity — not the full 6-slot,
18-credit pattern seen in Sociology or Digital Marketing. Individual and
Society, Scientific World, World Cultures, and a second Creative
Expression course are all absent from the map as open categories, each
instead satisfied by a specific required program course (MES 152, ART
113, MES 160) — see "Choices and alternatives" below.

## Choices and alternatives

- **MES 152, ART 113, MES 160 — Pathways-substitute Program
  Requirements.** Each is explicitly annotated on the map: "MES 152 will
  satisfy the Individual and Society requirement," "ART 113 will satisfy
  one of the Creative Expression requirements," "MES 160 will satisfy the
  World Cultures and Global Issues requirement." Unlike a real Flexible
  Core choice, each is a single, specific, non-substitutable required
  course (shown directly in the map's own course table, not as an "XXX
  xxx" open placeholder) — modeled as fixed `Program Requirements` rows,
  matching how VAT_AS and AMG_AS modeled their own program-specific
  Pathways substitutions.
- **PHY 110 / PHY 400 (Common Core, Life and Physical Sciences).**
  Footnote: "PHY400 is an alternate option." Modeled with
  `alternatives=PHY 400`; PHY 400 is not part of this curriculum's own
  course list, so the validator is expected to warn about it.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression).** Modeled as
  two reciprocal rows, matching the pattern established for
  `soc_aa_courses.csv`, `vat_as_courses.csv`, `amg_as_courses.csv`,
  `dmk_as_courses.csv`, and `com_aa_courses.csv`.
- **U.S. Experience in Its Diversity (Flexible Core).** Footnote: "Please
  consult with an academic or faculty advisor" — advisory, not
  restrictive. Left as the standard, unrestricted `FC_US_EXPERIENCE` pool.
- **Multimedia Discipline Sequence (6 credits, choose 2 courses "within
  one sequence").** Footnote 4 names three sequences (Game Design: MMP
  210/270/271; UX and Web Design: MMP 240/350/202; Graphic Design: MMA
  215/225/235), each itself a 3-course pool, with the student expected to
  pick 2 courses from a *single* sequence, not mix across sequences. The
  nine valid two-course combinations are encoded in `completion_options`,
  so mixing courses from different sequences cannot satisfy the group.
- **Multimedia Program Elective (6 credits, choose 2 courses).** Footnote
  5's named list: MMP 202, 210, 240, 310, 270, 271, 350, MMA 215, 225,
  235, ANI 260, ANI 401, MEA 211, MEA 300, or "any 200-level or higher
  MMA or MMP course." The footnote explicitly states: "Classes cannot
  count both as MMD program elective and for another program
  requirement" — but 9 of these 14 named courses are *also* part of the
  Multimedia Discipline Sequence pool above. The schema has no
  progress page allocates completed electives in display order and never
  allocates one course to a second elective group, enforcing the source's
  no-double-counting rule. The open-ended "any 200-level or
  higher MMA or MMP course" addition is not enumerated or enforced.
- **Multimedia Advised Elective (3 credits, choose 1 of 20 named
  courses).** All 20 courses in footnote 11 are selectable. The previously
  missing Art, MUS 123, and SBE 100 records were verified against BMCC's
  current Music and Art and Business Management course listings.
- **MEA 371 / MEA 201 (Media Arts and Technology Internship).**
  Footnote: "MEA 201 is an alternate option." Modeled as two reciprocal
  rows, matching the identical pattern already used in `vat_as_courses.csv`
  and `amg_as_courses.csv`.
- **General Elective / STEM excess credit (3 credits).** Footnote: "A
  total of 3 credits required. Some of these credits can be satisfied by
  taking STEM variants in the Common Core." Only 2 credits appear
  explicitly on the two-year map (Semester 4) because PHY 110 is a
  4-credit course filling a nominally 3-credit Common Core slot (+1
  credit). Modeled as a single 3-credit placeholder, `MMD-AS-GENERAL`,
  matching the identical pattern and title text already used in
  `eco_aa_courses.csv`, `crj_aa_courses.csv`, `vat_as_courses.csv`, and
  `dmk_as_courses.csv`.

## Prerequisite review

- **MMP 200 (Multimedia Design).** Official prerequisite: "MMP 100 and
  MMA 100." Encoded as `MMP 100|MMA 100`.
- **MMP 210 (Multimedia Programming I) / MMP 270 (Introduction to Video
  Game Design) / MMP 271 (3D Game Development) / MMP 202 (Introduction to
  User Experience Design).** Official prerequisite for all four: "MMP
  100." Encoded as `MMP 100`.
- **MMP 240 (Web Design).** Official prerequisite: "CIS 180 or MMP 100."
  Encoded as `CIS 180 or MMP 100`, matching the identical encoding already
  used for this same course in `vat_as_courses.csv`. CIS 180 is not part
  of this curriculum, so the validator is expected to warn about it.
- **MMP 350 (Advanced Web Design).** Official prerequisite: "MMP 240."
  Encoded as `MMP 240`.
- **MMP 310 (Multimedia Programming II).** Official prerequisite: "MMP
  210." Encoded as `MMP 210`.
- **MMP 460 (Multimedia Project Lab).** Official prerequisite (quoted
  exactly): "MMP 200 and [any 200-level MMP or MMA course]" — matching
  this program's own footnote 10 exactly (a rare case of full map/catalog
  agreement). Only the concrete part (`MMP 200`) is encoded; the "any
  200-level" portion has no specific course code and cannot be enumerated
  without guessing.
- **MMA 215 (Typography and Layout) / MMA 225 (Digital Imaging for
  Graphic Design) / MMA 235 (Visual Communication and Design).** Official
  prerequisite for all three: "MMA 100 or ART 100 or ART 101." Encoded
  exactly as `MMA 100 or ART 100 or ART 101`. ART 100 and ART 101 are not
  part of this curriculum, so the validator is expected to warn about
  both.
- **ANI 260 / ANI 401.** Official prerequisite for both: "MMP 100 or MMA
  100." Encoded as `MMP 100 or MMA 100`, matching the identical encoding
  already established for these same two courses in `vat_as_courses.csv`
  and `amg_as_courses.csv` (both courses are shared across all three
  Media Arts and Technology majors).
- **MEA 211.** Official prerequisite: "MMA 100 and MMP 100." Encoded as
  `MMA 100|MMP 100`, matching the identical encoding already used in
  `vat_as_courses.csv`.
- **CIS 165, CSC 101, CSC 110, CSC 111, COM 240, COM 245, BUS 110.5, BUS
  200.** All reused with identical prerequisite encodings already
  established for these same courses in `cyb_cert_courses.csv`,
  `cis_courses.csv`, `com_aa_courses.csv`, `dmk_as_courses.csv`, and
  `vat_as_courses.csv` respectively.
- **ENG 100.5 / MAT 161.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 161 respectively, identical pattern to
  every other major. Not added as additional rows.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive
  course is needed to graduate." Graduation-wide flag, not a course row;
  recorded here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. The two official degree-map dropbox links are no longer linked from
   the live program page (which now serves a 2026-2027 map instead) and
   were recovered via the Wayback Machine.
2. `docs/programs.csv` listed MMP_AS's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/mmp_as_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/mmp_as_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 22 warning(s).`
- Warnings explained (all 22): `alternatives`/`prerequisites` external
  references to `PHY 400`, `CIS 180` (x2, once each for MMP 240's two
  appearances in the Discipline Sequence and Program Elective groups),
  `ART 100`/`ART 101` (x6, once each for MMA 215/225/235's two
  appearances in both groups), and `MAT 206`/`MAT 206.5`/`MAT 301` (CSC
  111, reused verbatim from `cis_courses.csv`) — all expected, matching
  "Prerequisite review" above. Plus 4 group-credit-overage warnings:
  `Required Common Core` (13 vs 12, expected PHY 110 STEM overage),
  `Multimedia Discipline Sequence` (27 vs 6, expected "choose 2 of 9"),
  `Multimedia Program Elective` (42 vs 6, expected "choose 2 of 14
  named"), and `Multimedia Advised Elective` (58 vs 3, expected "choose
  1 of 20").
- Local seed completed: `python seed_database.py` — `MMP_AS` seeded
  cleanly with 50 course associations (41 distinct courses; some appear
  in two groups, see "Choices and alternatives" above); no stale
  placeholder needed cleanup since `programs.csv` was corrected before
  the first seed on this branch.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: MMP 200 is `locked`.
  2. After completing MMP 100 + MMA 100: MMP 200 becomes `available`.
  3. Before completing MMP 200: MMP 460 stays `locked`.
  4. After completing MMP 200: MMP 460 becomes `available`.
  All group cards render with correct titles and credit targets. Shared
  sequence/program-elective courses remain synchronized visually, while
  the allocation logic prevents one completion from satisfying both
  groups. No console errors.
