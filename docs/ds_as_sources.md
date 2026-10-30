# Curriculum Source Notes: Data Science (A.S.)

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Mathematics
- Program code: `DS_AS` (project identifier; BMCC's degree map labels the plan `DSM`)
- Program name: Data Science
- Degree type: A.S.
- Effective catalog year: 2026-2027
- Published total credits: 61
- Degree map supplied and reviewed: 2026-10-30

## Official sources

1. Program requirements
   - Title: Data Science (A.S.)
   - Direct URL: https://www.bmcc.cuny.edu/academics/departments/math/data-science/
   - Effective year shown: 2024-2025 or later

2. Program map
   - Title: BMCC Data Science (DSM) 2026-2027 Degree Map
   - Source document: BMCC Data Science Degree Map 2026-2027.pdf supplied for the curriculum update
   - Effective year shown: 2026-2027

3. Course listings
   - Mathematics: https://www.bmcc.cuny.edu/academics/departments/math/course-listings/
   - Computer Information Systems: https://www.bmcc.cuny.edu/academics/departments/cis/course-listings/

## Credit reconciliation

| Requirement group | Required credits | Official source section |
| --- | ---: | --- |
| Required Common Core | 13 | Required Common Core |
| Flexible Core | 19 | Flexible Core |
| Program Requirements | 19 | Curriculum Requirements: MAT 200, 301, 302, 409, and 415 |
| Program Electives | 10 | CIS 395, CSC 211, and CIS 490 on the map; MAT 420 and CSC 203 are alternatives |
| **Published program total** | **61** | Degree-map total |

The canonical curriculum now follows the supplied 2026-2027 map's 61-credit total
and four-semester sequence.

## Choices and alternatives

- Program electives: 10 credits. The map places CIS 395, CSC 211, and CIS 490;
  MAT 420 and CSC 203 are the approved alternatives identified in the footnote.
- SPE 100 is the mapped Creative Expression course. The degree map identifies
  SPE 102 as the option for eligible non-native English speakers, represented as an
  alternative to SPE 100.
- Placeholder rows represent Pathways areas where the source does not prescribe a
  single course: Life and Physical Sciences, Individual and Society, U.S. Experience,
  and World Cultures.

## Prerequisite review

- MAT 409 requires MAT 301 and has MAT 302 as a co-requisite. The CSV records MAT
  301 only because the current relationship model does not represent co-requisites.
- MAT 420 has MAT 415 as a co-requisite. It is omitted from the prerequisite field
  for the same reason.
- The Data Science map states that CIS department permission is required for CSC
  111. The CSV does not invent a course-only prerequisite for that permission rule.
- CSC 203 permits multiple prerequisite combinations or departmental approval. For
  this curriculum, the CSV represents the in-program combination of CSC 103 and
  either MAT 200 or MAT 206.
- The 2026-2027 degree map assigns 3 credits to CSC 103, 4 credits to CSC 111, and
  4 credits to CSC 211. The CSV follows those mapped values.

## Ambiguities requiring maintainer review

- A future data-model revision should represent co-requisites, permission rules, and
  excess STEM-credit application directly.

## Validator and local testing

- Validator command: `python3 scripts/validate_curriculum_csv.py docs/ds_as_courses.csv`
- Validator result: completed; see implementation test output
- Warnings explained: the five approved program-elective options total 17 credits
  for a 10-credit choice requirement, and the official map totals 61 credits rather
  than the validator's conventional 60-credit associate-degree target
- Curriculum and graph regression tests: completed locally
- Complex co-requisites remain a documented model limitation
