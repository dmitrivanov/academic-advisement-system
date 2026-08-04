# Contributing

Thank you for contributing to the Academic Advisement System. All contributions are
reviewed before they become part of the deployed application.

## Access and safety rules

- Work in your own GitHub fork.
- Never push directly to the upstream `main` branch.
- Never push to the professor's repository or configure its remote locally.
- Never commit credentials, API keys, `.env` files, databases, or student data.
- Do not modify Render settings or production environment variables.
- Do not change curriculum requirements without an identified official source and
  explicit approval in the issue.
- Keep each pull request limited to one assigned issue.

Curriculum-data contributors must also follow
[CURRICULUM_DATA_GUIDE.md](CURRICULUM_DATA_GUIDE.md), start from the canonical CSV
template, cite official sources, and run the curriculum validator before seeding.

## One-time setup

1. Fork `dmitrivanov/academic-advisement-system` on GitHub.
2. Clone your fork and connect the original repository as `upstream`:

```bash
git clone https://github.com/YOUR_USERNAME/academic-advisement-system.git
cd academic-advisement-system
git remote add upstream https://github.com/dmitrivanov/academic-advisement-system.git
git remote -v
```

3. Follow the detailed local installation instructions in [README.md](README.md).

Expected remotes:

```text
origin    https://github.com/YOUR_USERNAME/academic-advisement-system.git
upstream  https://github.com/dmitrivanov/academic-advisement-system.git
```

## Workflow for every task

### 1. Read and claim the issue

Read the goal, acceptance criteria, testing instructions, and out-of-scope section.
Ask questions on the issue before implementing unclear requirements.

### 2. Start from the newest upstream `main`

Replace `12` and the description with the assigned issue number and short name:

```bash
git fetch upstream
git switch -c intern/issue-12-login-accessibility upstream/main
```

Use a new branch for every issue. Do not reuse an old pull-request branch.

### 3. Make a focused change

Run the application locally and check the relevant screen. Avoid formatting or
reorganizing unrelated files.

Before committing, inspect exactly what changed:

```bash
git status
git diff
```

### 4. Test locally

Follow the issue's test steps. At minimum:

```bash
python3 scripts/validate_curriculum_csv.py path/to/new_major_courses.csv
python3 seed_database.py
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

The validator command applies to curriculum-data changes. Other tasks may omit it.

Open the affected page, verify the requested behavior, and ensure the terminal does
not show a new error. Do not reseed or test against the production database.

### 5. Commit and push to your fork

Stage only files related to the issue:

```bash
git add path/to/changed-file
git commit -m "Improve login form accessibility"
git push -u origin intern/issue-12-login-accessibility
```

Do not use `git add .` until you have carefully checked `git status`.

### 6. Open a draft pull request

On GitHub, open a pull request with:

- Base repository: `dmitrivanov/academic-advisement-system`
- Base branch: `main`
- Head repository: your fork
- Compare branch: your task branch

Open it as a **Draft pull request** while work is in progress. Include `Closes #12`
in the description, complete the checklist, and add screenshots for visual changes.
Mark it ready for review only after local testing is complete.

### 7. Respond to review

Make requested corrections on the same branch, commit them, and push again. The pull
request updates automatically. Do not open a second pull request for review fixes.

Only a maintainer merges the pull request.

## Keeping a branch current

If the maintainer asks you to update a branch:

```bash
git fetch upstream
git rebase upstream/main
git push --force-with-lease
```

Use `--force-with-lease`, never plain `--force`. Ask for help if the rebase reports
conflicts.

## Pull-request quality checklist

- The change satisfies every acceptance criterion.
- Only issue-related files changed.
- No secret, local database, log, or generated cache was committed.
- The application starts locally.
- Relevant manual tests passed.
- Visual changes include before/after screenshots.
- Curriculum or equivalency changes cite an official source.
- The pull request links its issue.
