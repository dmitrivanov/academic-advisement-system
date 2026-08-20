# CUNY Beyond Phase 4: Guided Major-Change Prototype

**Implementation record and repeatable testing guide — August 21, 2026**

## What Phase 2 already lets a user do

Phase 2 is the incoming-student career-matching prototype. A prospective student can identify their background, describe a career goal in ordinary words, answer a few employment and skill questions, identify possible credit-for-prior-learning experience, and receive reviewed BMCC program recommendations. Each result explains why it matched, links to the program and degree-planning experience, and identifies a possible four-year transfer destination when reviewed data exists.

The earlier “No reviewed match yet” message did not mean the service was offline. It meant the submitted phrase was not in the small reviewed career taxonomy. Phase 4 fixes that usability gap by showing selectable supported careers, browser autocomplete, and one-click retry choices on the no-match screen. Free-text aliases such as “software engineer” still work.

## Phase 4 in very simple words

### High-school student

A high-school student opens CUNY Beyond, chooses **High-school student**, and clicks or types **Data Analyst**. They answer the short questions and press **Find my matches**. They see ranked BMCC majors, a plain-language reason for each match, possible transfer and CPL information, and a button to open the degree planner.

### Current BMCC student

A current student opens CUNY Beyond and chooses **Continue as a current student**. After signing in, the system asks for the current campus and major, then uses the normal completed-course selector. The student opens **Explore Major Change**, chooses up to three other majors at the same campus, and sees what applies, what remains, which completed courses were not automatically applied, which choices need advisor review, prerequisite sequences, and official next steps. Changing the proposed major does not require entering completed courses again.

## What was implemented

- A public reviewed-career catalog endpoint powers the visible career suggestions.
- Career autocomplete and featured career buttons make supported goals discoverable before submission.
- An unsupported goal now offers clickable retry choices instead of a dead end.
- The current-student link opens the selector directly in the major-change path.
- Major change is restricted to other programs at the student’s current campus.
- A student can save and switch among up to three proposed majors.
- The page restates the current major and proposed-major shortlist.
- The same completed-course snapshot is reused for every comparison.
- Results distinguish applied requirements, remaining requirements, completed courses not automatically applied, and requirements needing advisor review.
- Remaining-course cards show prerequisite sequence text when it is present in the curriculum data.
- The next-step panel links to BMCC Student Forms and Academic Advisement and states that this prototype does not submit a change.

## Exact reproducible test 1: high-school Data Analyst

1. Open `/cuny-beyond`.
2. Choose **High-school student**.
3. Click the **Data Analyst** suggestion under the career field.
4. For current employment, choose **No**.
5. Select **Analyzing data**, **Working with numbers**, and **Communicating ideas**.
6. For possible prior learning, choose **None of these**.
7. Click **Find my matches**.

Expected result: the heading says the reviewed career match is **Data Analyst**. Ranked program cards appear for Data Science, Computer Science, and Computer Information Systems. Each card has a match explanation and a planning action. The page does not show “No reviewed match yet.”

## Exact reproducible test 2: alias matching

1. Reload `/cuny-beyond`.
2. Choose **High-school student**.
3. Type **software engineer** in the career field.
4. Choose **No** for employment.
5. Select **Solving technical problems** and **Building or repairing things**.
6. Choose **None of these** for prior learning.
7. Click **Find my matches**.

Expected result: the system recognizes the reviewed **Software Developer** career through its alias and displays a Computer Science recommendation.

## Exact reproducible test 3: recover from an unsupported goal

1. Reload `/cuny-beyond` and choose **High-school student**.
2. Type **Marine biologist**.
3. Complete the remaining required questions and click **Find my matches**.
4. Confirm the no-match explanation appears with supported-career buttons.
5. Click **Data Analyst** in that message.

Expected result: the form retries immediately and displays reviewed Data Analyst program matches. The tester does not have to restart the questionnaire.

## Exact reproducible test 4: current-student major change

1. Open `/cuny-beyond` and click **Continue as a current student**.
2. Sign in with the provided non-admin tester account if asked.
3. Confirm the selector opens at the current campus/current major step.
4. Choose **Borough of Manhattan Community College** and a populated current major such as **Computer Science**.
5. Choose manual entry and continue to the completed-course page.
6. Mark at least three completed courses, for example **ENG 101**, **CSC 101**, and **MAT 206**, when available in that program’s selector.
7. Click **Explore Major Change**.
8. Select another BMCC major and click **Add proposed major**. Add one or two more if desired.
9. Click any saved proposed-major button, then click **Run Major Change Analysis**.

Expected result: the page restates the current major and shows no more than three proposed majors. The same completed-course pills remain visible when switching proposed majors. Results show **Completed credits applied**, satisfied requirements, remaining requirements, completed courses not automatically applied, advisor-review items, and official next steps. No official major change is submitted.

## Validation boundaries

This is a planning prototype, not DegreeWorks and not an official transfer-credit or major-change determination. Direct matches, alternatives, reviewed equivalencies, and configured choice groups can be applied automatically. Unmatched courses, placeholders, substitutions, elective interpretations, financial-aid effects, and catalog-year questions remain advisor-review items.

## Official references

- BMCC Student Forms: https://www.bmcc.cuny.edu/registrar/student-resources-forms/student-forms/
- BMCC Academic Advisement: https://www.bmcc.cuny.edu/academics/advisement/advisement/

