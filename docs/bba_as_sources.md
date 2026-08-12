# BMCC Business Administration A.S. curriculum sources

## Program identity

- Institution: Borough of Manhattan Community College (BMCC)
- Department: Business Management (`BUS`)
- Program code: `BBA_AS`
- Degree: A.S.
- Catalog year: `2025-2026`, taken from the supplied official degree map
- Published total: 60 credits

## Official sources

- Program requirements: https://www.bmcc.cuny.edu/academics/departments/business-management/business-administration/
- Business Management courses: https://www.bmcc.cuny.edu/academics/departments/business-management/course-listings/
- Accounting courses: https://www.bmcc.cuny.edu/academics/departments/accounting/course-listings/
- Supplied official map: `degree_maps/bmcc_business_administration_2_year_2025_2026.pdf`
- Sources checked: 2026-08-13

The live requirements page still labels its curriculum as effective for
2023-2024. The supplied BMCC map is explicitly branded 2025-2026 and is the
current artifact used for this implementation. DegreeWorks remains
authoritative for a student's entry catalog.

## Credit reconciliation

| Requirement group | Credits |
| --- | ---: |
| Required Common Core | 12 |
| Flexible Core | 18 |
| Curriculum Requirements | 26 |
| Business Elective | 3 |
| Liberal Arts Elective / STEM excess | 1 |
| **Total** | **60** |

All eight named curriculum courses are classified as `program_required`.
MAT 301 and BUS 320 are reciprocal alternatives inside the same requirement;
selecting either contributes four credits once. The six published Business
Elective choices remain `program_elective`, as does the one-credit Liberal
Arts/STEM-excess requirement.

## Common and Flexible Core footnotes

- MAT 206 is recommended, not mandated. `BBA_AS_MATH_QUANT` retains the full
  canonical Mathematical and Quantitative Reasoning pool and displays that
  recommendation in the selector.
- Life and Physical Sciences and Scientific World may be satisfied with STEM
  variants. Their derived groups retain the canonical pools and add the
  program-specific advising note.
- The second Creative Expression course excludes SPE 100 and SPE 102 because
  one speech course is separately required.
- The published cap of no more than two Flexible Core courses in one
  discipline spans several independent choice groups. The current rule engine
  cannot enforce a subject-count cap across groups, so it is documented but
  not silently approximated.
- The one-credit Liberal Arts requirement may be satisfied by excess Common
  Core STEM credit. Automatic cross-group surplus-credit application is not
  currently supported, so the Liberal Arts selector remains available and its
  title explains the permitted STEM-excess route.

## Prerequisite interpretations

- BUS 150: ENG 101, ENG 201, and BUS 104 are enforced.
- MAT 209 and MAT 301: MAT 206 or MAT 206.5 is enforced.
- BUS 320: MAT 209 is enforced.
- CIS 200 officially requires any ACC or BUS course plus either the CIS 100
  course or a competency test. ACC 122 or BUS 104 captures the course-family
  portion using courses already required by this program. The non-course
  competency test cannot be represented and remains an advising check.
- BUS 201 requires BUS 104 and ECO 201. ECO 201 can be selected through the
  U.S. Experience Pathways selector.
- SBE 100 lists BUS 104 as a co-requisite for business majors; co-requisites
  are not modeled as completed-course prerequisites.

## Degree-map sequence

The registered map follows the official semester targets of 13, 16, 16, and
15 credits. ECO 201 and ECO 202 are shown choices for U.S. Experience and
Individual and Society on the map, but the published curriculum does not
narrow either Pathways category; students retain the complete canonical pools.
A Writing Intensive course is required for graduation.
