# Major Constructor Administrator Guide

This guide describes the administrator-facing Major Constructor as it works today. It covers the complete safe workflow, explains the supported rule types, and identifies adjustments that must still be maintained through the curriculum CSV architecture.

## 1. What the constructor currently supports

An administrator can:

- create and reopen curriculum drafts;
- select an existing campus and department;
- enter the program name, program code, degree type, catalog year, and official source URL;
- represent concentrations as separate curriculum tabs;
- search the canonical course database;
- add courses to Major Requirements, Major Electives, Common Core, and Flexible Core;
- see the total credits currently placed in each bin;
- create pairwise course alternatives (`Course A OR Course B`);
- create direct prerequisite rules (`Course A requires Course B`);
- record a student-facing note for a major-specific Common/Flexible Core adjustment;
- preview the current concentration;
- validate required metadata and course references;
- save immutable version snapshots and restore an unpublished snapshot;
- move a draft through review and approval;
- publish an approved basic curriculum as new program records.

The constructor does not yet support all curriculum structures. See [Section 12](#12-current-limitations-and-when-not-to-publish) before publishing.

## 2. Before creating a draft

Gather all official evidence first:

1. The official program requirements page.
2. The official two-year and/or three-year program map for the correct catalog year.
3. All footnotes attached to Common Core, Flexible Core, electives, and prerequisites.
4. Official course descriptions when the prerequisite structure is unclear.
5. The existing institutional Pathways group codes from `docs/pathways_groups.csv`.

Do not infer a rule from course scheduling order alone. A course appearing earlier on a map is not necessarily a prerequisite.

Before starting, confirm that every required course exists under **Admin → Courses**. The constructor can select existing database courses but cannot create a missing catalog course.

## 3. Create the draft and enter metadata

Open **Admin → Major Constructor** and choose **New major draft**.

Complete every metadata field:

- **Campus:** the institution that owns the curriculum.
- **Department:** filtered to the selected campus.
- **Program name:** the official name without an invented abbreviation.
- **Program code:** a stable internal code such as `PSY-GEN-AS`.
- **Degree type:** the official award, such as `A.A.`, `A.S.`, or `A.A.S.`.
- **Catalog year:** the effective curriculum year, such as `2026-2027`.
- **Official source URL:** the college page supporting the requirements.

The program code and catalog year identify the published curriculum. Publishing refuses to overwrite an existing record with the same department, code, and catalog year.

Choose **Save draft** before moving to curriculum entry.

## 4. Model concentrations

Keep the default **General** concentration when the official program has one curriculum with no named concentrations.

When students formally choose between different curricula, create a tab for each official concentration. For example:

- `Psychology - General Concentration`
- `Psychology - STEM Concentration`

Each concentration owns its own four curriculum bins. Courses added under one concentration are not automatically copied to another concentration.

On publication, a draft with multiple concentrations creates separately selectable program records. The first uses the base program code with `-1`, the second `-2`, and so on. Until custom concentration codes are implemented, choose and verify the base code carefully.

## 5. Fill curriculum bins

Select the active concentration tab. Search by course code or title, select a destination bin, and click a course result.

Use the bins as follows:

| Bin | Include |
| --- | --- |
| Major Requirements | Individually required courses and courses participating in a required OR rule |
| Major Electives | Courses or placeholders used for major elective credit |
| Common Core | Required Core placeholders or specifically required Core courses |
| Flexible Core | Flexible Core placeholders or specifically required Flexible Core courses |

The displayed number is the sum of all course records currently in the bin. It does not yet represent a configurable required-credit target. For an OR pair, the displayed total can therefore exceed the credits the student must actually complete.

A course may appear in more than one bin when the official curriculum intentionally allows or requires double placement. Validation reports this as a warning, and the student progress system synchronizes completion state for the same course.

## 6. Course alternatives (`OR` rules)

Use an alternative rule when the official requirement says that either of two courses satisfies one requirement.

Example:

```text
PSY 240 OR PSY 250
```

Procedure:

1. Add both courses to the appropriate curriculum bin.
2. Under **Rules and major adjustments**, select the first course as Alternative A.
3. Select the second course as Alternative B.
4. Choose **Add OR rule**.
5. Confirm the rule appears in the rule list.

Do not use an OR rule for a broad elective pool such as “choose 9 credits from this list.” Pairwise alternatives only express one-of-two logic.

Current OR rules are pairwise. Requirements such as `A OR B OR C` and “choose two of four” need the elective-pool editor described in Section 12.

## 7. Prerequisites

Use a prerequisite rule only when supported by an official course description or curriculum rule.

Example:

```text
MAT 301 requires MAT 206
```

Procedure:

1. Select the dependent course under **Course**.
2. Select its prerequisite under **Requires**.
3. Choose **Add prerequisite**.
4. Confirm the direction in the rule list.

The current editor creates one direct prerequisite per rule. Multiple saved prerequisite rules for the same course behave as separate required prerequisites. The constructor does not yet provide a visual prerequisite expression editor for mixed logic such as `(A OR B) AND C`.

If a prerequisite is not itself a degree requirement, it may still need a selectable external-prerequisite representation. Do not add it to a degree bin merely to make the prerequisite rule work.

## 8. Common/Flexible Core adjustments

The system architecture separates college-wide groups from major-specific restrictions:

1. `docs/pathways_groups.csv` defines canonical Common/Flexible Core groups.
2. `docs/pathways_courses.csv` defines the broad course membership of each group.
3. `docs/program_choice_group_adjustments.csv` narrows or modifies a group for one major.

An adjustment may:

- include only named courses;
- include only selected subject prefixes;
- exclude courses from the base group;
- change required credits or required course count;
- add a brief student-facing explanation.

The constructor currently records only the **group code and student-facing note** in its versioned draft document. Example:

```text
Group code: BMCC-FLEX-SCIENTIFIC-WORLD
Note: For this major, choose one course from PHY 110, PHY 210, or PHY 215.
```

The current constructor does **not** yet apply an include/exclude list to the published choice group. For a real restriction, enter the full rule in `docs/program_choice_group_adjustments.csv` and validate it using the normal CSV workflow. A note by itself does not restrict the courses a student can select.

Never edit the college-wide base group to enforce a restriction belonging to only one major.

## 9. Placeholder requirements and elective pools

Placeholders such as these require a populated choice group:

```text
PSY-GEN-LIBERAL — Liberal Arts Elective
PSY-GEN-GENERAL — General Elective or Common Core STEM excess credits
```

A placeholder must never be selectable when its `choice_group_code` is empty or points to a group without courses.

The current constructor can place an existing placeholder course in a bin, but it cannot create or edit the placeholder’s pool membership. Until the elective-pool editor is implemented:

1. Define the pool in the canonical CSV architecture.
2. Seed and verify that the placeholder opens a complete course selector.
3. Add the existing placeholder course to the constructor bin.
4. Verify the published program manually on the progress page.

## 10. Save, version, preview, and validate

Use **Save draft** after each meaningful change. Saving updates the editable document; it does not create a historical snapshot.

Use **Create version** at review boundaries, for example:

- initial transcription complete;
- official footnotes audited;
- reviewer corrections complete;
- ready for approval.

**Preview major** shows the active concentration, its bins, and selected course codes. This is currently a structural preview, not a pixel-identical copy of the completed-courses page.

**Validate** currently blocks submission when:

- campus or department is missing;
- required program metadata is missing;
- no concentration exists;
- a concentration has no courses;
- a referenced course ID does not exist;
- an OR or prerequisite rule references a missing course.

It warns when the same course appears in multiple bins.

Validation does not yet reconcile the curriculum to a required 60-credit total, evaluate complex elective math, or compare the draft against official PDFs. Those checks remain part of human review.

## 11. Review, approval, publishing, and restore

The normal lifecycle is:

```text
draft → in_review → approved → published
                    ↘ changes_requested → in_review
```

- **Submit for review** saves and validates the draft before moving it to `in_review`.
- **Approve** is allowed only from `in_review`.
- A reviewer can return an in-review draft as `changes_requested` through the API; a dedicated reviewer control is still pending in the page.
- **Publish** is allowed only after approval and another successful server validation.

Publishing creates new program, requirement-group, alternative, and prerequisite records in one database transaction. If any protected operation fails, the transaction is rolled back.

Restoring a saved version copies that snapshot into the editable draft and returns it to `draft` status. A published curriculum is immutable in this release; create a new draft/catalog version rather than silently changing records used by students.

## 12. Current limitations and when not to publish

The editor is not yet a complete replacement for the CSV curriculum workflow. These features are still pending:

- credit targets and custom credit splits for bins;
- broad elective pools and “choose N courses/credits” rules;
- three-or-more-course alternative sets;
- mixed AND/OR prerequisite expressions;
- Core adjustment include/exclude course picker;
- subject-prefix adjustment rules;
- creating missing courses and placeholders;
- custom sequences and co-requisites;
- importing requirements from program-map PDFs;
- exact completed-courses-page preview;
- draft deletion, concentration rename/removal, and custom concentration codes;
- reviewer comments and a page control for requesting changes;
- CSV import/export and synchronization with repository source files;
- rollback of already published live program records.

Do not publish from the constructor alone when the major depends on any pending feature. Maintain those rules in the reviewed CSV files and use the existing seeding/validation workflow until the corresponding visual editor is implemented.

## 13. Final publication checklist

Before publishing, verify all of the following:

- [ ] Program identity and catalog year match the official source.
- [ ] Every official concentration has the correct curriculum.
- [ ] All curriculum sections and footnotes were transcribed.
- [ ] Every required course is in the correct bin.
- [ ] OR pairs are represented and are not being counted as multiple required courses.
- [ ] Prerequisite directions and AND/OR meaning are correct.
- [ ] Every placeholder opens a non-empty, correct course selector.
- [ ] Major-specific Core restrictions exist in the adjustment CSV, not only as notes.
- [ ] Credits reconcile to the official program total after applying alternatives and elective rules.
- [ ] Constructor validation passes and warnings were reviewed.
- [ ] A version snapshot was created before approval.
- [ ] A second person compared the preview and CSV data against official sources.
- [ ] The completed-courses page was regression-tested after publication.
