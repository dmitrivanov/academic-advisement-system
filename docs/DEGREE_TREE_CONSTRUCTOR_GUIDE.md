# Administrator Guide: Creating a Major Degree Map Tree

The Degree Tree Constructor is available to administrators at `/admin/curriculum-graph`. It turns an existing program curriculum into a student-facing dependency tree and allows reviewed relationship corrections without changing the canonical course membership.

> Use official catalog and degree-map evidence. A visually plausible sequence is not automatically an official prerequisite.

## What this tool manages

- Prerequisite links that must be completed before a dependent course.
- Corequisite links for courses taken together.
- Recommended sequences that communicate advising order without locking a course.
- AND/OR grouping for multi-course prerequisite logic.
- Reversible administrator overrides and a live student-facing preview.

The Major Constructor remains responsible for program membership, curriculum bins, credits, alternatives, elective pools, concentrations, and Common/Flexible Core adjustments.

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

Use campus-qualified course records. Visible codes may repeat across CUNY colleges, so every relationship must resolve within the selected program's institution.

## Understanding AND and OR logic

- Give alternative prerequisites the same `group_id`. Example: CSC 101 or CSC 103 can each lead to CSC 111.
- Give separately required prerequisite groups different group numbers. Example: one programming prerequisite group and one mathematics prerequisite group must both be satisfied.
- Use `recommended` only for an advising sequence that is not enforced as a catalog prerequisite.
- Use `corequisite` only when concurrent enrollment is officially permitted or required.

## Workflow

1. Select the program.
2. Upload a CSV and review every parsed relationship and warning.
3. Press **Save imported relationships** only after review.
4. Drag course cards directly in the visual tree; connecting arrows follow the cards while they move.
5. Select **Save card layout** and confirm before the shared layout is written to the database.
6. To add a link visually, select **Connect courses**, select the earlier course, and then select the course it unlocks.
7. Confirm the proposed link before it is saved. Use the advanced settings only when the relationship is a corequisite, recommended sequence, or needs a particular AND/OR group.
8. To remove a link, select its arrow and confirm. Canonical links are hidden through reversible overrides rather than deleted from the source CSV.
9. Inspect the live preview. Saved overrides immediately become the relationships used by student-facing degree trees.
10. Use **Reset** to remove an override and restore the CSV-derived relationship. Use **Reset layout** to return cards to automatic placement.

## Creating a tree for a newly added major

1. Finish the program draft in Major Constructor and verify every required/elective group has courses and credit targets.
2. Publish or seed the reviewed curriculum so the program is available to the tree service.
3. Open Degree Tree Constructor and select the program.
4. Import its curriculum CSV. Resolve every unknown course, cross-campus mismatch, and malformed prerequisite warning.
5. Compare the preview against the official degree map and catalog prerequisites course by course.
6. Add only evidence-backed relationships that are missing from the canonical data.
7. Check category cards: Common Core, Flexible Core, Program Electives, and other choice groups should remain folded at the top level.
8. Test expansion, collapse, green pathway highlighting, OR branches, and PDF export.
9. Open the same program in the completed-course selector and confirm both views use the same curriculum and prerequisite behavior.

## Review checklist before release

- Program name, campus, degree type, and catalog year are correct.
- Every visible course belongs to the selected campus or has an approved equivalency.
- Every relationship has an official source or documented administrative rationale.
- AND requirements and OR alternatives behave correctly.
- No elective choice was accidentally converted into a prerequisite.
- Category cards open the same choice pools as the completed-course selector.
- Collapsing and reopening cards does not detach or distort relationship lines.
- The selected pathway highlights in green.
- Downloaded PDF is readable and includes the complete tree.
- A student/tester account can view the tree but cannot edit it.

## Troubleshooting

**A course is missing:** Add or publish it through Major Constructor first; the tree cannot create curriculum membership.

**The wrong prerequisite reappears:** Check the program CSV first, then the campus-wide prerequisite file, and finally saved overrides. Reset removes only the override.

**An imported code is unknown:** Confirm the selected campus and the exact code used by that campus. Do not silently substitute a same-code course from another college.

**The student tree differs from the constructor preview:** Save the relationship changes, reload the student page, and confirm both pages selected the same program and catalog year.

## Safe change-control practice

Record the source URL or degree-map reference in the relationship note. Make one coherent change set, preview it, test the student view, and retain the prior CSV or database backup so the change can be reversed. Never infer prerequisites solely from what seems logically necessary.
