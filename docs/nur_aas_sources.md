# Curriculum Source Notes: Nursing (A.A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Nursing (NUR)
- Program code: NUR_AAS
- Program name: Nursing
- Degree type: AAS
- Effective catalog year: 2025-2026
- Published total credits: 65
- Date accessed: 2026-08-13

Note: `docs/programs.csv` previously listed NUR_AAS's `catalog_year` as `2026`,
not `2025-2026` — the same recurring mismatch already found and corrected
for every prior BMCC major added this way (ECO_AA, HIS_AA, SOC_AA, CRJ_AA).
Fixed before the first seed on this branch, so no stale empty program
placeholder was ever created.

## Official sources

1. Program map ("Undeclared Health (UDH) to Nursing (NUR)", Fall Start Day
   & Evening/Weekend, three-year)
   - Direct URL: https://www.dropbox.com/s/5a3mtwdwb435g7w/nur-fall-3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_nursing_fall_start_2025_2026.pdf`

2. Program map (Spring Start Day, three-year)
   - Direct URL: https://www.dropbox.com/s/l7z6zhinea1dbx2/nur-spring-day-3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_nursing_spring_day_2025_2026.pdf`

3. Program map (Spring Start Evening/Weekend, four-year)
   - Direct URL: https://www.dropbox.com/s/zohuhxu9qqau4h9/nur-spring-eve-3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_nursing_spring_evening_2025_2026.pdf`

   These three direct URLs are not currently linked from the live nursing
   program page (which now links a newer 2026-2027 map instead); they were
   recovered from a Wayback Machine snapshot of the page
   (`web.archive.org/web/20250819235446/.../nursing-program/`) taken while
   2025-2026 was current, matching the 2025-2026 maps supplied for this
   submission. **Flagged for maintainer review**: confirm these dropbox
   links remain stable, since they are no longer discoverable from the live
   page.

4. Program requirements page
   - Title: Registered Nursing (A.A.S.) - BMCC
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/nursing/nursing-program/
   - Used for group credit totals ("Required Common Core" 13, "Flexible
     Core" 10, "Curriculum Requirements" 42) and the general/Speech course
     rows, since it uses the same section headers as the degree maps'
     underlying credit breakdown.

5. Course listings
   - Nursing (NUR courses): https://www.bmcc.cuny.edu/academics/departments/nursing/course-listings/
   - Science for Health (CHE 121, BIO 425, BIO 426, BIO 420): https://www.bmcc.cuny.edu/academics/departments/science/science-for-health-professions/
   - Mathematics (MAT 104): https://www.bmcc.cuny.edu/academics/departments/math/mathematics-program/
   - Psychology (PSY 100): https://www.bmcc.cuny.edu/academics/departments/social-sciences/psychology/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 13 | Program page "Required Common Core" |
| Flexible Core | 10 | Program page "Flexible Core" |
| Curriculum Requirements | 42 | Program page "Curriculum Requirements" |
| **Published program total** | **65** | All three degree maps, "TOTAL: 65 CREDITS" |

Unlike the BMCC A.A. majors already in this system (Economics, History,
Sociology, Criminal Justice), this AAS curriculum has **no elective choice
groups at all** — all three degree maps and the program page list exactly
15 specific, individually-required courses with no "choose from" language
anywhere in any footnote. `choice_group_code` is left blank on every row;
no `program_choice_group_adjustments.csv` rows were needed.

The validator is expected to warn that the program totals 65, not 60,
credits (`Associate-degree group requirements total 65, not 60 credits`).
This is expected and correct: NUR_AAS is a 65-credit AAS program per all
three official degree maps, not a 60-credit A.A./A.S. program.

## Choices and alternatives

- **SPE 100 / SPE 102 (Flexible Core).** Footnote: "SPE 102 is an option
  for non-native speakers of English." Modeled as two reciprocal rows
  (`alternatives=SPE 102` / `alternatives=SPE 100`), matching the pattern
  established for `soc_aa_courses.csv` and `acct_aas_courses.csv` —
  `alternativeComponents()` in `frontend/db_progress_graph.html` groups
  reciprocally-linked courses into one credit-counted slot, so this does
  not double the Flexible Core total.
- **Three map variants, one requirement set.** The Fall Start (three-year),
  Spring Start Day (three-year), and Spring Start Evening/Weekend
  (four-year) maps all require the identical 15 courses at the identical
  credit values — they differ only in which term each course is scheduled
  in and how many terms the sequence spans. All three are represented in
  `bmcc_nur_degree_map_2025_2026.json`'s `semesters` (Fall Start, the
  default) and `alternate_pathways` (the other two), each verified to sum
  to 65 credits.
- **CHE 121's title.** The degree maps wrap it across two lines
  ("Fundamentals of General, / Organic and Biological Chemistry I"); the
  comma in the joined title required CSV-quoting the field
  (`"Fundamentals of General, Organic and Biological Chemistry I"`).

## Prerequisite review

- **BIO 425 (Anatomy and Physiology I).** Footnote: "CHE 121 must be
  passed in order to take BIO 425." Encoded as `CHE 121`.
- **BIO 426 (Anatomy and Physiology II).** Footnote: "BIO 425 must be
  passed in order to take BIO 426." Encoded as `BIO 425`.
- **BIO 420 (Microbiology).** Footnote: "BIO 426 must be passed in order
  to take BIO 420." Encoded as `BIO 426`.
- **NUR 112 (Nursing Process I).** Footnote (all three maps): "Students
  must first complete CHE 121, ENG 101, BIO 425, MAT 104, and PSY 100, in
  order to sit for the Nursing Admission test and apply for the clinical
  rotation." Encoded as `CHE 121|ENG 101|BIO 425|MAT 104|PSY 100`.
  **Two things are intentionally not encoded:**
  1. The Nursing Admission Test and competitive clinical-rotation
     acceptance itself is an application/testing gate, not a course
     completion — not translatable into `prerequisites`, matching the
     established practice for non-course gates (e.g. "permission of
     department" elsewhere in this repo).
  2. The Fall and Spring Start Evening/Weekend maps' footnotes add: "In
     addition, evening/weekend students must complete BIO 426 and BIO 420
     before starting NUR 112." This track-specific addition was
     **considered and rejected** as a universal requirement: encoding it
     for all students would be a knowingly stricter substitution that
     incorrectly blocks Day-track students, who do not need BIO 426/BIO
     420 first — the same category of mistake flagged and reverted in the
     Sociology PR review (see lesson in the curriculum-data feedback
     notes). The schema has no concept of a student's enrollment track, so
     this remains documented but unenforced. **Flagged for maintainer
     review.**
- **NUR 211 (Nursing Process II).** Degree map footnote: "NUR 112 must be
  passed in order to take NUR 211." The official course-listings page
  states a fuller "Prerequisites: NUR 112, BIO 426, PSY 240, Corequisites:
  BIO 420." Reconciled as follows:
  - `NUR 112` — encoded, matches all three maps.
  - `BIO 426` — encoded (`prerequisites=NUR 112|BIO 426`). Not stated on
    any degree map footnote, but BIO 426 is already completed before NUR
    211 begins in the natural term sequence of all three official maps, so
    adding it does not conflict with any map's own sequencing.
  - `PSY 240` — **not encoded.** This course does not appear on any of the
    three official degree maps and is not part of this program's course
    list; encoding an unverified, out-of-curriculum course code would mean
    guessing rather than modeling a confirmed requirement. **Flagged for
    maintainer review** to confirm whether this catalog line is current.
  - `BIO 420` (listed as a "corequisite") — **not encoded.** Same-semester
    corequisites have no primitive in the current prerequisite grammar
    (see NUR 411/NUR 415 below), and per the degree maps' own sequencing
    BIO 420 is completed a full term *before* NUR 211 in all three
    variants, not simultaneously — the catalog's corequisite label does
    not match the current maps' term-by-term structure. Documented, not
    encoded.
- **NUR 313 (Nursing Process III).** Degree map footnote: "NUR 211 must be
  passed in order to take NUR 313." Encoded as `NUR 211`. The
  course-listings page's "NUR 211 and all previous prerequisites" is
  transitively equivalent given the strict NUR 112 -> NUR 211 -> NUR 313
  chain, so no information is lost by encoding only the direct link. The
  course-listings page's stated corequisites "SPE 100, ENG 201" also do
  not match the current maps' sequencing (both are completed a full year
  or more before NUR 313 in every variant) and are not encoded.
- **NUR 411 / NUR 415 (Nursing Process IV / Professional Issues).** Degree
  map footnote: "NUR 313 must be passed in order to take NUR 411 and NUR
  415," and "NUR 411 and NUR 415 are co-requisite courses and must be
  taken in the same semester." Both encoded with `prerequisites=NUR 313`;
  the same-semester corequisite relationship between them has no primitive
  in the current prerequisite grammar and is documented in
  `bmcc_nur_degree_map_2025_2026.json`'s `sequence_notes` rather than
  guessed at. The course-listings page's fuller "NUR 112, NUR 211 and NUR
  313" prerequisite for NUR 415 is transitively equivalent to `NUR 313`
  given the strict chain above.
- **Writing Intensive requirement.** All three maps: "A Writing Intensive
  course is needed to graduate." Graduation-wide flag, not a course row;
  recorded here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. The three official degree-map dropbox links are no longer linked from
   the live nursing program page (which now serves a 2026-2027 map
   instead) and were recovered via the Wayback Machine. See "Official
   sources" above.
2. Evening/Weekend-track students' additional BIO 426/BIO 420 requirement
   before NUR 112 is not enforced (see "Prerequisite review" above) —
   deliberately, to avoid incorrectly blocking Day-track students.
3. NUR 211's official course-listing prerequisite lists PSY 240, which is
   not part of this curriculum and was not encoded (see "Prerequisite
   review" above).
4. Several "corequisite" pairings on the official course-listings page
   (BIO 420 with NUR 211; SPE 100/ENG 201 with NUR 313) do not match the
   degree maps' own term-by-term sequencing and were not encoded.
5. `docs/programs.csv` listed NUR_AAS's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/nur_aas_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/nur_aas_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 1 warning(s).`
- Warning explained: "Associate-degree group requirements total 65, not 60
  credits" — expected; see "Credit reconciliation" above.
- Local seed completed: `python seed_database.py` — `NUR_AAS` seeded
  cleanly with 15 courses; no stale placeholder needed cleanup since
  `programs.csv` was corrected before the first seed on this branch.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: NUR 112 card is `locked`.
  2. After completing CHE 121, ENG 101, BIO 425, MAT 104, PSY 100 (the
     universal minimum): NUR 112 becomes `available`.
  3. Completing BIO 425 -> BIO 426 -> BIO 420 in sequence: each unlocks
     correctly after its direct predecessor.
  4. Completing NUR 112 -> NUR 211 -> NUR 313 in sequence: each unlocks
     correctly.
  5. After NUR 313: both NUR 411 and NUR 415 become `available` together
     (their shared true prerequisite), matching the co-requisite pairing's
     intent even though same-semester enrollment itself isn't enforced.
  All group cards render with correct titles (including the corrected
  "...Nursing Care" wording for NUR 313 and the properly-quoted CHE 121
  title) and credit targets; SPE 100/SPE 102 render as an explicit
  "Alternative requirement - CHOOSE ONE" widget. No console errors.
