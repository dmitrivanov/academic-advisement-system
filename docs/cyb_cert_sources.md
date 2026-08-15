# Curriculum Source Notes: Cybersecurity Certificate (CERT)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Computer Information Systems (CIS)
- Program code: CYB_CERT
- Program name: Cybersecurity Certificate
- Degree type: CERT
- Effective catalog year: 2025-2026
- Published total credits: 30
- Date accessed: 2026-08-13

Note: `docs/programs.csv` previously listed CYB_CERT's `catalog_year` as
`2026`, not `2025-2026` — the same recurring mismatch already found and
corrected for every prior BMCC major added this way. Fixed before the
first seed on this branch, so no stale empty program placeholder was
ever created.

## Official sources

1. Program map (two-year)
   - Direct URL: https://www.dropbox.com/scl/fi/1f91fs6bmyujjjrom43oc/cybcert2yr.pdf?rlkey=uzna3c3m7wets6w3ohzxbmsjx&e=1&st=00jnmqd2&raw=1
   - Effective year shown: 2025-2026
   - Retained at: `docs/degree_maps/bmcc_cybersecurity_certificate_2_year_2025_2026.pdf`
   - Unlike Nursing and VAT, this link was still live and current on the
     program page at the time of writing — no Wayback Machine recovery was
     needed. Downloaded and read directly; confirmed identical to the
     2025-2026 map image supplied for this submission (including catching
     an OCR-style misread in the supplied image, which showed footnote 3
     as "CIS 111" — the actual PDF text reads "CSC 111", the real course
     code).
   - Only one map variant is published for this certificate (no alternate
     five-semester map, unlike the full AA/AS/AAS majors).

2. Program requirements page
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/cis/cybersecurity-certificate/
   - Section header: "Curriculum Requirements", 30 credits — matches the
     degree map exactly, course for course.

3. Course listings
   - Computer Information Systems (all 10 courses): https://www.bmcc.cuny.edu/academics/departments/cis/course-listings/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Curriculum Requirements | 30 | Program page "Curriculum Requirements"; degree map "TOTAL: 30 CREDITS" |

This is a fully-prescribed, 10-course certificate with **no elective
choice groups and no general-education requirements at all** — every
course is individually required. `choice_group_code` is blank on every
row; no `program_choice_group_adjustments.csv` rows were needed.

## Prerequisite review

- **CIS 165 (Introduction to Operating Systems).** Footnote: "CSC 101
  must be passed in order to take CIS 165." Course-listing confirms:
  "Prerequisite: CSC 101 or departmental approval." Encoded as `CSC 101`;
  the departmental-approval alternate is not course-based and not
  translated.
- **CIS 345 / CIS 359 / CIS 440 / CIS 316 / CIS 362.** Footnote 3 (same
  wording across all five): "CIS 165 or CSC 110 or CSC 111 must be passed
  or Departmental approval required." Encoded identically as `CIS 165 or
  CSC 110 or CSC 111` for all five — confirmed course-by-course against
  the official course-listings page, which independently states the same
  three-course OR prerequisite for each (word order varies slightly per
  course, but the same three codes every time).
  **Discrepancy noted, not corrected here:** the existing Computer
  Information Systems A.A.S. curriculum (`docs/cis_courses.csv`) encodes
  this same prerequisite for CIS 345 and CIS 440 only, and leaves CIS 359,
  CIS 362, and CIS 316 without any prerequisite at all — even though the
  official course-listings page states the identical prerequisite for all
  five, independent of which program is requiring them (prerequisites are
  a property of the course, not the program). This appears to be stale or
  incomplete data in that other file. Out of scope to fix as part of this
  submission (a different program's curriculum file); **flagged for
  maintainer review.**
  CSC 110 and CSC 111 are not part of this certificate's own course list
  — they exist only in `cis_courses.csv` (the CIS A.A.S. curriculum), so
  the validator is expected to warn about external references for both,
  on all five courses (10 warnings total).
- **CIS 455 (Network Security).** Footnote: "CIS 345 must be passed... in
  order to take CIS 455." Course-listing confirms: "Prerequisite: CIS
  345." Encoded as `CIS 345`.
- **CIS 459 (Ethical Hacking and System Defense).** Footnote: "CIS 345 and
  CIS 440 must be passed... in order to take CIS 459." Course-listing
  confirms: "Prerequisites: CIS 440 and CIS 345." Encoded as `CIS
  345|CIS 440`.
  **Title discrepancy noted, not corrected here:** `cis_courses.csv`
  currently lists CIS 459 under a different title, "Security Penetration
  Testing," while both this degree map and the official course-listings
  page (verified) agree on "Ethical Hacking and System Defense." This
  submission uses the verified, current official title. **Flagged for
  maintainer review** in case CIS 459 was renamed and the other file
  hasn't been updated to match.
- **"Or Departmental approval" alternates.** Every footnote in this
  program includes a "...or Departmental approval required" alternate
  path. None are course-based, so none are translated into
  `prerequisites`, matching the established practice for similar
  non-course alternates elsewhere in this repo (e.g. "permission of
  department" cases in Sociology and Video Arts and Technology).

## Ambiguities requiring maintainer review

1. `docs/cis_courses.csv` (Computer Information Systems A.A.S.) does not
   apply the same CIS 165/CSC 110/CSC 111 prerequisite to CIS 359, CIS
   362, and CIS 316 that this certificate's own official sources confirm
   for all three courses. Not corrected here (different program's file).
2. `docs/cis_courses.csv` lists CIS 459 under an older title ("Security
   Penetration Testing") that no longer matches the current official
   course-listings page ("Ethical Hacking and System Defense"). Not
   corrected here.
3. `docs/programs.csv` listed CYB_CERT's catalog year as `2026`; corrected
   to `2025-2026` (see "Program identity").

## Validator and local testing

- Validator command: `python scripts/validate_curriculum_csv.py docs/cyb_cert_courses.csv`
- Validator command (strict): `python scripts/validate_curriculum_csv.py --strict docs/cyb_cert_courses.csv`
- Validator result: `Validated 1 file(s): 0 error(s), 10 warning(s).`
- Warnings explained (all 10): `prerequisites` references `CSC 110` and
  `CSC 111` on each of CIS 345, CIS 359, CIS 440, CIS 316, and CIS 362 (2
  warnings × 5 courses) — both external to this certificate, but present
  in `cis_courses.csv`; see "Prerequisite review" above.
- Local seed completed: `python seed_database.py` — `CYB_CERT` seeded
  cleanly with 10 courses; no stale placeholder needed cleanup since
  `programs.csv` was corrected before the first seed on this branch.
- Real-behavior browser verification (Playwright, logged in as `admin`,
  program selector -> onboarding -> `/db-progress`):
  1. Baseline: CIS 165 and CIS 459 are both `locked`.
  2. After CSC 101: CIS 165 becomes `available`.
  3. After CIS 165: CIS 345 becomes `available`.
  4. After CIS 345 only: CIS 455 becomes `available`, but CIS 459 stays
     `locked` (still needs CIS 440) -- confirms the two-course AND
     prerequisite is genuinely enforced, not just documented.
  5. After CIS 345 + CIS 440: CIS 459 becomes `available`.
  All 10 courses render under "Program Requirements" with correct titles
  (including "Ethical Hacking and System Defense" for CIS 459, not the
  stale "Security Penetration Testing"); the Program Electives, Common
  Core, and Flexible Core columns correctly show no courses, matching this
  certificate's fully-prescribed structure. No console errors.
