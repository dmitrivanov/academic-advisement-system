# Academic Advisement System: Implemented Features

The Academic Advisement System is a research prototype for curriculum-aware student advising. It supplements—but does not replace—DegreeWorks, the official college catalog, academic departments, or professional academic advisors.

## Student access and authentication

- Secure session-based login.
- Two authorization roles:
  - `admin`: student-facing and administrative access.
  - `tester`: student-facing access without administrative privileges.
- Administrator navigation is hidden from tester accounts.
- Administrator pages and API operations are protected on the server.
- Account credentials can be configured separately for local and Render deployments.

## Program selection and onboarding

- Campus and academic-program selection across supported CUNY colleges.
- Duplicate-program filtering so only one current, populated version of a program appears.
- Support for programs with separate concentrations represented as clear program choices.
- New-student workflow for students without completed college coursework.
- Links to official program pages and stored degree-map PDFs where available.

## Completed-course selection

- Requirements organized into:
  - Required Common Core
  - Flexible Core
  - Program requirements
  - Program electives
- Searchable course-choice dialogs.
- Course sequences and major-specific requirement explanations.
- Machine-enforced prerequisites and prerequisite groups.
- Visually grouped `OR` alternatives and mutually exclusive choices.
- Elective pools with course, credit, level, and selection limits.
- Disabled courses cannot be selected when prerequisites or requirement rules are unmet.
- A completed course is synchronized across every applicable requirement location.
- Requirement-satisfied indicators and progress totals.
- Writing Intensive confirmation.
- Program-specific footnotes and Common/Flexible Core adjustments.

## Degree progress and planning

- Interactive degree-progress view.
- Completed, remaining, unavailable, and not-needed course states.
- Manual semester-by-semester planning.
- AI-assisted plan generation when a Gemini API key is configured.
- Preferred credit-load settings.
- Prerequisite-aware course sequencing.
- Explicit elective placeholders when the student must still choose a course.
- Downloadable PDF degree plan for saving or reviewing with an advisor.

## Major-change and transfer analysis

- What-if major-change analysis using the student's completed coursework.
- Transfer-program comparison.
- Campus-aware course identity using institution plus course code.
- Direct and combination course-equivalency rules.
- Administrative tools for creating and validating equivalencies.
- Clear separation between confirmed matches and courses requiring review.
- AI-generated summaries when Gemini is configured.

## AI advisor

- Student-facing advising drawer using the current page and program context.
- Configurable Gemini model, system prompt, display settings, and logging.
- Token-usage metrics and advisor interaction logs.
- Guardrails instructing the advisor not to invent requirements or policies.
- Manual advising functionality remains available without an AI key.

## Administrator dashboard

- Management interfaces for:
  - Institutions
  - Departments
  - Programs
  - Courses
  - Requirement groups
  - Course equivalencies
  - Advisor logs
- AI-advisor configuration.
- Protected access available only to administrator accounts.

## Major Constructor

- Saved curriculum drafts.
- Program metadata and concentration setup.
- List and visual board editing modes.
- Drag-and-drop curriculum bins.
- Campus-filtered course library.
- Selected-department courses prioritized in search results.
- Credit counters for requirement bins.
- Rule editors for prerequisites, alternatives, elective pools, sequences, and credit splits.
- Common and Flexible Core groups with program-specific adjustments.
- Student-view preview before publication.
- Draft validation and approval workflow.
- Version history, publishing, and rollback support.
- Detailed administrator guide.

## Curriculum data and quality controls

- CSV-backed curriculum, Pathways, program-adjustment, and equivalency data.
- Campus plus course code used to distinguish courses across institutions.
- Official-source documentation for many implemented programs.
- Automated checks for:
  - Duplicate programs in student selectors
  - Missing or empty choice groups
  - Invalid curriculum rules
  - Broken alternatives and elective pools
  - Regressions in established majors
- SQLite support for local development.
- PostgreSQL support for Render deployment.
- FastAPI backend serving both the API and frontend.

## Scope and limitations

This application is an advising prototype, not an official degree audit. DegreeWorks, official catalogs, academic departments, and professional advisors remain authoritative for graduation requirements, substitutions, waivers, transfer decisions, catalog-year exceptions, and individual student records.
