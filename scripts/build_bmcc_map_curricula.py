#!/usr/bin/env python3
"""Build reviewed 2025-2026 BMCC curriculum seed CSVs from extracted map rows.

This maintainer utility is intentionally not part of application startup.  It reads
the official consolidated BMCC map PDF supplied on the command line and writes the
missing curriculum CSV/source-note pairs using the repository's existing schema.
Programs with multiple official maps use the named representative map below and are
explicitly marked partial in their source notes because the current schema has no
track/concentration branch entity.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import OrderedDict
from pathlib import Path


PDF_URL = "https://www.dropbox.com/scl/fi/w1lycuqzbnnwihjdicd7r/2025-2026degreemapsrev110625.pdf?raw=1&rlkey=ovleo82ap162u43bq8u3x9zyy&st=jqa2q9gt"
COLUMNS = [
    "institution_code", "department", "department_code", "program_code",
    "program_name", "degree_type", "catalog_year", "group_name", "group_type",
    "required_credits", "display_order", "course_code", "title", "credits",
    "prerequisites", "alternatives", "choice_group_code", "source",
]

# zero-based PDF page, filename, and representative-map note
PROGRAMS = {
    "BUSM_AAS": (22, "busm_aas", "General Management specialization; four other official specialization maps remain documented, not merged"),
    "HIT_AAS": (73, "hit_aas", "single official two-year map"),
    "PAR_AAS": (120, "par_aas", "single official two-year map"),
    "RTH_AAS": (134, "rth_aas", "single official two-year map"),
    "AFH_AA": (8, "afh_aa", "single official two-year map"),
    "BCE_AA": (12, "bce_aa", "General concentration; Special Education map remains documented, not merged"),
    "CHED_AA": (30, "ched_aa", "General concentration; Special Education map remains documented, not merged"),
    "CYS_AA": (34, "cys_aa", "single official two-year map"),
    "CTJ_AA": (48, "ctj_aa", "single official two-year map"),
    "ETH_AA": (63, "eth_aa", "single map; its five areas of study remain a documented choice limitation"),
    "LA_AA": (79, "la_aa", "single official two-year map"),
    "LIN_AA": (83, "lin_aa", "General concentration; TESOL/Applied Linguistics map remains documented, not merged"),
    "LITST_AA": (87, "litst_aa", "single official two-year map"),
    "SESS_AA": (144, "sess_aa", "single official two-year map"),
    "FAA_AS": (2, "faa_as", "Statistics pathway; official Precalculus pathway is an alternative map"),
    "AFS_AS": (10, "afs_as", "single official two-year map"),
    "ECE_AS": (55, "ece_as", "Infant/Toddler specialization; Pre-School map remains documented, not merged"),
    "CHE_AS": (38, "che_as", "single official two-year map"),
    "ENT_AS": (146, "ent_as", "2025-2026 map title is Small Business Entrepreneurship"),
    "GIS_AS": (69, "gis_as", "single official two-year map"),
    "MSSE_AS": (91, "msse_as", "Biology specialization; Chemistry, Mathematics, and Physics maps remain documented, not merged"),
    "MUS_AS": (115, "mus_as", "Music Studies specialization; Jazz, Education, and Performance maps remain documented, not merged"),
    "PH_AS": (132, "ph_as", "single official two-year map"),
    "SHE_AS": (136, "she_as", "single official two-year map"),
    "THR_AS": (150, "thr_as", "single official two-year map"),
    "VAT_AS": (154, "vat_as", "single official two-year map"),
    # Certificate support already exists in the schema.  This is the only
    # additional missing certificate with a 2025-2026 map in the map book.
    "PN_CERT": (81, "pn_cert", "official 2025-2026 Licensed Practical Nursing certificate map"),
}

PLACEHOLDERS = {
    "world culture": ("FC-WORLD-CULTURES", "World Cultures and Global Issues", "FC_WORLD_CULTURES", "flexible_core"),
    "u.s. experience": ("FC-US-EXPERIENCE", "U.S. Experience in Its Diversity", "FC_US_EXPERIENCE", "flexible_core"),
    "us experience": ("FC-US-EXPERIENCE", "U.S. Experience in Its Diversity", "FC_US_EXPERIENCE", "flexible_core"),
    "individual and society": ("FC-INDIVIDUAL", "Individual and Society", "FC_INDIVIDUAL", "flexible_core"),
    "creative expression": ("FC-CREATIVE", "Creative Expression", "FC_CREATIVE", "flexible_core"),
    "life and physical": ("RC-LIFE-PHYSICAL", "Life and Physical Sciences", "RC_LIFE_PHYSICAL", "common_core"),
    "scientific world": ("FC-SCIENTIFIC-WORLD", "Scientific World", "FC_SCIENTIFIC_WORLD", "flexible_core"),
    "modern language": ("MODERN-LANGUAGE", "Modern Language Requirement", "BMCC_MODERN_LANGUAGE_CONTINUATION", "program_elective"),
    "liberal arts elective": ("LIBERAL-ARTS-ELECTIVE", "Liberal Arts Elective", "BMCC_LIBERAL_ARTS_ELECTIVE", "program_elective"),
    "general elective": ("GENERAL-ELECTIVE", "General Elective", "BMCC_GENERAL_ELECTIVE", "program_elective"),
}

PREREQUISITES = {
    "FAA_AS": {"ACC 222": "ACC 122", "ACC 330": "ACC 222", "ACC 360": "ACC 222", "ACC 370": "ACC 222", "ACC 430": "ACC 330"},
    "CYS_AA": {"PSY 250": "PSY 100", "SOC 250": "SOC 100"},
    "HIT_AAS": {
        "HIT 206": "HIT 110|HIT 111|HIT 112", "HIT 209": "HIT 110|HIT 111|HIT 112",
        "HIT 215": "HIT 110|HIT 111|HIT 112", "HIT 210": "HIT 206|HIT 209|HIT 215|BIO 426|CIS 100",
        "HIT 332": "HIT 110|HIT 111|HIT 112|HIT 206|HIT 209|HIT 215|HIT 210|BIO 426",
        "HIT 334": "HIT 210", "HIT 423": "HIT 332|HIT 334|CIS 207",
    },
    "RTH_AAS": {
        "BIO 425": "CHE 121", "RTT 201": "RTT 100|RTT 101|CHE 121", "RTT 202": "RTT 100|RTT 101|CHE 121",
        "BIO 426": "BIO 425", "RTT 210": "RTT 201|RTT 202", "RTT 301": "RTT 210|BIO 426",
        "RTT 302": "RTT 210|BIO 426", "RTT 310": "RTT 202|BIO 426", "RTT 320": "RTT 202|BIO 426|MAT 109",
        "RTT 401": "RTT 301|RTT 302|RTT 310|RTT 320", "RTT 403": "RTT 301|RTT 302|RTT 310|RTT 320",
        "RTT 410": "RTT 301|RTT 302|RTT 310|RTT 320", "BIO 420": "BIO 426",
    },
    "ENT_AS": {"BUS 150": "SPE 100|ENG 101|ENG 201", "BUS 210": "MAT 150", "MAR 320": "MAR 100", "SBE 201": "BUS 104|ECO 201", "SBE 400": "BUS 104|SBE 100"},
    "PH_AS": {"HSD 290": "HSD 110|HSD 280", "HSD 295": "HSD 110|HSD 280", "HSD 296": "HSD 110|HSD 280|MAT 150"},
    "THR_AS": {"THE 210": "THE 110", "THE 220": "THE 125 or THE 126 or THE 127 or THE 128", "THE 300": "ENG 201"},
    "VAT_AS": {"COM 240": "SPE 100"},
}


def _course_rows(page):
    text = page.extract_text() or ""
    columns = 3 if "YEAR 3" in text else 2
    rows = []
    for index in range(columns):
        left, right = page.width * index / columns, page.width * (index + 1) / columns
        block = page.crop((left, 105, right, page.height - 82)).extract_text(x_tolerance=2, y_tolerance=3) or ""
        block = block.split("FOOTNOTES", 1)[0]
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        course_re = re.compile(r"^(?P<code>(?:[A-Z]{2,4}|XXX)\s+(?:\d{2,3}(?:\.5)?|[0-9Xx]{1,3}|xxx))\s+(?P<title>.*)$")
        credit_re = re.compile(r"^(\d+)\s+CREDIT")
        pos = 0
        while pos < len(lines):
            match = course_re.match(lines[pos])
            if not match:
                pos += 1
                continue
            title, cursor = match.group("title"), pos + 1
            while cursor < len(lines) and not credit_re.match(lines[cursor]) and not course_re.match(lines[cursor]) and not lines[cursor].startswith(("SEMESTER", "SUMMER", "WINTER", "TOTAL", "YEAR")):
                title += " " + lines[cursor]
                cursor += 1
            if cursor < len(lines) and (credit := credit_re.match(lines[cursor])):
                title = re.sub(r"\s*\d+(?:\s*,\s*\d+)*\s*$", "", title).strip()
                rows.append([match.group("code").upper(), title, int(credit.group(1))])
                pos = cursor + 1
            else:
                pos += 1
    return rows


def _placeholder(title, program_code, ordinal):
    lowered = title.lower()
    for needle, values in PLACEHOLDERS.items():
        if needle in lowered:
            return values
    slug = re.sub(r"[^A-Z0-9]+", "-", title.upper()).strip("-")[:34]
    return f"{program_code}-{slug}-{ordinal}", title, "BMCC_GENERAL_ELECTIVE", "program_elective"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    args = parser.parse_args()
    try:
        import pdfplumber
    except ImportError as exc:
        raise SystemExit("This maintainer utility requires pdfplumber; application runtime does not.") from exc

    programs = {row["program_code"]: row for row in csv.DictReader((args.docs / "programs.csv").open(encoding="utf-8-sig")) if row["institution_code"] == "BMCC"}
    departments = {row["department_code"]: row["department_name"] for row in csv.DictReader((args.docs / "departments.csv").open(encoding="utf-8-sig")) if row["institution_code"] == "BMCC"}
    with pdfplumber.open(args.pdf) as pdf:
        for program_code, (page_index, stem, variant_note) in PROGRAMS.items():
            identity = programs[program_code]
            page = pdf.pages[page_index]
            page_text = page.extract_text() or ""
            total_match = re.search(r"TOTAL:\s*(\d+)\s+CREDITS", page_text)
            official_total = int(total_match.group(1)) if total_match else sum(row[2] for row in _course_rows(page))
            extracted = _course_rows(page)

            # Collapse repeated open-category placeholders into one credit requirement.
            normalized = OrderedDict()
            placeholder_ordinal = 0
            for code, title, credits in extracted:
                is_placeholder = "X" in code.upper()
                if is_placeholder:
                    placeholder_ordinal += 1
                    mapped_code, mapped_title, choice, group_type = _placeholder(title, program_code, placeholder_ordinal)
                    key = (mapped_code, mapped_title, choice, group_type)
                    normalized[key] = normalized.get(key, 0) + credits
                else:
                    normalized[(code, title, "", "named")] = credits

            groups = OrderedDict()
            for (code, title, choice, kind), credits in normalized.items():
                if kind != "named":
                    group_name = title
                    group_type = kind
                elif code in {"ENG 101", "ENG 100.5"}:
                    group_name, group_type = "Required Common Core - English Composition", "common_core"
                elif code in {"ENG 201", "SPE 100", "SPE 102"}:
                    group_name, group_type = "Flexible Core and Communication", "flexible_core"
                elif code.startswith("MAT ") and not any(k.startswith("MAT ") for k, *_ in [item[0] for item in groups.values()]):
                    group_name, group_type = "Required Common Core - Mathematical and Quantitative Reasoning", "common_core"
                else:
                    group_name, group_type = "Program Requirements", "program_required"
                groups.setdefault((group_name, group_type), []).append((code, title, credits, choice))

            output_rows = []
            order = {"common_core": 10, "flexible_core": 20, "program_required": 30, "program_elective": 40}
            for (group_name, group_type), entries in groups.items():
                required = sum(entry[2] for entry in entries)
                for code, title, credits, choice in entries:
                    output_rows.append({
                        "institution_code": "BMCC", "department": departments[identity["department_code"]],
                        "department_code": identity["department_code"], "program_code": program_code,
                        "program_name": identity["program_name"], "degree_type": identity["degree_type"],
                        "catalog_year": "2025-2026", "group_name": group_name, "group_type": group_type,
                        "required_credits": required, "display_order": order[group_type], "course_code": code,
                        "title": title, "credits": credits,
                        "prerequisites": PREREQUISITES.get(program_code, {}).get(code, ""), "alternatives": "",
                        "choice_group_code": choice, "source": PDF_URL,
                    })

            # The VAT map names ANI 301 as a finite alternative and the same
            # cross-listed course already has an official title in AMG_AS.
            # Keep it visible instead of hiding every option behind the broad
            # fallback selector used for choices whose titles are not on-map.
            if program_code == "VAT_AS":
                output_rows.append({
                    "institution_code": "BMCC", "department": departments[identity["department_code"]],
                    "department_code": identity["department_code"], "program_code": program_code,
                    "program_name": identity["program_name"], "degree_type": identity["degree_type"],
                    "catalog_year": "2025-2026", "group_name": "VAT Program Elective",
                    "group_type": "program_elective", "required_credits": 3, "display_order": 40,
                    "course_code": "ANI 301", "title": "Introduction to Motion Graphics and Visual Effects",
                    "credits": 3, "prerequisites": "VAT 161 or VAT 171 or MMA 100 or MMP 100",
                    "alternatives": "", "choice_group_code": "", "source": PDF_URL,
                })

            csv_path = args.docs / f"{stem}_courses.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=COLUMNS)
                writer.writeheader(); writer.writerows(output_rows)

            footnotes = page_text.split("FOOTNOTES", 1)[1].strip() if "FOOTNOTES" in page_text else "No separate footnote block was extracted."
            status = "Partial" if any(token in variant_note for token in ("remain", "areas of study", "alternative map")) else "Needs Review"
            notes = f"""# {identity['program_name']} ({identity['degree_type']}) — 2025–2026 sources\n\n- Official source: [{page_text.splitlines()[0]}]({PDF_URL}), PDF page {page_index + 1}\n- Official map total: **{official_total} credits**\n- Imported map variant: {variant_note}.\n- Tree status: **{status}**.\n- Accessed: 2026-10-29.\n\n## Representation notes\n\nThe CSV transcribes the courses and credit-bearing open categories printed on the selected official two-year map. Named prerequisites that the current schema can express are included where reviewed. Corequisites, term-only availability, permissions, minimum grades, repeated-course rules, and specialization branches cannot be represented by the current schema and remain in the official footnotes below. Program-specific open elective pools use the existing broad selector only as a visible selection mechanism and require advisor verification.\n\n## Official footnotes (verbatim extraction)\n\n```text\n{footnotes}\n```\n"""
            (args.docs / f"{stem}_sources.md").write_text(notes, encoding="utf-8")
            print(f"Wrote {csv_path}: {len(output_rows)} rows, {official_total} official credits, status {status}")


if __name__ == "__main__":
    main()
