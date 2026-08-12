import re


def normalized_program_identity(program):
    normalize = lambda value: " ".join(str(value or "").split()).casefold()
    return (
        normalize(program["institution_code"]),
        normalize(program["name"]),
        normalize(program["degree_type"]),
    )


def catalog_year_rank(value):
    normalized = str(value or "").strip().replace("–", "-").replace("—", "-")
    match = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{2}|\d{4}))?", normalized)
    if not match:
        return (0, 0, 0, 0, normalized.casefold())

    start = int(match.group(1))
    end_text = match.group(2)
    if end_text is None:
        end = start
        single_year = 1
    elif len(end_text) == 2:
        end = (start // 100) * 100 + int(end_text)
        single_year = 0
    else:
        end = int(end_text)
        single_year = 0

    # A single-year catalog wins an exact ending-year tie (2026 over
    # 2025-2026), followed by the normalized string and database ID.
    return (1, end, start, single_year, normalized.casefold())


def canonical_selector_programs(programs):
    winners = {}
    for program in programs:
        identity = normalized_program_identity(program)
        rank = (
            int(bool(program.get("has_curriculum"))),
            *catalog_year_rank(program.get("catalog_year")),
            int(program.get("id") or 0),
        )
        current = winners.get(identity)
        if current is None or rank > current[0]:
            winners[identity] = (rank, program)

    return sorted(
        (item[1] for item in winners.values()),
        key=lambda program: (
            str(program.get("institution") or "").casefold(),
            str(program.get("name") or "").casefold(),
            str(program.get("degree_type") or "").casefold(),
            int(program.get("id") or 0),
        ),
    )
