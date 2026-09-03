# Degree Tree Constructor

The Degree Tree Constructor is available to administrators at `/admin/curriculum-graph`.

## Source precedence

1. A program's curriculum CSV is authoritative for prerequisite relationships explicitly declared in that program.
2. `course_prerequisites.csv` supplies a campus-wide relationship only when the program CSV has no prerequisite declaration for that course.
3. Administrator changes are stored as reversible graph overrides. Student-facing degree trees apply these overrides without rewriting the source curriculum CSV.

## Import formats

The constructor accepts the standard curriculum format used by files such as `cs_courses.csv`. It reads `course_code` and `prerequisites`. Use `or` inside one prerequisite group and `|` between requirements that must both be completed.

It also accepts the compact format in `degree_tree_relationship_template.csv`:

- `source_course`: earlier course
- `target_course`: course unlocked by the source
- `relation_type`: `prerequisite`, `corequisite`, or `recommended`
- `group_id`: alternatives use the same group number; separate required groups use different numbers
- `note`: optional administrative source or rationale

## Workflow

1. Select the program.
2. Upload a CSV and review every parsed relationship and warning.
3. Press **Save imported relationships** only after review.
4. For a manual change, drag a course card into the earlier-course and dependent-course wells.
5. Select the relationship type and AND/OR group number.
6. Add the relationship or hide a canonical relationship.
7. Inspect the live preview. Saved overrides immediately become the relationships used by student-facing degree trees.
8. Use **Reset** to remove an override and restore the CSV-derived relationship.

Curriculum membership and requirement-bin editing remain in `/admin/major-constructor`. The Degree Tree Constructor manages relationships and their visual preview.
