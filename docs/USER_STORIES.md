# Academic Advisement System: User Stories

The primary audiences are current and prospective students. Academic advisors and curriculum administrators are supporting audiences. Transfer students and students changing majors are treated separately because their decisions depend on equivalencies and what-if comparisons.

## Current CUNY student

1. As a current student, I want to select my campus and major and mark completed courses so that I can see which requirements remain.
2. As a student, I want the same completed course to count everywhere it legitimately satisfies a requirement so that my progress is not understated.
3. As a student, I want locked courses to show their prerequisites so that I understand what must be completed first.
4. As a student, I want elective and alternative groups to enforce course and credit limits so that I cannot accidentally create an invalid plan.
5. As a student, I want satisfied requirements to be clearly identified so that I can focus on unfinished areas.
6. As a student, I want to generate and download a semester-by-semester PDF plan so that I can review it with an advisor.

## New or prospective student

7. As a new student with no completed courses, I want a first-semester pathway so that I can begin planning without entering a transcript.
8. As a prospective student, I want to compare programs, required credits, and course sequences so that I can choose a suitable major.
9. As a prospective student, I want links to official program sources so that I can verify important requirements.

## Student changing majors

10. As a student considering a major change, I want a what-if analysis using my completed courses so that I can see which credits apply and what remains.
11. As a student changing majors, I want a clear summary of credits that apply, do not apply, or require review so that I can estimate time to completion.
12. As a student changing majors, I want to compare the remaining workload of different programs so that I can make an informed decision.

## CUNY transfer student

13. As a transfer student, I want course equivalencies matched by campus and course code so that similarly numbered courses from different colleges are not confused.
14. As a transfer student, I want to compare my current program with a destination program so that I can identify transferable courses, gaps, and prerequisite sequences.
15. As a transfer student, I want official source links and warnings for unverified equivalencies so that I know when advisor confirmation is necessary.
16. As a transfer student, I want combination equivalencies to be recognized so that multiple source courses can satisfy one destination requirement when officially permitted.

## Academic advisor

17. As an advisor, I want to review a student's completed courses and generated plan so that I can focus the meeting on exceptions and decisions.
18. As an advisor, I want requirement explanations, prerequisites, and official degree-map links in one place so that recommendations are traceable.
19. As an advisor, I want the AI summary to use only the selected program and student context so that it does not invent policy.
20. As an advisor, I want elective and prerequisite violations to be visually clear so that I can identify planning problems quickly.

## Curriculum administrator or department representative

21. As a curriculum administrator, I want to create a major as a draft, organize courses into requirement bins, and preview the student view so that I can validate it before publication.
22. As a curriculum administrator, I want to define alternatives, prerequisites, elective pools, credit limits, and Common/Flexible Core adjustments so that published rules are machine-enforced.
23. As a curriculum administrator, I want validation, approval, versioning, and rollback so that incomplete or incorrect curricula are not published.
24. As a curriculum administrator, I want official sources and degree-map PDFs attached to each program so that future audits are possible.
25. As a curriculum administrator, I want course selection limited to the chosen campus so that courses from other institutions are not accidentally added.

## System administrator and tester

26. As a system administrator, I want role-based access so that testers can use student functionality without changing curriculum data.
27. As a tester, I want a dedicated non-administrator account so that I can evaluate the real student experience.
28. As a maintainer, I want automated tests for duplicate programs, empty course groups, invalid rules, and regressions so that new data does not corrupt existing programs.
29. As a system administrator, I want configurable credentials and session secrets so that local and hosted environments can use different security settings.

## Suggested implementation priority

1. Student progress accuracy and curriculum-rule enforcement.
2. Transfer and major-change equivalencies.
3. Advisor review and official-source transparency.
4. Major Constructor validation and publishing.
5. Expanded roles, audit logs, archival controls, and institutional reporting.
