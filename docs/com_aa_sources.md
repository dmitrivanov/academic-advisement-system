# Curriculum Source Notes: Communication Studies (A.A.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Speech, Communications and Theatre Arts (SCT)
- Program code: COM_AA
- Program name: Communication Studies
- Degree type: AA
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-16

Note: `docs/programs.csv` previously listed COM_AA's `catalog_year` as
`2026`, not `2025-2026` — the same recurring mismatch already found and
corrected for every prior BMCC major added this way. Fixed before the
first seed on this branch, so no stale empty program placeholder was
ever created.

## Official sources

1. Program map (two-year)
   - Direct URL: https://www.dropbox.com/s/6o0f5a1nr3ceq1k/com2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_com_2_year_2025_2026.pdf`
   - Unlike Nursing, VAT, Cybersecurity Certificate, Digital Marketing,
     and Animation and Motion Graphics, this direct link was **still
     live** on the program page at the time of writing — no Wayback
     Machine recovery was needed.

2. Program map (five-semester)
   - Direct URL: https://www.dropbox.com/s/7mgbnjyfyw6si9h/com3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_com_5_semester_2025_2026.pdf`

3. Program requirements page
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/speech/communication-studies/

4. Course listings
   - Speech, Communications and Theatre Arts (COM, SPE, THE courses): https://www.bmcc.cuny.edu/academics/departments/speech/course-listings/
   - Media Arts and Technology (MES 140, MES 152, MES 153): https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/course-listings/
   - Business Management (MAR 100, MAR 220, MAR 230, BUS 150): https://www.bmcc.cuny.edu/academics/departments/business-management/course-listings/
   - Mathematics (MAT 161): https://www.bmcc.cuny.edu/academics/departments/math/course-listings/
   - MUS 107 and ART 106 titles sourced from `docs/pathways_courses.csv`
     (already-vetted canonical Pathways data), since the Music and Art &
     Design department pages were inaccessible (see "Prerequisite review"
     below).
   - LIN 150's home department course-listing page could not be located.

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Degree map (ENG 101, ENG 201, MAT 161, Life and Physical Sciences) |
| Flexible Core | 6 | Degree map (SPE 100, Scientific World) |
| Program Requirements | 24 | Degree map (8 distinct required-course slots) |
| COM Advised Elective | 12 | Degree map's own course table (see discrepancy below) |
| COM Program Elective | 6 | Degree map footnote 5, "choose 2 courses" |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

**Discrepancy in the official source, resolved in favor of the map's own
course table over its footnote text:** both the two-year map's footnote 3
and the five-semester map's footnote 6 state "Choose 5 three-credit
courses... for a total of 15 credits" for the COM Advised Elective area.
But both maps' own printed course tables show only **4** such slots (12
credits) — 1 in Semester 2, 1 in Semester 3, 2 in Semester 4 on the
two-year map, and the identical 4-slot pattern on the five-semester map.
Reconciling every course and credit value printed on both maps confirms
the published 60-credit total only balances using 4 slots (12 credits);
using 5 (15 credits) would push the total to 63. This was verified
against the actual downloaded PDFs (not just the submitted image), and
the inconsistency is present in **both** independent map documents, not a
transcription error on this submission's part. Modeled as a 12-credit,
4-course requirement. **Flagged for maintainer review.**

Unlike most majors, this program's Common Core has **no STEM-variant
credit overage** — MAT 161 is genuinely 3 credits (confirmed via the
Mathematics course-listings page), unlike MAT 150/MAT 160 used elsewhere.
No General Elective placeholder was needed.

Flexible Core has only 2 slots (6 credits) — Creative Expression (SPE
100/102) and Scientific World — not the full 6-slot, 18-credit pattern
seen in Sociology, Criminal Justice, or Digital Marketing. Individual and
Society, U.S. Experience, World Cultures, and a second Creative Expression
course are entirely absent from this map, replaced by specific required
program courses, the same pattern already documented for Video Arts and
Technology and Animation and Motion Graphics (this program's siblings in
adjacent departments).

## Choices and alternatives

- **MAT 161 (Common Core, Mathematical and Quantitative Reasoning).** No
  alternate shown. The five-semester map uses MAT 161.5 instead (a
  placement course) — not added as an additional row, matching the
  established ENG 100.5/MAT 161.5 handling in every other major so far.
- **Life and Physical Sciences, Scientific World (Flexible Core).** Both
  footnoted only with advisory "consult an advisor" language. Left as the
  standard, unrestricted shared pools.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression).** Modeled as
  two reciprocal rows, matching the pattern established for
  `soc_aa_courses.csv`, `nur_aas_courses.csv`, `vat_as_courses.csv`,
  `dmk_as_courses.csv`, and `amg_as_courses.csv`.
- **THE 100 / MES 153 / MUS 107 / ART 106 (Program Requirements).**
  Footnote: "MES 153, MUS 107, or ART 106 are alternative course
  options." A **four-way** alternative cluster, the first of its kind in
  this repo (every prior reciprocal-alternatives case had exactly two
  options). Modeled with THE 100 as the hub (`alternatives=MES 153|MUS
  107|ART 106`) and each alternate individually pointing back to THE 100
  (`alternatives=THE 100`). `alternativeComponents()` in
  `frontend/db_progress_graph.html` performs a graph traversal starting
  from any course in the cluster, so a star topology (all three alternates
  linked to the hub, not to each other) is sufficient to group all four
  into one credit-counted slot.
- **COM Advised Elective (12 credits, choose 4).** See "Credit
  reconciliation" above for the slot-count discrepancy. Official
  eligibility list: "SPE xx, COM xxx, THE xxx, GWS xxx, MES 152, ENG xxx,
  MAR 100, MAR 220, MAR 230, BUS 150, or ANY social science course," with
  a sub-rule requiring "at least three from SPE, COM, THE, or GWS."
  Modeled as two ordered selectors: a 9-credit discipline-core group
  restricted to SPE/COM/THE/GWS, followed by one 3-credit additional-choice
  group containing those subjects, ENG and the social-science disciplines,
  plus MES 152, MAR 100/220/230 and BUS 150. This split machine-enforces
  the official "at least three" rule while preserving all published choices.
- **COM Program Elective (6 credits, choose 2).** Footnote: "Choose 2
  courses from any Communication courses." Modeled as a subject-wildcard
  placeholder (`include_subject_codes=COM`).
- **Cross-pool double-counting.** The progress allocator reserves fixed
  requirements first and then allocates electives by display order, so a
  completed course cannot earn credit in two requirement groups.

## Prerequisite review

- **COM 240 (Interpersonal Communication) / COM 245 (The Mass Media).**
  Official prerequisite for both: "SPE 100 or permission of department."
  Encoded as `SPE 100`; the permission-of-department alternate is not
  course-based and not translated.
- **COM 255 (Intercultural Communication).** Official prerequisite: "SPE
  100 or SPE 102." Encoded exactly as `SPE 100 or SPE 102`.
- **MAR 220 / MAR 230.** Official prerequisite for both: "ENG 101 and MAR
  100." Encoded as `ENG 101|MAR 100`, matching the identical encoding
  already used for these same two courses in `dmk_as_courses.csv`.
- **BUS 150.** Official prerequisite: "ENG 101, ENG 201, and BUS 104."
  Encoded as `ENG 101|ENG 201|BUS 104`, matching the identical encoding
  already used in `dmk_as_courses.csv` and `bba_as_courses.csv`. BUS 104
  is external to this curriculum, so the validator is expected to warn
  about it.
- **LIN 150.** Could not locate LIN 150 on the Speech, Communications and
  Theatre Arts department's or the English department's course-listings
  pages to independently verify a prerequisite or exact department home —
  the same difficulty already encountered with LIN 250 during the
  Criminal Justice submission. Title and credits are sourced from both
  degree maps, which agree exactly. No prerequisite was encoded (left
  blank) rather than guessed. **Flagged for maintainer review.**
- **MUS 107 / ART 106.** No prerequisite information available (not
  independently verified — sourced from `docs/pathways_courses.csv`,
  which does not carry prerequisite data); left blank.
- **ENG 100.5 / MAT 161.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 161 respectively, identical pattern to
  every other major. Not added as additional rows.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive
  course is needed to fulfill graduation requirement." Graduation-wide
  flag, not a course row; recorded here and in the degree-map JSON
  `sequence_notes`.

## Ambiguities requiring maintainer review

1. Both official degree maps' footnotes state "5 courses / 15 credits"
   for the COM Advised Elective area, but both maps' own course tables
   only show 4 slots (12 credits), and the published 60-credit total only
   balances with 4. See "Credit reconciliation" above.
2. The COM Advised Elective pool's "any ENG course," "any social science
   course," and "at least three from SPE/COM/THE/GWS" conditions are not
   enforced — see "Choices and alternatives" above.
3. The COM Advised Elective wildcard pool can overlap with courses
   already separately required elsewhere in this curriculum (e.g. SPE
   100, COM 240/245/255) — the schema has no exclusion mechanism for
   this. See "Choices and alternatives" above.
4. LIN 150's prerequisite could not be independently verified; left
   blank rather than guessed.
5. MUS 107's and ART 106's prerequisites could not be independently
   verified (sourced from canonical Pathways data without prerequisite
   information); left blank.
6. `docs/programs.csv` listed COM_AA's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/com_aa_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/com_aa_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 2 warning(s).`
- Warnings explained (both):
  1. `prerequisites` references `BUS 104` (BUS 150) — external, not part
     of COM_AA; see "Prerequisite review" above.
  2. `COM Advised Elective` lists 24 credits but requires 12 — expected
     "choose 4 of a larger pool" behavior.
- Local seed completed: `python seed_database.py` — `COM_AA` seeded
  cleanly with 18 courses; no stale placeholder needed cleanup since
  `programs.csv` was corrected before the first seed on this branch.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: COM 240 and COM 255 are both `locked`.
  2. After completing SPE 100: both become `available`.
  The four-way THE 100/MES 153/MUS 107/ART 106 alternative cluster renders
  correctly as a single "Alternative requirement - Choose one" widget with
  all four options listed, confirming the star-topology graph traversal
  works for more than two alternatives. All group cards render with
  correct titles and credit targets. No console errors.
