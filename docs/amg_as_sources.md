# Curriculum Source Notes: Animation and Motion Graphics (A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Media Arts and Technology (MMA)
- Program code: AMG_AS
- Program name: Animation and Motion Graphics
- Degree type: AS
- Effective catalog year: 2025-2026
- Published total credits: 60
- Date accessed: 2026-08-15

Note: `docs/programs.csv` previously listed AMG_AS's `catalog_year` as
`2026`, not `2025-2026` — the same recurring mismatch already found and
corrected for every prior BMCC major added this way. Fixed before the
first seed on this branch, so no stale empty program placeholder was
ever created.

Note on file naming: this file is named `amg_as_courses.csv` (matching
program code `AMG_AS`), not `ani_as_courses.csv` (which would match the
program's parenthetical abbreviation "ANI" on the degree map) — the
validator explicitly warns when a filename doesn't match its program
code, and following the program code keeps this consistent with every
other file in `docs/`.

## Official sources

1. Program map (two-year)
   - Direct URL: https://www.dropbox.com/s/q2xiqk2rusfg52r/ani2yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_ani_2_year_2025_2026.pdf`

2. Program map (five-semester)
   - Direct URL: https://www.dropbox.com/s/vl42rhif1qdwrio/ani3yr.pdf?raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_ani_5_semester_2025_2026.pdf`

   As with every BMCC major added this way, neither direct URL is
   currently linked from the live program page (which now links a newer
   2026-2027 map instead); both were recovered from a Wayback Machine
   snapshot of the page taken while 2025-2026 was current. **Flagged for
   maintainer review**: confirm these dropbox links remain stable.

3. Program requirements page
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/animation-and-motion-graphics/
   - This page's own requirement-section summary describes the generic,
     boilerplate 12/18/30 Common-Core/Flexible-Core/Curriculum-Requirements
     split used across most BMCC AA/AS programs. It does **not** match
     this degree map, the same finding already documented for Video Arts
     and Technology (this program's sibling major in the same
     department). The group structure below is derived directly from the
     degree maps' own course-by-course content and credit totals.

4. Course listings
   - Media Arts and Technology (MMP, MMA, ANI, MES, MEA courses): https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/course-listings/
   - Mathematics (MAT 161): https://www.bmcc.cuny.edu/academics/departments/math/course-listings/
   - Science (PHY 110): https://www.bmcc.cuny.edu/academics/departments/science/science-program/
   - Art & Design (ART 166, ART 269, ART 176): page returned repeated HTTP
     503 errors; titles for ART 166/ART 269 sourced from the degree maps
     only (both agree), and ART 176's title could not be verified at all
     (see "Choices and alternatives" below).

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 13 | Degree map (ENG 101, ENG 201, MAT 161, PHY 110) |
| Flexible Core | 9 | Degree map (Creative Expression x2, U.S. Experience) |
| Program Requirements | 38 | Degree map (13 distinct required-course slots) |
| **Published program total** | **60** | Both degree maps, "TOTAL: 60 CREDITS" |

This program's Required Common Core is declared at **13 credits**, not
the nominal 12 used by every other major so far. Unlike Economics,
Criminal Justice, Digital Marketing, or Video Arts and Technology — all
of which have a separate "General Elective" placeholder whose declared
credits absorb a STEM-variant course's excess above its nominal 3-credit
slot — this program's map has **no General Elective line item at all**.
Its own footnote 3 explains the total works out because "the fourth
credit will be satisfied by the extra credit from PHY 110," so Common
Core's declared `required_credits` was set to 13 (the literal sum of its
four courses, including PHY 110's real 4 credits) to make the group's
declared value match its actual content directly, rather than leaving a
1-credit gap unaccounted for. This mirrors how `eco_aa_courses.csv`'s
"Program Requirements" group absorbs its own MAT-course excess directly
into its declared total, rather than the "Common Core stays nominal,
General Elective absorbs it" pattern used elsewhere. Verified by
reconciling every course and credit value on both official maps to
exactly 60.

Flexible Core has only 3 slots (9 credits) — Creative Expression (first
and second course) and U.S. Experience in Its Diversity — not the full
6-slot, 18-credit pattern seen in Sociology, Criminal Justice, or Digital
Marketing. Individual and Society, Scientific World, and World Cultures
are entirely absent from this map, replaced by specific required program
courses, the same pattern already documented for Video Arts and
Technology.

## Choices and alternatives

- **MAT 161 (Common Core, Mathematical and Quantitative Reasoning).** No
  alternate shown. The five-semester map uses MAT 161.5 instead (a
  non-STEM-variant placement course) — not added as an additional row,
  matching the established ENG 100.5/MAT 161.5 handling in every other
  major so far.
- **PHY 110 / PHY 400 (Common Core, Life and Physical Sciences).**
  Footnote: "PHY 400 is an alternative option." Modeled with
  `alternatives=PHY 400`; PHY 400 is not part of this curriculum's own
  course list, so the validator is expected to warn about an external
  reference.
- **SPE 100 / SPE 102 (Flexible Core, Creative Expression, first
  course).** Modeled as two reciprocal rows, matching the pattern
  established for `soc_aa_courses.csv`, `nur_aas_courses.csv`,
  `vat_as_courses.csv`, and `dmk_as_courses.csv`.
- **Creative Expression, second course.** Footnote: "Select any Creative
  Expression Pathways course except SPE 100, SPE 102 or MES 153." A
  **three-way** exclusion, unlike every prior major's two-way
  SPE 100/SPE 102 exclusion — MES 153 (Script Writing) is itself a
  Pathways-eligible Creative Expression course, and it's already
  separately required as a fixed Program Requirement here, so this
  footnote prevents double-dipping. Modeled with a new derived group,
  `AMG_AS_CREATIVE` (base `FC_CREATIVE`,
  `exclude_course_codes=SPE 100|SPE 102|MES 153`).
- **U.S. Experience in Its Diversity (Flexible Core).** Footnote: "Please
  consult with an academic or faculty advisor" — advisory, not
  restrictive. Left as the standard, unrestricted `FC_US_EXPERIENCE` pool.
- **ART 269 / ART 176 (Program Requirements, Life Drawing Studio I).**
  Footnote: "ART 176 is an alternate option." ART 176's title and credits
  could not be verified (Art & Design department page returned repeated
  HTTP 503 errors), so it was **not added as a row** rather than guessed
  at. **Flagged for maintainer review.**
- **ANI 402 / ANI 360.** Footnote: "ANI 360 is an alternative option."
  Modeled as two reciprocal rows. Unlike SPE 100/SPE 102 or MEA 371/MEA
  201 (which share the same effective eligibility), ANI 360 has its own,
  genuinely different prerequisite (see "Prerequisite review" below) —
  the `alternatives` mechanism still applies correctly, since each
  course's own prerequisite gate is checked independently of the
  alternative relationship.
- **MEA 371 / MEA 201 (Media Arts and Technology Internship).**
  Footnote: "MEA 201 is an alternative option." Modeled as two reciprocal
  rows, matching the identical pattern already used in
  `vat_as_courses.csv`.
- **MMP 250 "ANI Elective" substitution (footnote 3).** Footnote: "MMP
  250 can be taken to satisfy the ANI elective requirement as it is the
  prerequisite course to ANI 301. Alternate ANI electives are MMA 215,
  MMA 225, MMA 235, MMP 210, ANI 301, COM 240, COM 245, MEA 211, MEA 371,
  MEA 300, HED 250 or BUS 200." **Not modeled as a choice group or as
  `alternatives` on MMP 250.** Two of the twelve listed alternates —
  ANI 301 and MEA 371 — are already separately, independently required
  elsewhere on this same map. `alternativeComponents()` in
  `frontend/db_progress_graph.html` graph-walks `alternatives` links to
  group interchangeable courses into one shared credit-counted slot;
  linking MMP 250 to ANI 301 and MEA 371 as alternatives would merge
  three genuinely distinct program requirements into one, which would be
  wrong — a student needs all three, not any one of the group. MMP 250 is
  modeled as the literal, fixed course shown on the map; the official
  substitution flexibility (choosing a different course than MMP 250
  itself) is documented here but not enforced. **Flagged for maintainer
  review.**

## Prerequisite review

- **MMP 250 (Digital Film Fundamentals).** Official prerequisite:
  "Prerequisite: MMP 100." Encoded as `MMP 100`.
- **ANI 260 (Introduction to 2D Animation) / ANI 401 (Introduction to 3D
  Animation).** Official course-listing prerequisite for both: "MMP 100
  or MMA 100." Encoded as `MMP 100 or MMA 100` for both.
  **Discrepancy with this program's own map:** footnote 2 states "MMP 100
  *and* MMA 100 must be passed in order to take ANI 260 and ANI 401" — an
  AND relationship, conflicting with the catalog's OR. The catalog's OR
  was used, both because it is the more specific, registrar-facing source
  and because ANI 401 already has this exact `MMP 100 or MMA 100`
  encoding in `vat_as_courses.csv` (ANI 401 is shared between both
  majors) — encoding it differently here would make the same course's
  prerequisite depend on which program's file happens to reference it,
  which is inconsistent with how course prerequisites actually work.
  **Flagged for maintainer review.**
- **ANI 301.** Official title (course-listings page, verified twice):
  "Introduction to Motion Graphics and Visual Effects." Official
  prerequisite: "VAT 161 or VAT 171 or MMA 100 or MMP 100." Both exactly
  match the ANI 301 row already present in `vat_as_courses.csv` (ANI 301
  is shared between this program and Video Arts and Technology).
  **This program's own degree map mislabels the course**, printing "ANI
  301 Introduction to Video Graphics" — but "Introduction to Video
  Graphics" is actually **VAT 301/MMP 301's** official title, a different
  course entirely (confirmed during the Video Arts and Technology
  submission). The course-listings page's title and prerequisite were
  used instead of the map's incorrect wording, per lesson 2 (match the
  official course listing, not the map). **Flagged for maintainer
  review** as an apparent copy-paste error in the official degree map.
  VAT 161 and VAT 171 are not part of this curriculum's own course list,
  so the validator is expected to warn about both as external references.
- **ANI 402 (3D Animation Projects).** Official course-listing
  prerequisite (quoted exactly): "Prerequisite: ANI 401 / Corequisite:
  ENG 101 and MAT 100-level or higher." Encoded as `ANI 401|MMP 250` —
  **see below for why MMP 250 was added despite not appearing in the
  catalog's prerequisite line.**
  This program's own map footnote 6 states a stricter, three-part
  requirement: "ANI 401, MMP 250 and a college-level MAT course must be
  passed in order to take ANI 402." Given the map's footnote 2 was
  *already* found to overstate an AND-relationship that the catalog shows
  as OR (see ANI 260/ANI 401 above), there is a real, demonstrated risk
  that this specific degree map's footnotes are not perfectly reliable —
  but MMP 250 is a specific, real, already-required course in this same
  curriculum (unlike the vague "college-level MAT course" condition,
  which is left unencoded), and the map's own sequencing places MMP 250
  in Semester 2, well before ANI 402 in Semester 4, consistent with it
  being a genuine prerequisite. `MMP 250` was therefore included, while
  the catalog's ENG 101/MAT-100-level corequisites (same-semester, not a
  strict "before" prerequisite, and the MAT-level portion isn't a
  specific course code) were left undocumented as unenforced. **Flagged
  for maintainer review** — this is a judgment call between two
  conflicting official sources, not a fully resolved discrepancy.
- **ANI 360 (2D Animation Projects).** Official prerequisite: "MMP 260 or
  ANI 260." Encoded as `MMP 260 or ANI 260`. MMP 260 is not part of this
  curriculum's own course list, so the validator is expected to warn
  about it as an external reference.
- **MEA 201.** Official prerequisite: "ANI 401 or two 200-level-or-higher
  MMA/MMP courses" — the "any two of a pool" condition has no primitive
  in the current prerequisite grammar; left blank, matching the identical
  limitation already documented for VAT_AS.
- **MMP 100 (Introduction to Multimedia).** No prerequisite listed.
  Footnote 1: "MMP 100 is the pre-requisite course to all MMP courses.
  ANI students should take this course as soon as possible, ideally in
  their first semester." A general recommendation, not itself a
  prerequisite condition on MMP 100.
- **ENG 100.5 / MAT 161.5 (five-semester map only).** Placement-based
  alternates for ENG 101 and MAT 161 respectively, identical pattern to
  every other major. Not added as additional rows.
- **Writing Intensive requirement.** Both maps: "A Writing Intensive
  course is needed in order to graduate." Graduation-wide flag, not a
  course row; recorded here and in the degree-map JSON `sequence_notes`.

## Ambiguities requiring maintainer review

1. The two official degree-map dropbox links are no longer linked from
   the live Animation and Motion Graphics program page (which now serves
   a 2026-2027 map instead) and were recovered via the Wayback Machine.
2. This program's own degree map appears to mislabel ANI 301's title as
   "Introduction to Video Graphics" (actually VAT 301/MMP 301's title);
   the verified official course-listings title was used instead.
3. This program's own degree map footnote 2 states an AND relationship
   for ANI 260/ANI 401's prerequisite (MMP 100 and MMA 100) that
   conflicts with the official course-listings page's OR; the catalog's
   OR was used, for consistency with VAT_AS's existing ANI 401 encoding.
4. ANI 402's prerequisite is a genuine three-way conflict between the
   degree map's footnote (ANI 401 + MMP 250 + a vague "college-level MAT
   course") and the course-listings page (ANI 401 only, with ENG 101 and
   a MAT-level course as corequisites, not MMP 250 at all). MMP 250 was
   included based on the map; the corequisites and vague MAT-level
   condition were not encoded.
5. The "ANI Elective" substitution flexibility (MMP 250 interchangeable
   with 12 other named courses) is documented but not modeled, since two
   of the alternates are already separately required elsewhere on this
   map — see "Choices and alternatives" above.
6. ART 176's title and credits could not be verified due to repeated
   HTTP 503 errors on the Art & Design department's course-listings page.
7. `docs/programs.csv` listed AMG_AS's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/amg_as_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/amg_as_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 4 warning(s).`
- Warnings explained (all 4):
  1. `alternatives` references `PHY 400` — external, not part of AMG_AS;
     see "Choices and alternatives" above.
  2-3. `prerequisites` references `VAT 161` and `VAT 171` (ANI 301) —
     external to this curriculum file; both are part of
     `vat_as_courses.csv`, and will resolve to "listed in another current
     curriculum file" once that branch is merged.
  4. `prerequisites` references `MMP 260` (ANI 360) — external, not part
     of AMG_AS; see "Prerequisite review" above.
- Local seed completed: `python seed_database.py` — `AMG_AS` seeded
  cleanly with 22 courses; no stale placeholder needed cleanup since
  `programs.csv` was corrected before the first seed on this branch.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: ANI 260 and ANI 401 are both `locked`.
  2. After completing MMP 100 alone (no MMA 100): both ANI 260 and ANI 401
     become `available` -- confirms the catalog's OR relationship is
     genuinely enforced, not the map footnote's stricter AND.
  3. ANI 402 and ANI 360 render as an explicit "Alternative requirement -
     Choose one" widget (same pattern as SPE 100/SPE 102 and MEA 371/MEA
     201), each showing its own distinct prerequisite text directly in the
     UI: "ANI 402 ... Prereqs: ANI 401, MMP 250" and "ANI 360 ... Prereqs:
     ANI 260 or MMP 260" -- confirms both the AND-prerequisite for ANI 402
     and ANI 360's separate OR-prerequisite took effect correctly.
  All group cards render with correct titles (including the corrected
  "Introduction to Motion Graphics and Visual Effects" for ANI 301, not
  the map's incorrect "Introduction to Video Graphics"); ART 176 does not
  appear anywhere on the page. No console errors.
