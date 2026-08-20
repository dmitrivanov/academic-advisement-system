# CUNY Beyond Phase 8 - Simple Tester Guide

## What This Phase Means in Simple Words

A student can ask the app to find a current section for a planned course. Because an approved live CUNY data connection is not available yet, the app clearly says that live sections are unavailable and gives the student an exact checklist for searching the official CUNY Global Search page. It does not invent seat availability.

An administrator can document a future official connection. The app will not allow that connection to be enabled unless its approval and ownership information is complete.

## Student Test - Safe Official Search

1. Sign in as a student and open a degree plan containing `MAT 301`.
2. Choose the action to find sections for that planned course.
3. On Find Current Sections, confirm the campus and choose an active verified term.
4. Select a modality or time preference if desired.
5. Click **Prepare search**.
6. Confirm the result says live sections are not currently available in the app.
7. Confirm it shows an institution, term, subject, and course-number checklist.
8. Confirm it says no live seat availability is claimed.
9. Click **Open CUNY Global Search** and use the checklist on the official page.

Expected result: the official search opens, the checklist remains useful, and the app never labels a section or seat as available.

## Student Test - Keyboard and Status

1. Repeat the student test using Tab, Shift+Tab, Enter, and Space.
2. Confirm the chosen course is visible.
3. Activate **Prepare search** from the keyboard.
4. Confirm assistive technology receives the result update from the polite live region.

## Admin Test - Default Safe State

1. Sign in as an administrator.
2. Open **Schedule Data Settings**.
3. Locate **Official live-section provider**.
4. Confirm its initial state is not approved and not enabled.
5. Confirm the page explains why it is not ready.

## Admin Test - Reject Incomplete Enablement

1. Leave the API URL, data owner, permission reference, attribution, and support contact empty.
2. Choose approval status `pending` and select **Enable live provider**.
3. Click **Save provider governance**.

Expected result: saving is rejected and the missing safety requirements are listed.

## Admin Test - Record Governance Without Activation

1. Enter a provider name, owner, permission reference, attribution, support contact, and an HTTPS API URL supplied by the authorized data owner.
2. Leave **Enable live provider** unchecked.
3. Save and reload.

Expected result: the documentation is retained, but student searches continue to use the safe official-search handoff.

## Important Limitation

Do not use placeholder credentials or guess an endpoint to activate live data. Phase 8 is ready for an approved adapter, but live embedded sections require official documentation, permission, and implementation review.
