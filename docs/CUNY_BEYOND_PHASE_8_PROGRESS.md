# CUNY Beyond Phase 8 - Approved Live-Section Integration Readiness

## Outcome

Phase 8 adds the safe boundary needed for future embedded current-section results. The repository does not contain an approved CUNY section API, feed agreement, response schema, or credentials. Therefore this phase does not scrape CUNY Global Search and does not claim live seat availability. Students retain the working official-search handoff from Phase 5.

## Implemented

- Added a persistent `ScheduleProviderConfig` governance record.
- Added admin-only read and update endpoints for provider approval metadata.
- Enforced approval, HTTPS, ownership, permission, attribution, support, refresh, and retention rules before enablement.
- Added a provider-neutral `SectionResult` contract for the future adapter.
- Added a circuit breaker primitive with cooldown recovery.
- Added a new student sections endpoint that always fails safely to the verified Global Search handoff while the adapter is gated.
- Updated the student page with a clear live-data status and accessible result announcement.
- Expanded Schedule Data Settings with the provider-governance form and readiness state.
- Seeded a disabled, not-approved provider record only when one does not already exist.

## Data and Request Flow

1. A student selects a verified term and planned course.
2. The browser calls `POST /api/db/cuny-beyond/schedule/sections`.
3. The service evaluates the governed provider configuration.
4. Until an approved adapter exists, it returns `mode: guided_handoff`, an empty `live_sections` array, and `live_data_claimed: false`.
5. The student receives exact filters and a link to CUNY Global Search.

## Safety Contract

Live integration can only be enabled when all of the following exist: approved status, HTTPS API base URL, data owner, permission reference, required attribution, support contact, acceptable refresh interval, and acceptable retention. Even a complete configuration remains adapter-gated until the official response schema and authentication method are implemented and reviewed.

The app never infers that a seat is open. Global Search results still require confirmation, and registration remains in CUNYfirst.

## Verification

Automated tests cover fail-closed readiness, incomplete approval rejection, fallback response semantics, circuit-breaker recovery, admin authorization wiring, accessible status rendering, no-scraping constraints, and seed preservation.

## Remaining Work Before Live Activation

1. Obtain written authorization and official technical documentation from the CUNY data owner.
2. Confirm authentication, permitted fields, refresh limits, retention, attribution, and support escalation.
3. Implement and contract-test the official response adapter.
4. Add short-TTL caching without retaining prohibited data.
5. Test stale data, provider errors, timeouts, accessibility, conflicts, and fallback behavior.
6. Complete security and product-owner review before enabling the provider.

Official fallback: https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController
