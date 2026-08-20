# CUNY Beyond Phase 6 Progress: Advising Referral and Exports

**Technical implementation record - August 21, 2026**

## Outcome

Phase 6 creates a concise pre-advisement package that a prospective student can review and download without creating an account. The student may optionally provide contact information at the final referral step, give explicit consent, and send the package when an approved SMTP destination is configured. If automatic email is unavailable, the system preserves the summary and provides a copyable subject/body plus the official BMCC Advisement link.

## Summary architecture

The public intake stores a short-lived referral summary in browser session storage after reviewed program and CPL results are produced. It combines:

- Student pathway and career goal
- Matched career and no more than five selected skills
- Up to three reviewed BMCC program recommendations
- Possible CPL conversations and official next steps
- Completed-course snapshot when one exists
- Transfer-planning prompts for advisor review
- Latest Phase 5 schedule-search checklist when one exists
- Human-readable source links and a nonbinding disclaimer

The referral page reads this browser-local package. It does not require login and does not ask for a name, email, or ID during career exploration.

## Exports

The page uses the application’s existing print-to-PDF approach: **Save / Print PDF** opens the browser print interface with a clean, print-specific layout. A plain-text download is also available as a resilient fallback and for accessibility or easy copying.

## Referral workflow

The final form asks for a name and email. Last four ID digits are optional and must be exactly four digits when entered. A required checkbox explains the sharing purpose and logging behavior. A hidden honeypot rejects basic automated submissions.

The backend accepts only a whitelisted, bounded subset of the browser summary. It removes unknown keys and limits skills, programs, CPL items, completed courses, and checklist lines. It prepares a structured plain-text email without attachments.

Automatic delivery is disabled by default. It activates only when `BMCC_ADVISING_REFERRAL_ENABLED=true`, `BMCC_ADVISING_REFERRAL_EMAIL`, and an SMTP host are configured. When enabled, the advising destination receives the message and the student is copied. The system does not send anything before explicit consent.

## Failure handling

When SMTP is absent or delivery fails, the student receives:

- A stable reference/event ID
- The saved/printable summary
- A copyable email subject and body
- A downloadable text summary
- The official BMCC Academic Advisement page

The delivery log records only event ID, timestamp, status, and delivery mode. It does not log the student’s name, email, ID digits, summary, career goal, skills, courses, or answers.

## Security and privacy decisions

- Contact information is collected only on the referral page.
- Consent is machine-enforced.
- No referral email contains an attachment.
- Public inputs are length-bounded and structurally whitelisted.
- Optional ID digits are not required for a summary or fallback.
- Automatic delivery fails safely to a student-controlled copy/download workflow.
- The summary expires with the existing browser-session planning context.

## Validation

Tests cover summary whitelisting and bounds, manual delivery fallback, consent fields, public no-login routing, optional last-four behavior, non-PII logging, export controls, and context carried from career, CPL, coursework, transfer, and schedule phases. Existing curriculum and advising tests remain part of the full regression run.

## Official next step

BMCC Academic Advisement: https://www.bmcc.cuny.edu/academics/advisement/advisement/

