import csv
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/careers", tags=["careers"])

ONET_BASE_URL = "https://api-v2.onetcenter.org"
DOCS_DIR = Path(__file__).resolve().parent / "docs"
CAREER_PATHWAYS_FILE = DOCS_DIR / "career_pathways.csv"

_CACHE_TTL_SECONDS = 60 * 60 * 12  # 12 hours
_detail_cache: dict[str, tuple[float, dict]] = {}
_detail_locks: dict[str, threading.Lock] = {}
_detail_locks_guard = threading.Lock()


def get_onet_api_key():
    return os.environ.get("ONET_API_KEY")


def load_career_pathways():
    if not CAREER_PATHWAYS_FILE.exists():
        return []
    with CAREER_PATHWAYS_FILE.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def careers_for_program(institution_code: str, program_code: str):
    rows = [
        row
        for row in load_career_pathways()
        if row["institution_code"].upper() == institution_code.upper()
        and row["program_code"].upper() == program_code.upper()
    ]
    rows.sort(key=lambda row: int(row["display_order"]))
    return rows


@router.get("/{institution_code}/{program_code}")
def list_careers(institution_code: str, program_code: str):
    rows = careers_for_program(institution_code, program_code)
    return {
        "institution_code": institution_code.upper(),
        "program_code": program_code.upper(),
        "onet_api_key_configured": bool(get_onet_api_key()),
        "careers": [
            {"onet_soc_code": row["onet_soc_code"], "title": row["occupation_title"]}
            for row in rows
        ],
    }


def _onet_get(path: str):
    api_key = get_onet_api_key()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="O*NET API key is not configured. Set the ONET_API_KEY environment variable.",
        )
    response = None
    for attempt in range(3):
        try:
            response = requests.get(
                f"{ONET_BASE_URL}{path}",
                headers={"X-API-Key": api_key, "Accept": "application/json"},
                timeout=10,
            )
        except requests.RequestException as exc:
            raise HTTPException(status_code=502, detail=f"Could not reach O*NET: {exc}") from exc
        if response.status_code != 429:
            break
        if attempt < 2:
            # O*NET asks clients receiving 429 to wait at least 200 ms.
            time.sleep(0.25 * (attempt + 1))

    if response is None:
        raise HTTPException(status_code=502, detail="O*NET did not return a response.")

    if response.status_code == 401:
        raise HTTPException(status_code=502, detail="O*NET rejected the configured API key.")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Occupation not found in O*NET.")
    if response.status_code == 429:
        raise HTTPException(status_code=503, detail="O*NET is temporarily rate limiting requests.")
    if not response.ok:
        raise HTTPException(
            status_code=502, detail=f"O*NET request failed ({response.status_code})."
        )
    return response.json()


def _extract_hard_skills(technology_categories):
    flagged = [
        example["title"]
        for category in technology_categories
        for example in category.get("example", [])
        if example.get("hot_technology") or example.get("in_demand")
    ]
    if flagged:
        return flagged
    return [
        example["title"]
        for category in technology_categories
        for example in category.get("example", [])
    ]


def _extract_soft_skills(skill_categories):
    return [
        element["name"]
        for category in skill_categories
        for element in category.get("element", [])
    ]


def _fetch_career_payload(soc_code: str):
    """Assemble one occupation's detail payload from O*NET.

    The five sub-resources are independent, so they are requested
    concurrently instead of one after another; a cold lookup was taking
    roughly the sum of five ~1.3s round trips (~6-7s) run sequentially.
    """
    with ThreadPoolExecutor(max_workers=5) as pool:
        summary_future = pool.submit(_onet_get, f"/mnm/careers/{soc_code}/")
        job_outlook_future = pool.submit(_onet_get, f"/mnm/careers/{soc_code}/job_outlook")
        education_future = pool.submit(_onet_get, f"/mnm/careers/{soc_code}/education")
        technology_future = pool.submit(_onet_get, f"/mnm/careers/{soc_code}/technology")
        skills_future = pool.submit(_onet_get, f"/mnm/careers/{soc_code}/skills")

        summary = summary_future.result()
        job_outlook = job_outlook_future.result()
        education = education_future.result()
        technology = technology_future.result()
        skills = skills_future.result()

    return {
        "onet_soc_code": soc_code,
        "title": summary.get("title"),
        "what_they_do": summary.get("what_they_do"),
        "bright_outlook": summary.get("tags", {}).get("bright_outlook", False),
        "salary": job_outlook.get("salary"),
        "outlook": job_outlook.get("outlook"),
        "job_zone": education.get("job_zone"),
        "education_usually_needed": education.get("education_usually_needed", []),
        "hard_skills": _extract_hard_skills(technology)[:8],
        "soft_skills": _extract_soft_skills(skills)[:8],
    }


def _detail_lock(soc_code: str) -> threading.Lock:
    """Return a stable per-career lock without serializing unrelated careers."""
    with _detail_locks_guard:
        return _detail_locks.setdefault(soc_code, threading.Lock())


def _cached_payload(soc_code: str):
    cached = _detail_cache.get(soc_code)
    if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]
    return None


def _get_or_fetch_payload(soc_code: str):
    """Return one cached payload and collapse simultaneous cold requests."""
    cached = _cached_payload(soc_code)
    if cached is not None:
        return cached
    with _detail_lock(soc_code):
        cached = _cached_payload(soc_code)
        if cached is not None:
            return cached
        payload = _fetch_career_payload(soc_code)
        _detail_cache[soc_code] = (time.time(), payload)
        return payload


@router.get("/{institution_code}/{program_code}/{soc_code}")
def get_career_detail(institution_code: str, program_code: str, soc_code: str):
    valid_codes = {row["onet_soc_code"] for row in careers_for_program(institution_code, program_code)}
    if soc_code not in valid_codes:
        raise HTTPException(
            status_code=404,
            detail="This occupation is not part of the curated list for this program.",
        )

    return _get_or_fetch_payload(soc_code)


def warm_cache():
    """Pre-fetch every curated occupation so the first real click during a
    session doesn't pay the cold-cache O*NET latency. Safe to call from a
    background thread at app startup: skips silently without a key, and
    only refetches codes that are missing or stale.

    Careers are warmed one at a time (each internally fetching its five
    sub-resources concurrently via `_fetch_career_payload`) rather than all
    at once. O*NET rate-limits bursts of concurrent connections; warming
    every curated career at once (16 careers x 5 requests) was observed to
    trigger throttling that also affected concurrent live requests. Running
    this in the background means the extra time from going one-at-a-time
    costs nothing real users wait on.
    """
    if not get_onet_api_key():
        return

    now = time.time()
    stale_codes = [
        code for code in {row["onet_soc_code"] for row in load_career_pathways()}
        if code not in _detail_cache or (now - _detail_cache[code][0]) >= _CACHE_TTL_SECONDS
    ]
    for code in stale_codes:
        try:
            _get_or_fetch_payload(code)
        except HTTPException:
            continue
