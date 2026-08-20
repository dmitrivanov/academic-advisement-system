# Find Current Sections: Simple Explanation and Tester Guide

**Plain-language guide - August 21, 2026**

## What this does in simple words

A student finishes a degree plan and sees that MAT 301 is still needed. They click **Find Sections**, choose **2026 Fall Term**, and optionally choose online, in-person, morning, evening, or another preference. The app tells them exactly what to select in CUNY Global Search and opens the official page. The student then uses CUNYfirst to register.

The app does not claim that MAT 301 has an open seat. It does not register the student. It helps the student move from “this is the course I need” to “this is how I look for its current sections.”

## Reproducible test 1: MAT 301 from a degree plan

1. Sign in with the non-admin tester account.
2. Open **Programs** and select a populated BMCC major that includes MAT 301.
3. Continue to **My Progress**.
4. Mark prerequisite courses completed if necessary and generate the semester plan.
5. Find MAT 301 in a future semester and click **Find Sections**.
6. Confirm the page shows campus **BMCC**, planned course **MAT 301**, and **2026 Fall Term - verified 2026-08-21**.
7. Choose **Online** and **Evening**.
8. Click **Prepare search**.

Expected result: the checklist says Borough of Manhattan CC, 2026 Fall Term, subject MAT, course number 301, Online, and Evening. The page displays a verification date and the CUNYfirst warning. **Copy checklist** and **Open CUNY Global Search** appear.

## Reproducible test 2: from major-change analysis

1. Complete the Phase 4 current-student major-change test.
2. In **Remaining Requirements**, find a concrete course such as CSC 111 or MAT 301.
3. Click **Find Sections**.
4. Choose the active term and click **Prepare search**.

Expected result: the same completed-course comparison remains in the original browser tab. The new page shows the selected proposed-major course and correct campus-specific instructions.

## Reproducible test 3: decimal course number

1. Directly open `/schedule-handoff?institution_code=BMCC&courses=MAT%20157.5` while signed in.
2. Click **Prepare search**.

Expected result: the checklist separates the course into subject **MAT** and course number **157.5**. It does not remove the decimal.

## Reproducible test 4: multiple planned courses

1. Open `/schedule-handoff?institution_code=BMCC&courses=MAT%20301,CSC%20111` while signed in.
2. Click the **CSC 111** course button.
3. Click **Prepare search**.

Expected result: the checklist uses subject **CSC** and course number **111**. Clicking MAT 301 and preparing again switches the checklist back to MAT and 301.

## Reproducible test 5: admin term control

1. Sign in with the admin account.
2. Open **Admin**, then **Global Search Terms**.
3. Confirm Spring 2026 and Summer 2026 are inactive and Fall 2026 is active.
4. Open **Verify source** and confirm the name and code against the official term selector.
5. Do not change the verified code unless the official source differs.

Expected result: only active terms appear on the student schedule page. Each term has a visible verification date. A non-admin account cannot open the term-management page.

## What a tester should not expect

- The app does not show live seats or instructors.
- The official site is not automatically filled because its stable public deep-link parameters are not documented.
- The app does not register classes.
- The app cannot remove holds, waive prerequisites, or grant permission.
- Availability can change after the student opens Global Search.

## Official destination

CUNY Global Search: https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController

