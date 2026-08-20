# CUNY Beyond Phase 7 Progress: Governance and Career Expansion

**Technical implementation record - August 21, 2026**

## Outcome

Phase 7 moves CUNY Beyond’s evidence mappings from seed-only maintenance toward an administrator-controlled governance workflow. Administrators can create, revise, review, approve, publish, archive, version, and roll back careers, skills, program-career mappings, CPL guidance, and transfer options. A dashboard reports missing mappings, stale reviews, mapped programs without curriculum, and active schedule terms without provider codes.

The phase also begins expansion beyond computing careers by adding a reviewed **Registered Nurse** career, including RN, staff nurse, nurse, and professional nurse aliases, mapped to the populated BMCC Nursing A.A.S. curriculum.

## Why nursing is narrowly mapped

The initial nursing match is deliberately limited to Registered Nurse. BMCC’s Nursing A.A.S. supports the professional registered-nursing/licensure pathway. Advanced-practice careers such as nurse practitioner require education beyond an associate degree and are not presented as direct outcomes of this program.

## Governed data types

- Careers and their aliases, source, review date, active state, and up to five skill relationships
- Skills used in explainable matching
- Program-career evidence, points, explanation, source, official program URL, and review date
- Program-specific CPL guidance and evidence expectations
- Reviewed transfer destinations and explanations
- Academic-term/provider settings through the existing Phase 5 term interface

## Publishing workflow

The allowed state sequence is:

`Draft -> In review -> Approved -> Published -> Archived`

An in-review or approved item can be returned to draft. An archived item can be reopened as a draft. Publishing is rejected unless the record is already approved and has an HTTPS source. Entity-specific validation requires the relevant career, program, CPL type, explanation, and evidence fields.

Every save and transition creates an immutable version containing the document, status, user, and timestamp. **Rollback previous** restores an earlier document as a new draft; it never silently rewrites the published database record.

## Public/private separation

Public recommendation endpoints continue to query active `Career` and `ProgramCareer` records only. They never query governance drafts. A draft, review, or approved-but-unpublished record therefore cannot appear in student results.

Initial CSV seeding now inserts missing records without deleting or overwriting administrator-governed career mappings and CPL guidance. This prevents a deployment from erasing a published admin correction.

## Transfer option support

The new `TransferOption` model stores the source program, target institution/program/degree, target link, evidence explanation, source, review date, and active state. Published options are included in recommendation responses and carried into the Phase 6 advising package. If no reviewed destination exists, the student is told to review the program in CUNY Transfer Explorer with an advisor rather than receiving an invented destination.

## Data-quality dashboard

The admin dashboard reports:

- Active careers with no active program mapping
- Career records older than the 365-day review threshold
- Active mapped programs without populated requirement groups
- Active Global Search terms without provider codes
- Counts for active careers, skills, mappings, and unfinished governance drafts

## Automated quality gates

Repository tests verify every active seeded career has an active mapping, mapping keys are unique, evidence fields and HTTPS sources are present, every recommended program has curriculum data, Registered Nurse maps to Nursing A.A.S., public endpoints exclude drafts, workflow transitions are constrained, and deployment seeding preserves governed records.

## Career expansion method going forward

Each BMCC program should be processed using the same evidence method used for Computer Science:

1. Read the official BMCC program page and its explicitly listed career outcomes.
2. Normalize each supported occupation and common aliases into one career record.
3. Assign no more than five relevant skills.
4. Create a program-career mapping with evidence strength and a plain-language explanation.
5. Require the official source URL and review date.
6. Confirm the mapped major has a complete curriculum selector.
7. Review, approve, publish, and test the mapping.

Careers that require a higher credential must be labeled as transfer/long-term destinations or excluded from direct associate-degree outcomes.

## Official source used for the first expansion

BMCC Nursing Program: https://www.bmcc.cuny.edu/academics/departments/nursing/nursing-program/

