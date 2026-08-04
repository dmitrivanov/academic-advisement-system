#!/usr/bin/env python3
"""Validate curriculum CSV files before they are used by seed_database.py."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CANONICAL_COLUMNS = [
    "institution_code",
    "department",
    "department_code",
    "program_code",
    "program_name",
    "degree_type",
    "catalog_year",
    "group_name",
    "group_type",
    "required_credits",
    "display_order",
    "course_code",
    "title",
    "credits",
    "prerequisites",
    "alternatives",
    "choice_group_code",
    "source",
]

REQUIRED_COLUMNS = {
    "program_code",
    "program_name",
    "catalog_year",
    "group_name",
    "group_type",
    "required_credits",
    "course_code",
    "title",
    "credits",
    "prerequisites",
    "alternatives",
    "choice_group_code",
}

REQUIRED_ROW_VALUES = {
    "institution_code",
    "department",
    "department_code",
    "program_code",
    "program_name",
    "degree_type",
    "catalog_year",
    "group_name",
    "group_type",
    "required_credits",
    "display_order",
    "course_code",
    "title",
    "credits",
    "source",
}

ALLOWED_GROUP_TYPES = {
    "common_core",
    "flexible_core",
    "program_required",
    "program_elective",
}

ASSOCIATE_DEGREES = {"AA", "AS", "AAS"}
CODE_PATTERN = re.compile(r"^[A-Z0-9]+(?:[ _.-][A-Z0-9]+)*$")
CATALOG_YEAR_PATTERN = re.compile(r"^\d{4}(?:-\d{2,4})?$")
URL_PATTERN = re.compile(r"^https://", re.IGNORECASE)
NON_MAJOR_COURSE_FILES = {"pathways_courses.csv"}


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str
    row: int | None = None

    def format(self, path: Path) -> str:
        location = f"{path}:{self.row}" if self.row else str(path)
        return f"{self.severity.upper():7} {location} — {self.message}"


@dataclass
class ValidationResult:
    path: Path
    findings: list[Finding]
    row_count: int = 0

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "warning"]


def clean(value: str | None) -> str:
    return (value or "").strip()


def parse_number(value: str, *, integer: bool = False) -> float | int | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number < 0:
        return None
    if integer and not number.is_integer():
        return None
    return int(number) if integer else number


def relationship_codes(value: str) -> list[str]:
    """Return referenced codes from the seeder's `|` and ` or ` syntax."""
    if not clean(value):
        return []

    codes: list[str] = []
    for required_part in value.split("|"):
        part = clean(required_part)
        if not part:
            continue
        options = re.split(r"\s+or\s+", part, flags=re.IGNORECASE)
        codes.extend(clean(option) for option in options if clean(option))
    return codes


def load_reference_course_codes(docs_dir: Path, exclude: Path) -> set[str]:
    codes: set[str] = set()
    for candidate in docs_dir.glob("*_courses.csv"):
        if candidate.resolve() == exclude.resolve():
            continue
        try:
            with candidate.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    code = clean(row.get("course_code") or row.get("code")).upper()
                    if code:
                        codes.add(code)
        except (OSError, csv.Error):
            continue
    return codes


def validate_legacy_rows(path: Path, headers: list[str], rows: list[dict]) -> ValidationResult:
    findings = [Finding(
        "warning",
        "Legacy course-list schema detected. Existing files are supported, but new majors must use the full contributor template.",
    )]
    result = ValidationResult(path=path, findings=findings, row_count=len(rows))
    required = {"code", "title", "credits"}
    missing = sorted(required - set(headers))
    if missing:
        findings.append(Finding("error", f"Missing legacy column(s): {', '.join(missing)}."))
        return result
    if not rows:
        findings.append(Finding("error", "CSV contains no curriculum rows."))
        return result

    seen: dict[str, int] = {}
    for index, raw_row in enumerate(rows, start=2):
        row = {key: clean(value) for key, value in raw_row.items() if key is not None}
        for field in required:
            if not row.get(field):
                findings.append(Finding("error", f"Required value `{field}` is blank.", index))

        code = row.get("code", "")
        if code and code != code.upper():
            findings.append(Finding("error", f"`code` must be uppercase: {code}.", index))
        if code and not CODE_PATTERN.fullmatch(code):
            findings.append(Finding("error", f"`code` contains unsupported characters: {code}.", index))
        if code in seen:
            findings.append(Finding("error", f"Duplicate course `{code}`; first listed on row {seen[code]}.", index))
        elif code:
            seen[code] = index

        credits = parse_number(row.get("credits", ""), integer=True)
        if credits is None or credits <= 0:
            findings.append(Finding("error", "`credits` must be a whole number greater than zero.", index))

        for field in ("prerequisites", "alternatives"):
            value = row.get(field, "")
            if "||" in value or value.startswith("|") or value.endswith("|"):
                findings.append(Finding("error", f"Malformed `{field}` relationship syntax: {value}.", index))

    return result


def validate_file(path: Path, *, docs_dir: Path | None = None) -> ValidationResult:
    findings: list[Finding] = []
    result = ValidationResult(path=path, findings=findings)

    if not path.exists():
        findings.append(Finding("error", "File does not exist."))
        return result

    if path.suffix.lower() != ".csv":
        findings.append(Finding("error", "Curriculum file must use the .csv extension."))
        return result

    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            rows = list(reader)
    except UnicodeDecodeError:
        findings.append(Finding("error", "File must be UTF-8 encoded."))
        return result
    except (OSError, csv.Error) as exc:
        findings.append(Finding("error", f"Could not read CSV: {exc}"))
        return result

    result.row_count = len(rows)

    if not headers:
        findings.append(Finding("error", "CSV header is missing."))
        return result

    duplicate_headers = sorted({name for name in headers if headers.count(name) > 1})
    if duplicate_headers:
        findings.append(Finding("error", f"Duplicate header(s): {', '.join(duplicate_headers)}."))

    missing_required = sorted(REQUIRED_COLUMNS - set(headers))
    if missing_required:
        if {"code", "title", "credits"}.issubset(headers):
            return validate_legacy_rows(path, headers, rows)
        findings.append(Finding("error", f"Missing required column(s): {', '.join(missing_required)}."))
        return result

    missing_canonical = [name for name in CANONICAL_COLUMNS if name not in headers]
    if missing_canonical:
        findings.append(Finding(
            "warning",
            "Not using the full contributor schema; missing: " + ", ".join(missing_canonical) + ".",
        ))
    elif headers != CANONICAL_COLUMNS:
        findings.append(Finding("warning", "Columns are not in the canonical template order."))

    unexpected = sorted(set(headers) - set(CANONICAL_COLUMNS))
    if unexpected:
        findings.append(Finding("warning", f"Unexpected column(s) are ignored by the seeder: {', '.join(unexpected)}."))

    if not rows:
        findings.append(Finding("error", "CSV contains no curriculum rows."))
        return result

    known_external_codes = load_reference_course_codes(docs_dir or path.parent, path)
    program_values: dict[str, set[str]] = {
        field: set()
        for field in (
            "institution_code",
            "department",
            "department_code",
            "program_code",
            "program_name",
            "degree_type",
            "catalog_year",
        )
    }
    course_rows: dict[str, int] = {}
    local_course_codes: set[str] = set()
    relationships: list[tuple[int, str, str, str]] = []
    group_metadata: dict[str, tuple[str, str, str]] = {}
    group_rows: dict[str, list[tuple[str, float, str]]] = {}
    non_url_source_rows: list[int] = []

    for index, raw_row in enumerate(rows, start=2):
        row = {key: clean(value) for key, value in raw_row.items() if key is not None}

        if None in raw_row:
            findings.append(Finding("error", "Row has more fields than the header.", index))

        for field in REQUIRED_ROW_VALUES:
            if field in headers and not row.get(field):
                findings.append(Finding("error", f"Required value `{field}` is blank.", index))

        for field in program_values:
            if row.get(field):
                program_values[field].add(row[field])

        for field in ("institution_code", "department_code", "program_code", "course_code"):
            value = row.get(field, "")
            if value and value != value.upper():
                findings.append(Finding("error", f"`{field}` must be uppercase: {value}.", index))
            if value and not CODE_PATTERN.fullmatch(value):
                findings.append(Finding("error", f"`{field}` contains unsupported characters: {value}.", index))

        catalog_year = row.get("catalog_year", "")
        if catalog_year and not CATALOG_YEAR_PATTERN.fullmatch(catalog_year):
            findings.append(Finding(
                "error",
                "`catalog_year` must look like 2026, 2025-2026, or 2025-26.",
                index,
            ))

        group_type = row.get("group_type", "")
        if group_type and group_type not in ALLOWED_GROUP_TYPES:
            findings.append(Finding(
                "error",
                f"Unsupported group_type `{group_type}`; use one of {', '.join(sorted(ALLOWED_GROUP_TYPES))}.",
                index,
            ))

        credits = parse_number(row.get("credits", ""), integer=True)
        if credits is None or credits <= 0:
            findings.append(Finding("error", "`credits` must be a whole number greater than zero.", index))

        required_credits = parse_number(row.get("required_credits", ""), integer=True)
        if required_credits is None or required_credits <= 0:
            findings.append(Finding("error", "`required_credits` must be a whole number greater than zero.", index))

        display_order = row.get("display_order", "")
        if "display_order" in headers and display_order and parse_number(display_order, integer=True) is None:
            findings.append(Finding("error", "`display_order` must be a non-negative whole number.", index))

        source = row.get("source", "")
        if "source" in headers and source and not URL_PATTERN.match(source):
            non_url_source_rows.append(index)

        code = row.get("course_code", "").upper()
        if code:
            if code in course_rows:
                findings.append(Finding(
                    "error",
                    f"Duplicate course `{code}`; first listed on row {course_rows[code]}.",
                    index,
                ))
            else:
                course_rows[code] = index
                local_course_codes.add(code)

        group_name = row.get("group_name", "")
        if group_name:
            metadata = (
                group_type,
                row.get("required_credits", ""),
                row.get("display_order", ""),
            )
            previous = group_metadata.get(group_name)
            if previous and previous != metadata:
                findings.append(Finding(
                    "error",
                    f"Group `{group_name}` has inconsistent type, required credits, or display order.",
                    index,
                ))
            group_metadata.setdefault(group_name, metadata)
            if credits is not None:
                group_rows.setdefault(group_name, []).append(
                    (code, float(credits), row.get("choice_group_code", ""))
                )

        for field in ("prerequisites", "alternatives"):
            value = row.get(field, "")
            if value:
                if "||" in value or value.startswith("|") or value.endswith("|"):
                    findings.append(Finding("error", f"Malformed `{field}` relationship syntax: {value}.", index))
                if re.search(r"\bOR\b", value) and " or " not in value:
                    findings.append(Finding("warning", f"Use lowercase ` or ` in `{field}` for consistency.", index))
                for referenced_code in relationship_codes(value):
                    relationships.append((index, code, field, referenced_code.upper()))

    for field, values in program_values.items():
        if len(values) > 1:
            findings.append(Finding(
                "error",
                f"A curriculum file must describe one program; `{field}` has multiple values: {', '.join(sorted(values))}.",
            ))

    if non_url_source_rows:
        row_preview = ", ".join(str(row) for row in non_url_source_rows[:5])
        remaining = len(non_url_source_rows) - 5
        suffix = f" and {remaining} more" if remaining > 0 else ""
        findings.append(Finding(
            "warning",
            f"`source` should be a direct official HTTPS URL on row(s) {row_preview}{suffix}.",
        ))

    degree_type = next(iter(program_values["degree_type"]), "").upper()
    if degree_type and degree_type not in {"AA", "AS", "AAS", "BA", "BS", "BBA", "CERT"}:
        findings.append(Finding("warning", f"Unrecognized degree type `{degree_type}`; confirm it is intentional."))

    for row_number, course_code, field, referenced_code in relationships:
        if referenced_code == course_code:
            findings.append(Finding("error", f"Course `{course_code}` cannot reference itself in `{field}`.", row_number))
        elif referenced_code not in local_course_codes:
            location = "another current curriculum file" if referenced_code in known_external_codes else "no current curriculum file"
            findings.append(Finding(
                "warning",
                f"`{field}` references `{referenced_code}`, which is listed in {location}. Confirm students can satisfy this relationship in the progress UI.",
                row_number,
            ))

    for group_name, entries in group_rows.items():
        required = parse_number(group_metadata[group_name][1])
        if required is None:
            continue
        listed_credits = sum(item[1] for item in entries)
        if listed_credits < required:
            findings.append(Finding(
                "error",
                f"Group `{group_name}` lists {listed_credits:g} credits but requires {required:g}.",
            ))
        elif listed_credits > required:
            findings.append(Finding(
                "warning",
                f"Group `{group_name}` lists {listed_credits:g} credits but requires {required:g}. Confirm elective/choice logic does not make every option required.",
            ))

    unique_groups = {
        name: parse_number(metadata[1])
        for name, metadata in group_metadata.items()
    }
    published_total = sum(value for value in unique_groups.values() if value is not None)
    if degree_type in ASSOCIATE_DEGREES and published_total != 60:
        findings.append(Finding(
            "warning",
            f"Associate-degree group requirements total {published_total:g}, not 60 credits. Confirm the official program total and STEM-variant adjustments.",
        ))

    filename_program_code = path.stem.removesuffix("_courses").upper()
    actual_program_code = next(iter(program_values["program_code"]), "")
    if actual_program_code and filename_program_code != actual_program_code:
        findings.append(Finding(
            "warning",
            f"Filename implies program `{filename_program_code}`, but rows use `{actual_program_code}`. Prefer `{actual_program_code.lower()}_courses.csv`.",
        ))

    return result


def discover_paths(arguments: Iterable[str], all_files: bool, docs_dir: Path) -> list[Path]:
    paths = [Path(item) for item in arguments]
    if all_files:
        paths.extend(
            path for path in sorted(docs_dir.glob("*_courses.csv"))
            if path.name not in NON_MAJOR_COURSE_FILES
        )

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            unique.append(path)
            seen.add(resolved)
    return unique


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate curriculum CSV files before database seeding.",
    )
    parser.add_argument("files", nargs="*", help="One or more curriculum CSV files.")
    parser.add_argument("--all", action="store_true", help="Validate every docs/*_courses.csv file.")
    parser.add_argument("--docs-dir", default="docs", help="Curriculum directory used for --all and reference checks.")
    parser.add_argument("--strict", action="store_true", help="Return a failure status when warnings are present.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    docs_dir = Path(args.docs_dir)
    paths = discover_paths(args.files, args.all, docs_dir)

    if not paths:
        parser.error("Provide at least one CSV file or use --all.")

    total_errors = 0
    total_warnings = 0
    for path in paths:
        result = validate_file(path, docs_dir=docs_dir)
        for finding in result.findings:
            print(finding.format(path))
        total_errors += len(result.errors)
        total_warnings += len(result.warnings)
        if not result.findings:
            print(f"OK      {path} — {result.row_count} curriculum rows validated.")

    print(
        f"\nValidated {len(paths)} file(s): "
        f"{total_errors} error(s), {total_warnings} warning(s)."
    )
    return 1 if total_errors or (args.strict and total_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
