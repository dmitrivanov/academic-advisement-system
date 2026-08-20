"""Provider-neutral, non-scraping schedule-search handoff helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict


GLOBAL_SEARCH_URL = "https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController"

INSTITUTION_LABELS = {
    "BMCC": "Borough of Manhattan CC",
    "BC": "Brooklyn College",
    "CCNY": "City College",
    "JJAY": "John Jay College",
}

COURSE_CODE = re.compile(r"^\s*([A-Za-z]{2,8})\s*[- ]?\s*(\d+(?:\.\d+)?[A-Za-z]?)\s*$")


@dataclass(frozen=True)
class CourseParts:
    display_code: str
    subject: str
    catalog_number: str


def parse_course_code(value: str) -> CourseParts:
    match = COURSE_CODE.fullmatch(value or "")
    if not match:
        raise ValueError("Course code must contain a subject and catalog number, such as MAT 301 or MAT 157.5")
    subject, catalog = match.groups()
    subject = subject.upper()
    catalog = catalog.upper()
    return CourseParts(f"{subject} {catalog}", subject, catalog)


def build_global_search_handoff(institution_code: str, term, course_code: str, modality=None, time_preference=None):
    institution_label = INSTITUTION_LABELS.get((institution_code or "").upper())
    if not institution_label:
        raise ValueError(f"No reviewed Global Search institution mapping for {institution_code}")
    course = parse_course_code(course_code)
    instructions = [
        f"Select institution: {institution_label}",
        f"Select term: {term.name}",
        f"Select subject: {course.subject}",
        f"Enter course number: {course.catalog_number}",
    ]
    if modality:
        instructions.append(f"Apply instruction mode preference: {modality}")
    if time_preference:
        instructions.append(f"Apply time preference: {time_preference}")
    return {
        "provider": "CUNY Global Search",
        "url": GLOBAL_SEARCH_URL,
        "prefilled": False,
        "institution_code": institution_code.upper(),
        "institution_label": institution_label,
        "term": {"name": term.name, "provider_code": term.provider_code},
        "course": asdict(course),
        "instructions": instructions,
        "last_verified_at": term.verified_at.date().isoformat(),
        "disclaimer": "Global Search is for finding sections. Register in CUNYfirst. Seats, prerequisites, holds, permissions, and eligibility can change.",
    }

