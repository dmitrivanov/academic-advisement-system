# CUNY Beyond Implementation Roadmap

**Career-first pre-advisement, major exploration, prior-learning screening, transfer planning, and schedule discovery**

Version 1.0 - August 2026

## 1. Executive summary

CUNY Beyond should be implemented as a second public entry point into the existing Academic Advisement System. It will reuse the current curriculum, course, prerequisite, degree-map, transfer-equivalency, comparison, and PDF-planning services while presenting a new career-first experience.

The service has two primary pathways:

1. **Incoming and prospective students:** begin with a career or life goal, identify relevant skills, discover matching BMCC programs, review transfer possibilities, screen for possible Credit for Prior Learning (CPL), inspect the official degree map, and prepare a referral to BMCC advising.
2. **Current students:** begin with their present major and completed courses, explore a proposed major change, see how coursework applies, review a new degree plan and transfer options, find the official major-change process, and prepare for a human-advisor meeting.

The first deployable version should not create a separate application or database. It should add a public `/cuny-beyond` module to the existing FastAPI deployment. The current login-protected advisement application remains available, while CUNY Beyond becomes a no-login public front door with limited, privacy-conscious session storage.

For schedules, CUNY Global Search should be treated as the authoritative class-discovery destination. It supports institution, term, subject, time, modality, and course-attribute filters. Registration still occurs in CUNYfirst, and schedule availability remains subject to change and advisor confirmation. The initial implementation should generate a guided handoff to Global Search rather than scrape or copy live section data without an approved CUNY interface.

## 2. Product goals

### 2.1 Primary goals

- Help a student translate a career interest into one or more BMCC programs.
- Explain why each program matches the student's stated goal and skills.
- Connect each recommendation to the existing interactive degree map.
- Show relevant four-year transfer destinations and known course equivalencies.
- Identify possible CPL pathways without promising that credit will be awarded.
- Connect planned courses to the current or selected term in CUNY Global Search.
- Produce a concise, shareable pre-advisement summary.
- Hand the student to a human advisor with better-prepared information.
- Reuse the existing system instead of duplicating curriculum logic.

### 2.2 Non-goals for the first prototype

- Replacing academic, transfer, career, CPL, or financial-aid advisors.
- Guaranteeing admission, transfer, course availability, CPL, or graduation.
- Registering a student for classes.
- Submitting an official major change.
- Storing full student records or transcripts without authentication.
- Scraping Global Search on a recurring production schedule without authorization.
- Letting generative AI invent career-to-major or transfer relationships.

## 3. Users and pathways

### 3.1 Incoming and prospective students

Supported profiles:

- High-school student
- Incumbent worker or working adult
- Adult learner with some college
- Transfer student
- Returning student
- Adult who already holds a degree

Proposed journey:

```text
Audience selection
  -> career goal
  -> current employment and five skills
  -> prior education and CPL screening
  -> ranked BMCC program matches
  -> degree map and transfer options
  -> current-term schedule handoff
  -> downloadable summary and advising referral
```

### 3.2 Current students

Proposed journey:

```text
Current campus and major
  -> completed courses
  -> proposed major(s)
  -> reusable what-if degree audit
  -> remaining requirements and transfer options
  -> current-term schedule handoff
  -> official major-change and advising next steps
```

### 3.3 Staff and administrators

Staff need a controlled editor for career mappings, skills, CPL guidance, transfer links, schedule-link settings, source URLs, review dates, and publishing status. This belongs in the existing admin dashboard and must use the existing administrator role.

## 4. Experience and navigation

Add a second public call to action on the main landing page:

- **Plan My Degree** - the current student-focused advisement experience
- **Explore Careers and Majors** - the new CUNY Beyond experience

Recommended routes:

```text
/cuny-beyond
/cuny-beyond/start
/cuny-beyond/career
/cuny-beyond/skills
/cuny-beyond/prior-learning
/cuny-beyond/results
/cuny-beyond/major-change
/cuny-beyond/schedule
/cuny-beyond/referral
/admin/cuny-beyond
```

The public pages should use the same navbar, visual language, responsive layout, accessibility standards, and footer as the existing system. They should not expose administrator controls or require an account.

## 5. Schedule integration with CUNY Global Search

### 5.1 Source of truth

CUNY Global Search is the schedule-discovery destination:

- https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController

It allows students to search across CUNY using institution, term, subject, time, online/in-person delivery, and course attributes. Students register through CUNYfirst. CUNY also instructs students to direct availability questions to an academic advisor.

### 5.2 Recommended integration levels

#### Level 1 - Guided Global Search handoff (prototype and first deployment)

The application should:

1. Ask the student to choose a term.
2. Show recommended or remaining course codes from the degree plan.
3. Let the student select one course at a time, or copy a checklist.
4. Open CUNY Global Search in a new tab.
5. Display exact instructions: select Borough of Manhattan CC, select the chosen term, select the subject, enter the catalog number, and apply preferred modality/time filters.
6. Preserve the student's planning page in the original tab.
7. Warn that class availability and registration eligibility can change.

This level is reliable even if Global Search does not publish stable deep-link parameters for a prefilled result.

#### Level 2 - Verified deep links or prefilled searches

During implementation, inspect whether Global Search exposes documented and stable request parameters for institution, term, subject, and catalog number. If it does:

- Generate a link from each recommended course card.
- Prefill BMCC, term, subject, and catalog number.
- Label the action **Find current sections in CUNY Global Search**.
- Add automated tests for URL encoding and term mapping.
- Fall back to the Level 1 guided handoff if parameters change or are unavailable.

Do not rely on undocumented browser state, cookies, hidden tokens, or fragile page markup.

#### Level 3 - Official section-data integration

Only pursue embedded section results after receiving an approved CUNY API, data feed, or written integration permission. Then add a schedule-provider adapter that can return:

- Institution and term
- Subject and catalog number
- Section number
- Meeting pattern and modality
- Instructor when published
- Campus/location
- Open, closed, waitlist, or unknown status
- Last-updated timestamp
- Direct Global Search and CUNYfirst links

The UI must show freshness and source information and must never promise that a seat will remain available.

### 5.3 Schedule architecture

```text
Degree-plan recommendation
        |
        v
ScheduleLinkService
        |
        +-- GlobalSearchLinkProvider (launch requirement)
        |
        +-- OfficialCunyScheduleProvider (future, approved interface only)
        |
        v
Schedule result card or guided handoff
```

The service interface should be provider-neutral so an official feed can be added later without rewriting the career or degree-planning modules.

Suggested internal contract:

```text
build_search_link(
  institution_code,
  term_code,
  subject_code,
  catalog_number,
  modality=None,
  start_time=None,
  end_time=None
) -> ScheduleSearchLink
```

## 6. System architecture

### 6.1 Deployment model

Use one deployable application with two entry points:

```text
Existing Academic Advisement System
  /login
  /program-selector
  /db-progress
  /transfer-analysis
  /admin/*

CUNY Beyond public module
  /cuny-beyond/*
```

Benefits:

- One source of curriculum truth
- No duplicate course or program records
- Reuse of existing tests and deployment configuration
- Shared security, styling, analytics, and administrative tools
- Easier movement from career exploration into a real degree plan
- Lower hosting and maintenance cost

### 6.2 Backend modules

Recommended modules:

```text
cuny_beyond_routes.py
cuny_beyond_schemas.py
cuny_beyond_service.py
career_matching_service.py
cpl_screening_service.py
schedule_link_service.py
advising_referral_service.py
```

The new routes should call existing curriculum and transfer services rather than duplicate their queries.

### 6.3 Frontend modules

Recommended pages/components:

```text
frontend/cuny_beyond_landing.html
frontend/cuny_beyond_intake.html
frontend/cuny_beyond_career.html
frontend/cuny_beyond_prior_learning.html
frontend/cuny_beyond_results.html
frontend/cuny_beyond_schedule.html
frontend/cuny_beyond_referral.html
frontend/cuny_beyond.js
frontend/cuny_beyond.css
```

Use a resumable stepper, clear progress indicator, keyboard-accessible choices, mobile-first cards, and plain-language explanations.

## 7. Data model

### 7.1 Career and skill tables

```text
careers
- id
- title
- occupation_code
- description
- typical_entry_education
- experience_note
- source_url
- active
- reviewed_at

skills
- id
- name
- category
- description
- active

career_skills
- career_id
- skill_id
- importance_weight

program_careers
- program_id
- career_id
- relevance_weight
- pathway_type
- explanation
- source_url
- reviewed_at
```

`pathway_type` should distinguish:

- Direct or near-term employment possibility
- Entry-level employment with additional credentials
- Transfer-to-bachelor's pathway
- Graduate or advanced-professional pathway
- Related career requiring advisor review

### 7.2 CPL tables

```text
cpl_types
- id
- code
- name
- description
- official_url
- active

program_cpl_guidance
- program_id
- cpl_type_id
- guidance
- evidence_requested
- source_url
- reviewed_at
```

Initial CPL types:

- Previous college coursework
- AP examinations
- CLEP or other recognized examinations
- ACE-recommended education or training
- Employer or industry training
- Military education and training
- Licenses and certifications
- Biliteracy or language proficiency
- Portfolio or documented experiential learning

The system should say **possible CPL opportunity** and direct the student to official evaluation.

### 7.3 Transfer and schedule metadata

Reuse existing program and equivalency tables. Add only missing metadata:

```text
program_transfer_options
- id
- source_program_id
- destination_program_id
- agreement_type
- source_url
- notes
- reviewed_at

academic_terms
- id
- institution_code
- display_name
- global_search_term_code
- starts_on
- ends_on
- active_for_search

schedule_provider_settings
- provider
- base_url
- link_template
- enabled
- verified_at
```

Term codes must be administered or obtained through an approved source; they should not be guessed from the display year.

### 7.4 Anonymous sessions and referrals

```text
exploration_sessions
- id (random UUID)
- pathway
- answers_json
- current_program_id
- target_program_ids
- selected_career_id
- expires_at

advising_referrals
- id
- exploration_session_id
- name
- email
- student_id_last4 (optional)
- consent_timestamp
- summary_json
- created_at
- status
```

Do not store names, emails, or ID digits during ordinary anonymous exploration. Collect them only on the referral step after consent. Set a short expiration policy for anonymous session answers.

## 8. Matching and recommendation logic

Use deterministic, explainable scoring in the prototype:

```text
Explicit career-to-program mapping             50 points
Each matching selected skill                    6 points
Transfer goal supported                         10 points
Relevant prior coursework                       10 points
Relevant CPL possibility                         5 points
Education-path mismatch                  warning only
```

Requirements:

- Scores and weights are configurable by administrators.
- Every result includes a plain-language explanation.
- Source URLs and review dates are retained.
- AI may summarize a result later but may not create the mapping.
- Programs with low evidence should be labeled **Explore with an advisor**.
- The UI should show three strong recommendations rather than a false-precision list of every program.

## 9. Privacy, security, and accessibility

### 9.1 Privacy

- No login is required for exploration.
- Last four ID digits are optional and collected only for referral.
- No full EMPLID, Social Security number, password, or transcript upload in the prototype.
- No personal information in query strings or analytics events.
- Display a consent checkbox before emailing or storing a referral.
- Document data retention and deletion behavior.
- Sanitize all free-text input and rate-limit public submission endpoints.

### 9.2 Security

- Keep all mapping-edit and publishing actions behind the existing admin authorization.
- Add CSRF protection or same-site request protections for referral submission.
- Use server-side validation for all identifiers.
- Prevent open redirects in Global Search and advising links.
- Store email credentials and service keys only in environment variables.
- Log administrative changes without logging sensitive student answers.

### 9.3 Accessibility

- Meet WCAG 2.2 AA design expectations.
- Full keyboard operation and visible focus.
- Semantic headings, labels, fieldsets, and error summaries.
- Do not communicate ranking or status through color alone.
- Announce step changes and validation errors to assistive technologies.
- Make external schedule and registration transitions explicit.

## 10. Implementation phases, tasks, and subtasks

## Phase 0 - Discovery and source audit

**Outcome:** approved scope, sources, privacy boundary, and schedule-integration decision.

### Task 0.1 - Confirm stakeholders and language

- Confirm the service name and public-facing description.
- Confirm the incoming-student categories.
- Confirm who receives advising referrals.
- Confirm whether Career Development and CPL staff must also receive referrals.
- Confirm the official major-change form and advising links.

### Task 0.2 - Audit existing reusable services

- Inventory program, curriculum, degree-map, equivalency, comparison, PDF, and authentication APIs.
- Identify which endpoints can safely be public.
- Extract shared services from route handlers where necessary.
- Record current test coverage and performance baseline.

### Task 0.3 - Validate schedule integration

- Document Global Search fields and interaction sequence.
- Verify whether stable documented deep-link parameters exist.
- Confirm how current terms and term codes will be maintained.
- Contact the appropriate CUNY/BMCC owner before any automated data extraction.
- Approve Level 1 as the guaranteed fallback.

### Task 0.4 - Define prototype content

- Select the initial careers, beginning with Data Analyst and the Computer Science career family.
- Select initial BMCC programs, including Computer Science, Data Science, Mathematics, and related programs.
- Identify initial four-year transfer examples.
- Identify official CPL and advising resources.
- Assign a source and reviewer to every mapping.

**Acceptance criteria:** written data dictionary, approved privacy boundary, confirmed referral destination, and documented schedule strategy.

## Phase 1 - Public shell and anonymous intake

**Outcome:** deployed second entry point with no-login navigation and resumable intake.

### Task 1.1 - Routing and layout

- Add `/cuny-beyond` routes.
- Add the second landing-page entry point.
- Reuse the shared navbar and footer.
- Create responsive stepper layout and error states.

### Task 1.2 - Audience and profile intake

- Implement incoming/current-student selection.
- Implement the six incoming-student categories.
- Ask career goal and current-job questions.
- Keep identity fields out of early steps.
- Add session expiration and restart controls.

### Task 1.3 - Five-skill selection

- Build a controlled skill list with search and categories.
- Enforce exactly or up to five selections according to approved copy.
- Allow **I am not sure** without blocking progress.
- Store only skill identifiers in the anonymous session.

### Task 1.4 - Accessibility and analytics

- Add keyboard and screen-reader tests.
- Add privacy-safe funnel events: entry, step complete, results viewed, schedule handoff, referral started.
- Exclude name, email, free text, and course history from analytics.

**Acceptance criteria:** public URL works on local and hosted environments, no login is required, mobile layout works, and anonymous data expires.

## Phase 2 - Career, program, and skill mapping

**Outcome:** explainable ranked BMCC recommendations connected to real degree maps.

### Task 2.1 - Database migrations

- Add career, skill, career-skill, and program-career tables.
- Add source, reviewed-at, active, and pathway-type fields.
- Create seed files or admin-import format.
- Add uniqueness and referential-integrity constraints.

### Task 2.2 - Curated starter dataset

- Add Data Analyst.
- Add the supplied Computer Science career family.
- Normalize career names and remove truncated or duplicate entries.
- Classify required education/pathway type.
- Map each career to BMCC programs with explanations and sources.
- Map five or more relevant skills to each career.

### Task 2.3 - Matching service

- Implement deterministic scoring.
- Return score components and explanation text.
- Add minimum evidence thresholds.
- Add tests for stable ranking and missing data.
- Ensure empty programs never appear.

### Task 2.4 - Results UI

- Show top three program cards.
- Explain career, skill, education, and transfer fit.
- Link to the existing interactive requirements page.
- Link to official BMCC program and degree-map sources.
- Add compare and download actions.

**Acceptance criteria:** selecting Data Analyst returns reproducible, source-backed results and opens the existing degree planner without reselecting the program.

## Phase 3 - CPL screening

**Outcome:** students receive safe, nonbinding CPL preparation guidance.

### Task 3.1 - Questionnaire

- Ask about prior college credit.
- Ask about AP and recognized examinations.
- Ask about ACE-reviewed learning, employer training, military learning, licenses, biliteracy, and portfolio evidence.
- Add **not sure** and **none** options.

### Task 3.2 - Rules and content

- Add CPL types and program guidance tables.
- Attach official source links.
- Define evidence the student should gather.
- Add staff review date and publishing status.

### Task 3.3 - Results

- Show possible CPL opportunities separately from awarded credit.
- Explain that evaluation is required.
- Add a document checklist for the advising referral.
- Prevent CPL estimates from reducing degree totals automatically.

**Acceptance criteria:** results never claim credit has been awarded and every recommendation identifies the official next step.

## Phase 4 - Current-student major-change pathway

**Outcome:** existing comparison logic becomes an intentional guided workflow.

### Task 4.1 - Context collection

- Ask current campus and major.
- Reuse the completed-course selector.
- Allow one to three proposed majors.
- Restate current and proposed majors throughout the flow.

### Task 4.2 - What-if audit

- Reuse synchronized completion and equivalency logic.
- Show applied, remaining, unmatched, and review-required courses.
- Show prerequisite sequences and estimated remaining credits.
- Preserve elective and concentration rules.

### Task 4.3 - Transfer and action plan

- Show known transfer destinations.
- Link to the official major-change form.
- Generate advisor next steps.
- Carry recommended remaining courses into schedule discovery.

**Acceptance criteria:** a student can move from an existing major to a proposed degree map without manually reentering completed courses.

## Phase 5 - Global Search schedule handoff

**Outcome:** every planned course can be searched in the current or selected CUNY term.

### Task 5.1 - Term administration

- Add academic-term records and Global Search term codes.
- Add an admin interface for activation and verification.
- Display last-verified date.
- Do not infer term codes from year labels.

### Task 5.2 - Course-code normalization

- Parse each campus-scoped course into subject and catalog number.
- Handle decimal and alphanumeric catalog numbers.
- Map application institution codes to Global Search institution values.
- Add validation for unmappable codes.

### Task 5.3 - Link provider

- Implement `GlobalSearchLinkProvider`.
- Use verified deep-link parameters when supported.
- Otherwise open the base search page and show guided filter instructions.
- Open external pages safely in a new tab.
- Add a copyable course-search checklist.

### Task 5.4 - Schedule UI

- Add **Find Sections** to recommended course cards.
- Add selected term, campus, subject, and catalog number to the handoff panel.
- Add modality and time preferences as instructions or verified parameters.
- Explain that Global Search is for discovery and CUNYfirst is for registration.
- Warn that prerequisites, holds, permissions, and seat status still apply.

### Task 5.5 - Testing and monitoring

- Unit-test institution, term, subject, and catalog mappings.
- Add an external-link health check without submitting searches.
- Add a manual verification checklist for each active term.
- Track link failures and fall back to the base search page.

**Acceptance criteria:** from a degree plan, a student can select MAT 301 or CSC 111, choose a term, and reach Global Search with correct BMCC-specific instructions or verified prefilled filters.

## Phase 6 - Advising referral and exports

**Outcome:** students can share a concise, consented pre-advisement package.

### Task 6.1 - Summary

- Include student pathway, career goal, five skills, recommended programs, CPL possibilities, completed coursework summary, transfer options, and schedule-search checklist.
- Add sources and disclaimer.
- Reuse the existing PDF export system.

### Task 6.2 - Referral

- Ask for name and email only at the referral step.
- Make last four ID digits optional.
- Add explicit consent and retention notice.
- Prepare a structured email for BMCC advising.
- Send a copy to the student when approved.
- Avoid email attachment of unnecessary personal data.

### Task 6.3 - Failure handling

- Save a downloadable summary if email fails.
- Show the advisor contact link and copyable subject/body.
- Log delivery status without logging sensitive answers.

**Acceptance criteria:** the student can download the summary and intentionally submit a minimal referral without creating an account.

## Phase 7 - Administrative tools and governance

**Outcome:** mappings stay maintainable and auditable.

### Task 7.1 - Admin screens

- Career and skill management
- Program-career mapping editor
- CPL guidance editor
- Transfer-option editor
- Term and schedule-provider settings
- Source and review-date dashboard

### Task 7.2 - Publishing workflow

- Draft, review, approve, publish, archive, and rollback.
- Require source URLs for publishable mappings.
- Warn about stale review dates.
- Record who changed each rule and when.

### Task 7.3 - Data-quality tests

- Every active career maps to at least one active program.
- Every active mapping has a source and explanation.
- Every recommended program has a populated curriculum.
- Every schedule-enabled term has a verified code.
- No duplicate career-program mappings.
- No public endpoint exposes drafts.

**Acceptance criteria:** administrators can update mappings without changing code or editing production CSV files manually.

## Phase 8 - Approved live-section integration (optional future phase)

**Outcome:** embedded current sections, only with an approved data source.

### Task 8.1 - Governance approval

- Identify the data owner.
- Obtain API/feed documentation and usage permission.
- Establish refresh limits, retention, attribution, and support contacts.

### Task 8.2 - Provider adapter

- Implement the official provider behind the existing schedule interface.
- Add caching with a short time-to-live.
- Store source timestamp and never treat cached status as a guarantee.
- Add circuit breaker and Level 1 fallback.

### Task 8.3 - Section results

- Display sections, meeting patterns, modality, campus, and status.
- Filter against student preferences.
- Explain conflicts without building a registration cart.
- Link every section back to Global Search or CUNYfirst.

**Acceptance criteria:** embedded schedule results remain attributable, fresh, accessible, and safely degradable to Global Search links.

## Phase 9 - Reviewed career discovery and catalog expansion

**Outcome:** visitors can discover supported career language and receive reviewed matches across a broader set of populated BMCC programs.

### Task 9.1 - Career browser

- Add a searchable, keyboard-accessible browser to the career-goal step.
- Show the number of reviewed program relationships for each career.
- Keep free-text aliases available for common job-title variations.
- Provide a no-match recovery path without inventing a recommendation.

### Task 9.2 - Reviewed catalog expansion

- Add sourced careers for Accounting, Human Services, Psychology, Criminal Justice, Public and Nonprofit Administration, Urban Studies, Political Science, and Gerontology.
- Map careers only to populated curricula.
- Distinguish direct career evidence from related preparation that requires transfer, licensure, certification, or graduate education.

### Task 9.3 - Data quality

- Require a published mapping for every active career.
- Test representative aliases and multi-program careers.
- Preserve the earlier Computer Science, Data Science, and Nursing catalog.
- Verify all new sources and explanations.

**Acceptance criteria:** a visitor can browse or type a reviewed title such as Accounting Clerk, Case Manager, Police Officer, or Urban Planner and receive a sourced, explainable BMCC starting point without an unsupported professional-eligibility claim.

## 11. Testing strategy

### Unit tests

- Career scoring and explanations
- CPL rule evaluation
- Program and course-code normalization
- Term and institution mapping
- Schedule-link generation
- Privacy-field validation
- Anonymous-session expiration

### Integration tests

- Career selection to degree-map handoff
- Current-major comparison to schedule handoff
- Admin draft to publication
- Referral consent and email failure fallback
- Existing majors remain unchanged

### Browser and accessibility tests

- Keyboard-only completion
- Screen-reader labels and live regions
- Mobile widths
- External-link warnings
- Back/forward and resume behavior
- No accidental login requirement on public routes

### Regression tests

- Existing program selector
- Completed-course synchronization
- Prerequisites and alternatives
- Transfer equivalencies
- PDF degree-plan download
- Admin authorization
- Existing API response contracts

## 12. Deployment and operations

### Local development

- Feature branch: `codex/cuny-beyond-prototype`
- SQLite for local development
- Seeded career, skill, and mapping data
- Mock email delivery
- Global Search Level 1 link provider

### Hosted deployment

- Same Render service and PostgreSQL database as the existing system
- Database migrations applied during deployment
- Public CUNY Beyond routes enabled by feature flag
- Admin routes remain protected
- Referral email configuration stored in environment variables
- Privacy-safe error and funnel monitoring

Suggested flags:

```text
CUNY_BEYOND_ENABLED=true
CUNY_BEYOND_REFERRALS_ENABLED=false
CUNY_BEYOND_SCHEDULE_PROVIDER=global_search_link
CUNY_BEYOND_LIVE_SECTIONS_ENABLED=false
```

Rollout:

1. Local prototype
2. Private staff preview URL or feature flag
3. Content and privacy review
4. Limited student pilot
5. Metrics and usability review
6. Public second entry point

## 13. Team work breakdown

### Lead developer

- Architecture and shared-service extraction
- Database migrations
- Matching and schedule-provider interfaces
- Privacy and authorization boundaries
- Deployment, monitoring, and final review

### Intern

Good bounded assignments:

- Build the responsive intake stepper from approved wireframes.
- Add the controlled skills selector and tests.
- Populate a reviewed batch of career and skill records using the import template.
- Implement the Global Search guided-handoff card and unit tests.
- Add accessibility tests for the public flow.
- Build admin list/filter screens without publishing authority.

Intern changes should continue through fork branches and pull requests. The intern should not have direct push or merge permission to `main`.

### Professor and BMCC subject-matter reviewers

- Approve user categories and advising language.
- Approve career-to-program relationships.
- Identify official transfer and CPL sources.
- Confirm referral destination and response process.
- Confirm schedule-integration permissions.
- Approve pilot population and success criteria.

## 14. Suggested backlog issues

1. Add CUNY Beyond public route shell and feature flag.
2. Create anonymous intake session and expiration policy.
3. Build audience, career-goal, employment, and five-skill steps.
4. Add career, skill, and program-career database models.
5. Create career-mapping CSV/import validator.
6. Seed Data Analyst and Computer Science career families.
7. Implement explainable career-to-program ranking.
8. Connect recommendation cards to existing degree maps.
9. Add transfer-option summaries.
10. Add CPL questionnaire and nonbinding results.
11. Add current-student major-change entry pathway.
12. Add academic-term and Global Search mapping administration.
13. Implement Global Search guided handoff.
14. Add verified deep-link support with fallback.
15. Add CUNY Beyond PDF summary.
16. Add consented advising-referral workflow.
17. Add CUNY Beyond admin mapping editor.
18. Add accessibility and end-to-end regression suite.
19. Conduct staff preview and content audit.
20. Conduct limited student pilot and report findings.

## 15. Definition of done for the first public prototype

The prototype is ready for staff review when:

- It is available locally and through a feature-flagged hosted URL.
- A visitor can use it without logging in.
- Incoming and current-student pathways are visibly separate.
- Data Analyst produces at least three explainable BMCC recommendations.
- The Computer Science career family has been cleaned, classified, sourced, and reviewed.
- Every recommendation links to the correct existing degree map.
- Transfer options and possible CPL opportunities are clearly separated.
- A student can carry a recommended course to the selected term in Global Search through a verified link or guided handoff.
- The application clearly states that Global Search discovers classes and CUNYfirst handles registration.
- The student can download a summary.
- Referral information is collected only after consent.
- The existing advisement system passes its full regression suite.
- An administrator can review sources and mapping freshness.

## 16. Success measures for the pilot

- Percentage completing the intake
- Percentage opening a recommended degree map
- Percentage comparing more than one program
- Percentage opening Global Search
- Percentage downloading a summary
- Percentage requesting an advising referral
- Student rating of recommendation clarity
- Advisor rating of referral usefulness
- Number of incorrect or unclear mappings reported
- Median completion time
- Accessibility issues discovered and resolved

Do not optimize the pilot around clicks alone. The most important qualitative measure is whether the student arrives at the human-advisor conversation with a clearer goal, a plausible program, relevant prior-learning evidence, and a concrete list of schedule questions.

## 17. Key decisions requiring professor approval

1. Which office receives the referral: Academic Advising, Admissions, Career Development, CPL, or a routing mailbox?
2. Is the last four digits of student ID necessary in the prototype?
3. Which four BMCC programs and which career families form the first reviewed dataset?
4. Which transfer colleges should appear in the first demonstration?
5. Who is authorized to approve career mappings and CPL language?
6. Should the first pilot be public, invitation-only, or feature-flagged?
7. Is Level 1 Global Search handoff sufficient for the pilot?
8. Who can request or approve an official schedule data interface for a later phase?

## 18. Official references

- CUNY Global Class Search: https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController
- BMCC Computer Science A.S.: https://www.bmcc.cuny.edu/academics/departments/cis/computer-science/
- CUNYfirst: https://home.cunyfirst.cuny.edu/

This roadmap describes an advising prototype. Official BMCC and CUNY policies, catalogs, staff decisions, DegreeWorks, Global Search, and CUNYfirst remain authoritative.
