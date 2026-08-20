# CUNY Beyond Phase 9 - Reviewed Career Discovery and Catalog Expansion

## Outcome

Phase 9 makes career matching easier to discover and substantially broadens the reviewed BMCC coverage. A student no longer needs to guess an exact accepted phrase: the career step now includes a searchable browser backed by the published career API.

## Student-Side Functionality

- Open **Browse all reviewed careers** on the career-goal step.
- Filter by a job word such as `nursing`, `accounting`, `counseling`, `technology`, or `planning`.
- See how many reviewed BMCC program matches support each career.
- Choose a career with a keyboard or pointer and continue through the existing explainable matcher.
- Type a reviewed alias such as `bookkeeper`, `case worker`, `law enforcement`, `city planner`, or `healthcare administrator` and receive the correct canonical career match.
- Receive clear education or credential cautions for careers such as CPA, counseling, forensic psychology, and licensed legal practice.

## Catalog Expansion

The catalog grew from 25 to 46 active careers and from 27 to 50 active career-program relationships. Newly represented program families are:

- Accounting A.A.S.
- Human Services A.S.
- Psychology General and STEM concentrations
- Criminal Justice A.A.
- Public and Nonprofit Administration A.S.
- Urban Studies A.A.
- Political Science A.A.
- Gerontology A.S.

The previous Computer Science, Data Science, and Nursing matches remain intact.

## New Career Examples

Accounting Clerk; Accountant or Auditor; Case Manager; Community Organizer; Mental Health Counselor; Substance Abuse Counselor; Patient Navigator; Market Research Analyst; Psychology Research Assistant; Forensic Psychologist; Police Officer; Legal Advocate; Forensic Analyst; Public Administrator; Nonprofit Program Coordinator; Urban Planner; Political Analyst; Fundraising Specialist; Aging Services Coordinator; Geriatric Care Manager; and Health Services Administrator.

## Evidence Rules

Every active career has at least one active program mapping. Every new mapping points to a populated curriculum and an official BMCC or BMCC OpenLab source. `strong` evidence is used when BMCC explicitly names the career or employment area. `related` evidence is used when the associate degree is a starting point and further education, licensure, certification, or transfer is normally part of the path.

The result is exploration guidance, not a guarantee of employment, licensure, transfer admission, or salary.

## Technical Changes

- Expanded the two governed career CSV datasets.
- Added `program_count` to the public career catalog response.
- Added responsive and accessible career browsing to the public intake.
- Replaced the old three-example no-match message with a browser-oriented recovery path.
- Added tests for catalog size, program-family coverage, aliases, source domains, credential disclosures, and UI accessibility.

## Official Sources Used

- BMCC Accounting: https://www.bmcc.cuny.edu/academics/departments/accounting/
- BMCC Human Services: https://www.bmcc.cuny.edu/academics/departments/social-sciences/human-services/
- BMCC Psychology: https://www.bmcc.cuny.edu/academics/departments/social-sciences/psychology/
- BMCC Criminal Justice: https://www.bmcc.cuny.edu/academics/departments/criminal-justice/
- BMCC Public and Nonprofit Administration: https://www.bmcc.cuny.edu/academics/departments/business-management/public-and-nonprofit-administration/
- BMCC Social Sciences and Human Services: https://www.bmcc.cuny.edu/academics/departments/social-sciences/
