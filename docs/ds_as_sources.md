# Curriculum Source Notes: Data Science (A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Mathematics
- Program code: `DS_AS` (project identifier; BMCC's degree map labels the plan `DSM`)
- Program name: Data Science
- Degree type: A.S.
- Effective catalog year: 2024-2025
- Published total credits: 60
- Date accessed: 2026-08-05

## Official sources

1. Program requirements
   - Title: Data Science (A.S.)
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/math/data-science/
   - Effective year shown: 2024-2025 or later

2. Program map
   - Title: BMCC Degree Maps 2024-2025, Data Science A.S. (pages 48-49)
   - Direct URL: https://www.dropbox.com/scl/fi/yc2fov656co4sh38697ly/Degree-Maps-2024-2025.pdf?raw=1&rlkey=fa9r8ofnes11m289ysmrrkgyv&st=kbx6k55y
   - Effective year shown: 2024-2025

3. Course listings
   - Mathematics: https://www.bmcc.cuny.edu/academics/departments/math/course-listings/
   - Computer Information Systems: https://www.bmcc.cuny.edu/academics/departments/cis/course-listings/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 12 | Required Common Core |
| Flexible Core | 18 | Flexible Core |
| Program Requirements | 19 | Curriculum Requirements: MAT 200, 301, 302, 409, and 415 |
| Program Electives | 9 | Curriculum Requirements: select 9 credits |
| General Electives | 2 | Curriculum Requirements: General Electives |
| **Published program total** | **60** | Total Program Requirements |

The two-year degree map totals 61 course credits because it uses four-credit STEM
variants in areas that require three credits. The program page explains that general
elective credits may be satisfied by those excess STEM credits. The CSV keeps the
published 60-credit requirement total.

## Choices and alternatives

- Program electives: select 9 credits from MAT 420, CSC 203, CSC 211, CIS 395,
  and CIS 490. The CSV lists every approved option in one 9-credit group.
- SPE 100 is the mapped Creative Expression course. The degree map identifies
  SPE 102 as the option for eligible non-native English speakers, represented as an
  alternative to SPE 100.
- Placeholder rows represent Pathways areas where the source does not prescribe a
  single course: Life and Physical Sciences, Individual and Society, U.S. Experience,
  and World Cultures.
- `DS-GENERAL-ELECTIVE` preserves the published 2-credit group. The application
  currently cannot apply excess credits from MAT 206.5 and the Scientific World STEM
  courses automatically, so this placeholder must not be interpreted as an extra
  course beyond the official degree total.

## Prerequisite review

- MAT 409 requires MAT 301 and has MAT 302 as a co-requisite. The CSV records MAT
  301 only because the current relationship model does not represent co-requisites.
- MAT 420 has MAT 415 as a co-requisite. It is omitted from the prerequisite field
  for the same reason.
- CSC 111 requires MAT 206 plus CSC 101 or departmental approval in the general
  course listing, while the Data Science degree map directs students to obtain CIS
  department permission. The CSV does not invent a course-only replacement for that
  permission rule.
- CSC 203 permits multiple prerequisite combinations or departmental approval. For
  this curriculum, the CSV represents the in-program combination of CSC 103 and
  either MAT 200 or MAT 206.5.
- The 2024-2025 degree map assigns 3 credits to CSC 103 and 4 to CSC 111. The current
  online course-listing page displays the reverse. The CSV follows the catalog-year
  degree map, which also preserves the existing shared course values used by the
  Computer Science curriculum.

## Ambiguities requiring maintainer review

- Confirm whether later catalog years changed the CSC 103/CSC 111 credit allocation.
- A future data-model revision should represent co-requisites, permission rules, and
  excess STEM-credit application directly.

## Validator and local testing

- Validator command: `python3 scripts/validate_curriculum_csv.py docs/ds_as_courses.csv`
- Validator result: completed; see implementation test output
- Warnings explained: listed credits exceed required credits in choice/STEM groups;
  all are reconciled above
- Local seed completed: completed against an isolated temporary SQLite database
- Program Selector checked: verified through `/api/programs`
- Academic Progress checked: verified through program requirements/graph APIs
- Prerequisite unlocking checked: verified in seeded relationship records and API data
- Semester planner checked: API payload smoke-tested; complex co-requisites remain a
  documented model limitation
