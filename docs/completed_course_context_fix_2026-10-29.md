# Completed-course context preservation fix

## Symptom

The structured chatbot could show several confirmed completed courses, while the
saved academic plan and final advising report retained only the subset that the
selected program's curriculum engine could apply directly. In the reported case,
five courses were confirmed but the generated plan retained one three-credit
course.

## Root cause

The chatbot correctly stored the complete reported-course list in
`cunyBeyondImportedCoursesV1`. The planner then created a program-specific
snapshot from only direct curriculum rows and selected choice-group options.
When the plan was saved, that reduced snapshot replaced the original browser
session list. Courses not represented in the selected program, and courses still
requiring an official equivalency or requirement-area decision, were therefore
forgotten rather than retained for advisor review.

A second issue compounded this for choice groups: importing multiple completed
options assigned each option to the same placeholder using replacement semantics,
so the last option could overwrite earlier imported options.

## Fix

- Preserve the complete reported-course list separately from the set applied by
  the selected degree audit.
- Merge, rather than replace, imported options assigned to a choice placeholder.
- Save three explicit collections with the academic-plan artifact:
  `reported_completed_courses`, `applied_completed_courses`, and
  `pending_review_courses`.
- Keep all reported courses in the chatbot, transfer snapshot, final advising
  summary, and printable academic-plan document.
- Label courses that are not directly applied as needing advisor review; do not
  silently award them to a requirement or discard them.

## Safety boundary

The change does not invent transfer equivalencies or degree applicability. The
planning algorithm still counts only courses supported by the selected program's
curriculum and choice data. The report now makes the distinction visible while
preserving the student's complete history.

## Regression coverage

`tests/test_completed_course_context.py` reproduces the five-course/one-applied
scenario and verifies that all five courses and all 17 reported credits survive,
while the applied and pending-review subsets remain accurate. Existing planner
tests cover Computer Science, Accounting, Mathematics, Nursing, and other program
flows.
