# Student program selector versioning

Student-facing program lists call `/api/db/programs?selector_only=true`. The
API groups records by campus, normalized official program name, and normalized
degree type, then returns one record per identity. A populated curriculum wins
over an empty record; otherwise the newest valid catalog wins. For the same
ending year, a single-year label such as `2026` ranks above `2025-2026`, and an
exact tie uses the highest database ID. Invalid or missing years rank last.

The unfiltered `/api/db/programs` response remains available to the admin
dashboard and returns every database record.

## Future archive behavior

A future migration should add a lifecycle status or nullable `archived_at`
field. Selector candidates should exclude archived records, while admin views,
auditing, rollback, and existing student-plan references retain access to
them. Archiving should not delete historical curriculum rows or overload the
catalog-year field.
