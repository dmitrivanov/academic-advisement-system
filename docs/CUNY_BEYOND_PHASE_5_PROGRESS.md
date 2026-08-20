# CUNY Beyond Phase 5 Progress: Global Search Schedule Handoff

**Technical implementation record - August 21, 2026**

## Outcome

Phase 5 connects a planned course to the official CUNY Global Search without scraping live sections or claiming a fragile deep link is prefilled. Students can choose an administrator-verified term, course, modality preference, and time preference; receive exact BMCC-specific search instructions; copy the checklist; and open Global Search in a new tab while keeping the advising plan open.

## Implemented architecture

The new provider-neutral `schedule_link_service.py` separates course parsing and institution mapping from the user interface. It returns a structured handoff object containing the official provider URL, normalized subject and catalog number, selected term, instructions, verification date, and disclaimer. The response explicitly sets `prefilled` to false because no documented stable deep-link parameter contract was found.

The `AcademicTerm` database model stores the term name, exact provider code, provider, verification timestamp, source URL, and activation state. Initial records are seeded from `docs/cuny_beyond_academic_terms.csv`, but seeding does not overwrite later administrator decisions.

## Verified source data

The official Global Search interface was inspected on August 21, 2026. It displayed Borough of Manhattan CC and these term option values:

- 2026 Spring Term: `1262`
- 2026 Summer Term: `1266`
- 2026 Fall Term: `1269`

Only 2026 Fall Term is active in the initial configuration. Past terms remain stored for auditability and are not shown to students.

## Backend

- Public active-term endpoint.
- Public validated handoff endpoint.
- Admin-only all-term endpoint.
- Admin-only term-update endpoint.
- Fail-closed behavior for inactive terms, unknown campuses, and unparseable course placeholders.
- Reviewed institution labels for BMCC, Brooklyn College, City College, and John Jay College.
- Parsing support for ordinary, decimal, compact, and alphanumeric course codes.

## Student interface

The authenticated `/schedule-handoff` page provides verified term selection, planned-course selection, modality and time preferences, a copyable checklist, and the official Global Search launch button. It explains that Global Search is for discovery and CUNYfirst is for registration.

Concrete remaining courses now receive **Find Sections** actions in both the degree-plan semester view and the major-change/transfer remaining-requirements view. Generic elective placeholders do not receive misleading search buttons.

## Administrator interface

The admin dashboard links to `/admin/schedule-settings`. An administrator can inspect the provider code and verification date, activate or deactivate a term, update its reviewed label/code/date, and open the official source for manual verification.

## Safety and limitations

The feature does not scrape section availability, submit searches, register a student, promise a seat, or bypass CUNYfirst. Modality and time are presented as filters for the student to apply. Prerequisites, holds, permissions, enrollment appointments, and live seat status remain controlling conditions.

## Validation

Automated tests cover course normalization, decimal and alphanumeric catalog numbers, unmappable values, institution mapping, non-prefilled behavior, authenticated routes, admin connectivity, and Find Sections entry points. The full existing test suite is also run to protect curriculum and selector behavior.

## Official source

CUNY Global Search: https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController

