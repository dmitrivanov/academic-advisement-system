# Illustrated User Guides

This folder contains the editable Markdown sources and visual assets for the Academic Advisement System manuals.

## Guides

- [Student Guide](STUDENT_GUIDE.md) - detailed student workflow covering login, program selection, completed courses, Core choice groups, progress, degree planning, PDF export, AI advising, major changes, and transfer analysis.
- [Administrator Guide](ADMIN_GUIDE.md) - curriculum administration, Major Constructor, rules, Core adjustments, validation, publishing, equivalencies, AI settings, testing, and rollback.

## PDF editions

- [Student Guide PDF](../../output/pdf/academic_advisement_student_guide.pdf)
- [Administrator Guide PDF](../../output/pdf/academic_advisement_admin_guide.pdf)

## Rebuilding

Run from the repository root with the bundled dependencies installed:

```bash
python3 scripts/build_user_guides.py
```

The build script regenerates diagrams and writes the final PDFs under `output/pdf/`.
