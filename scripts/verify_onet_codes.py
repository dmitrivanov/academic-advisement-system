"""Confirm docs/career_pathways.csv's O*NET-SOC codes against the live O*NET search API.

The codes in career_pathways.csv were entered from general knowledge of
standard O*NET-SOC codes, not copied from a live API response (no API key
was available at the time). Run this once ONET_API_KEY is set to catch any
wrong or renamed codes before relying on them.

Usage:
    ONET_API_KEY=your-key python scripts/verify_onet_codes.py
"""

import csv
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CAREER_PATHWAYS_FILE = ROOT / "docs" / "career_pathways.csv"
ONET_BASE_URL = "https://api-v2.onetcenter.org"


def search_title(api_key, title):
    response = requests.get(
        f"{ONET_BASE_URL}/mnm/search",
        headers={"X-API-Key": api_key, "Accept": "application/json"},
        params={"keyword": title},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("career", [])


def main():
    api_key = os.environ.get("ONET_API_KEY")
    if not api_key:
        print("Set ONET_API_KEY before running this script.")
        return 1

    with CAREER_PATHWAYS_FILE.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    problems = 0
    for row in rows:
        title = row["occupation_title"]
        code = row["onet_soc_code"]
        results = search_title(api_key, title)
        matching = [r for r in results if r["code"] == code]
        if matching:
            print(f"OK    {code}  {title}")
            continue

        problems += 1
        print(f"CHECK {code}  {title}  -- no exact code match in search results:")
        for candidate in results[:5]:
            print(f"        {candidate['code']}  {candidate['title']}")

    print()
    print(f"{len(rows)} rows checked, {problems} need review.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
