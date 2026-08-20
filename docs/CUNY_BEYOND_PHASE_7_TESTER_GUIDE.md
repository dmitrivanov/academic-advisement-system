# Career Governance and Nursing Match: Simple Tester Guide

**Plain-language guide - August 21, 2026**

## What this does in simple words

An administrator can now prepare a new career recommendation without editing a CSV file on the server. They create a draft, add the official source and matching information, send it for review, approve it, and publish it. Students cannot see it until publication.

The first new non-computing example is **Registered Nurse**. A student can type “nurse,” “RN,” “staff nurse,” or “Registered Nurse” and receive the BMCC Nursing A.A.S. recommendation.

## Reproducible test 1: nursing recommendation

1. Open `/cuny-beyond` without signing in.
2. Choose **High-school student**.
3. Click **Registered Nurse** or type **RN**.
4. Choose **No** for employment.
5. Select **Helping people**, **Communicating ideas**, and **Organizing projects**.
6. Choose **None of these** for prior learning.
7. Click **Find my BMCC program matches**.

Expected result: the reviewed career heading says **Registered Nurse** and recommends **Nursing (A.A.S.)**. The explanation refers to the nursing/professional licensure pathway and links to the official BMCC Nursing page. It does not claim the student is licensed and does not recommend nurse practitioner as a direct associate-degree outcome.

## Reproducible test 2: open the governance dashboard

1. Sign in with the admin account.
2. Open **Admin**.
3. Choose **Career & Evidence Governance**.

Expected result: the page shows counts for careers, skills, mappings, and unfinished drafts. Issue cards report unmapped careers, stale careers, mappings without curriculum, and schedule terms without codes. Career and program-mapping catalogs are visible.

## Reproducible test 3: create a career draft

1. In the governance page, select **Career**.
2. Enter an official HTTPS source.
3. Enter valid JSON containing `slug`, `name`, `aliases`, `source_title`, `reviewed_at`, `active`, and `skill_slugs`.
4. Click **Save draft**.

Expected result: the item appears with status **Draft**. It does not appear in the public CUNY Beyond career suggestions or matching results.

## Reproducible test 4: review and publish

1. On the saved draft, click **In review**.
2. Click **Approved**.
3. Click **Published**.

Expected result: invalid transitions are not offered. Publication requires an HTTPS source and valid entity fields. After successful publication, the record is available to the published catalog. A program-career mapping must also be published before the career can produce a recommendation.

## Reproducible test 5: version and rollback

1. Create a second draft or return an in-review draft to Draft.
2. Click **Load JSON**, change a harmless field, and save.
3. Click **Rollback previous** and confirm.

Expected result: the earlier content is restored as a new Draft version. The operation does not silently change a published student recommendation.

## Reproducible test 6: source and quality warning

1. Create a draft using a non-HTTPS source or omit a required explanation.
2. Move it through review and approval, then attempt publication.

Expected result: publication is rejected with a clear validation message. The public site remains unchanged.

## How to add the next majors and careers

For Nursing, Accounting, Psychology, Sociology, Business, and every other BMCC program:

1. Use the official program page.
2. Add only career outcomes supported by that page or another authoritative source.
3. Group spelling variations and job-title synonyms as aliases.
4. Choose up to five skills.
5. Map the career to a populated major and explain the evidence.
6. Add reviewed transfer options separately when supported.
7. Review, approve, publish, and reproduce the student search.

Do not map a job merely because it sounds related. Do not present a career requiring a bachelor’s, master’s, doctorate, or professional license as an immediate associate-degree outcome.

## Official nursing source

BMCC Nursing Program: https://www.bmcc.cuny.edu/academics/departments/nursing/nursing-program/

