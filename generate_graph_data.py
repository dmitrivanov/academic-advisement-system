#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 17:57:56 2026

@author: dmitriiivanov
"""

import csv
import json
from pathlib import Path


MAJOR_FILES = {
    "CS": {
        "name": "Computer Science",
        "file": "docs/cs_courses.csv",
    },
    "CIS": {
        "name": "Computer Information Systems",
        "file": "docs/cis_courses.csv",
    },
    "CNT": {
        "name": "Computer Network Technology",
        "file": "docs/cnt_courses.csv",
    },
}

OUTPUT_FILE = Path("frontend/major_graph_data.js")


def parse_prereqs(value):
    """
    Supports:
    - empty prereqs
    - CSC 101
    - CIS 385|CSC 210
    - CSC 110 or CSC 111
    """
    if not value:
        return []

    value = value.strip()
    if not value:
        return []

    prereqs = []

    for part in value.split("|"):
        part = part.strip()

        if " or " in part:
            options = [x.strip() for x in part.split(" or ") if x.strip()]
            prereqs.append(options)
        else:
            prereqs.append(part)

    return prereqs


def prereq_options(prereq):
    if isinstance(prereq, list):
        return prereq
    return [prereq]


def course_dependency_depth(code, courses, memo, visiting):
    """
    Computes hierarchy depth automatically.
    Courses with no prereqs = level 0.
    Courses depending on level 0 = level 1, etc.
    """
    if code in memo:
        return memo[code]

    if code in visiting:
        return 0

    visiting.add(code)

    prereqs = courses[code]["prereqs"]

    if not prereqs:
        memo[code] = 0
        visiting.remove(code)
        return 0

    max_depth = 0

    for prereq in prereqs:
        options = prereq_options(prereq)

        option_depths = []
        for option in options:
            if option in courses:
                option_depths.append(course_dependency_depth(option, courses, memo, visiting))
            else:
                option_depths.append(0)

        # For OR prereqs, use easiest/earliest option
        max_depth = max(max_depth, min(option_depths))

    memo[code] = max_depth + 1
    visiting.remove(code)
    return memo[code]


def build_layout(courses):
    memo = {}

    for code in courses:
        course_dependency_depth(code, courses, memo, set())

    max_level = max(memo.values()) if memo else 0
    layout = [[] for _ in range(max_level + 1)]

    for code, level in sorted(memo.items(), key=lambda x: (x[1], x[0])):
        layout[level].append(code)

    return layout


def load_major(csv_path):
    courses = {}

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            code = row["code"].strip()
            title = row["title"].strip()
            credits = int(row["credits"])
            prerequisites = parse_prereqs(row.get("prerequisites", ""))
            alternatives = parse_prereqs(row.get("alternatives", ""))

            courses[code] = {
                "title": title,
                "credits": credits,
                "prereqs": prerequisites,
                "alternatives": alternatives,
            }

    layout = build_layout(courses)

    return {
        "courses": courses,
        "layout": layout,
    }


def main():
    all_data = {}

    for major_code, info in MAJOR_FILES.items():
        csv_path = Path(info["file"])

        if not csv_path.exists():
            print(f"Skipping {major_code}: file not found {csv_path}")
            continue

        major_data = load_major(csv_path)
        major_data["name"] = info["name"]

        all_data[major_code] = major_data

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    js = "const MAJORS = "
    js += json.dumps(all_data, indent=2)
    js += ";\n"

    OUTPUT_FILE.write_text(js, encoding="utf-8")

    print(f"Generated: {OUTPUT_FILE}")
    print(f"Majors included: {', '.join(all_data.keys())}")


if __name__ == "__main__":
    main()