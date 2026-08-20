"""Deterministic, explainable matching for reviewed CUNY Beyond mappings."""

from __future__ import annotations

import os
import re
from typing import Iterable


DEFAULT_SKILL_POINTS = 6
DEFAULT_MINIMUM_SCORE = 38


def normalize_phrase(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def configured_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return min(max(value, minimum), maximum)


def skill_points() -> int:
    return configured_int("CUNY_BEYOND_SKILL_POINTS", DEFAULT_SKILL_POINTS, 0, 20)


def minimum_score() -> int:
    return configured_int("CUNY_BEYOND_MINIMUM_SCORE", DEFAULT_MINIMUM_SCORE, 0, 100)


def resolve_career(goal: str, careers: Iterable[dict]) -> dict | None:
    normalized_goal = normalize_phrase(goal)
    if not normalized_goal:
        return None

    ranked = []
    for career in careers:
        terms = [career.get("name", ""), *(career.get("aliases") or [])]
        normalized_terms = {normalize_phrase(term) for term in terms if normalize_phrase(term)}
        exact = normalized_goal in normalized_terms
        contained = max((len(term) for term in normalized_terms if term in normalized_goal), default=0)
        reverse = max((len(normalized_goal) for term in normalized_terms if normalized_goal in term), default=0)
        if exact or contained or reverse:
            ranked.append((1 if exact else 0, contained, reverse, career.get("name", ""), career))
    return max(ranked, default=(0, 0, 0, "", None))[-1]


def rank_program_matches(mappings: Iterable[dict], selected_skills: Iterable[str], limit: int = 3) -> list[dict]:
    selected = {normalize_phrase(skill) for skill in selected_skills if normalize_phrase(skill)}
    per_skill = skill_points()
    threshold = minimum_score()
    results = []

    for mapping in mappings:
        if not mapping.get("has_curriculum"):
            continue
        career_skills = mapping.get("career_skills") or []
        matched_skills = [skill for skill in career_skills if normalize_phrase(skill) in selected]
        career_score = int(mapping.get("career_points", 50))
        skill_score = len(matched_skills) * per_skill
        total = career_score + skill_score
        if total < threshold:
            continue
        result = dict(mapping)
        result.update({
            "score": total,
            "score_components": {"career": career_score, "skills": skill_score},
            "matched_skills": matched_skills,
            "advising_label": "Strong starting point" if total >= 50 else "Explore with an advisor",
        })
        results.append(result)

    results.sort(key=lambda item: (-item["score"], item.get("program_name", ""), item.get("program_code", "")))
    return results[: max(1, min(limit, 3))]
