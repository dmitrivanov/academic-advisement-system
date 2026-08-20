# Pre-Advisement Package: Simple Explanation and Tester Guide

**Plain-language guide - August 21, 2026**

## What this does in simple words

A student explores a career, gets BMCC major recommendations, and checks possible prior learning. They click **Prepare advising summary**. The next page puts the important information into one short package. The student can save it as a PDF, download a text copy, or intentionally prepare an email for BMCC advising.

The student does not need an account to create or download the package. Their name and email are not requested until they choose the optional advising-referral form. Nothing is sent until they check the consent box and press the send button.

## Reproducible test 1: create a prospective-student package

1. Open `/cuny-beyond` without signing in.
2. Choose **High-school student**.
3. Choose or type **Data Analyst**.
4. Choose **No** for employment.
5. Select **Analyzing data**, **Working with numbers**, and **Communicating ideas**.
6. Choose **None of these** for possible prior learning.
7. Click **Find my BMCC program matches**.
8. Confirm program results appear, then click **Prepare advising summary**.

Expected result: the new page shows the student pathway, career goal, three skills, reviewed program recommendations, no awarded CPL claim, transfer-planning prompts, source links, and the planning disclaimer. The page does not ask the student to sign in.

## Reproducible test 2: save the package

1. From the summary page, click **Save / Print PDF**.
2. In the browser print dialog, choose **Save as PDF** or preview printing.
3. Cancel or save, then click **Download text summary**.

Expected result: the printable version omits the contact form and buttons. The downloaded text file contains the same planning categories and disclaimer.

## Reproducible test 3: optional last four digits

1. Enter a name and valid email.
2. Leave **Last 4 ID digits** empty.
3. Check the consent box.
4. Click **Send or prepare referral**.

Expected result: the request is accepted without ID digits. When automatic delivery is not configured, the page displays a reference ID, prepared subject/body, copy button, and official BMCC Advisement link.

## Reproducible test 4: validation and consent

1. Reload the summary page.
2. Enter a name and email but type `12AB` for the last four digits.
3. Try to submit.
4. Correct it to `1234`, but leave consent unchecked and try again.

Expected result: the browser or server rejects the nonnumeric ID value. Submission is also blocked without explicit consent. No prepared referral appears until both conditions are corrected.

## Reproducible test 5: schedule checklist carried forward

1. While signed in, open `/schedule-handoff?institution_code=BMCC&courses=MAT%20301`.
2. Prepare the Fall 2026 MAT 301 search checklist.
3. Return to CUNY Beyond, complete the Data Analyst path, and prepare the advising summary.

Expected result: **Latest schedule-search checklist** includes Borough of Manhattan CC, the verified term, subject MAT, and course number 301.

## Reproducible test 6: privacy check

1. Complete a referral fallback using a recognizable test name and email.
2. Ask an administrator/developer to inspect `logs/cuny_beyond_referral_delivery.jsonl` locally.

Expected result: the log contains only event ID, timestamp, status, and delivery mode. It contains no test name, email, ID digits, career goal, skills, courses, or summary content.

## What a tester should not expect

- The summary is not an official degree audit.
- A CPL possibility is not awarded credit.
- Transfer prompts are not an official transfer-credit evaluation.
- The referral does not register courses or change a major.
- Email is not sent unless the deployment administrator explicitly enables and configures approved SMTP delivery.
- A failed or unconfigured email never removes the student’s download and copy options.

## Official advising destination

BMCC Academic Advisement: https://www.bmcc.cuny.edu/academics/advisement/advisement/

