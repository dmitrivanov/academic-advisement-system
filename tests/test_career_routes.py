import csv
import os
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi import HTTPException

import career_routes


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read_career_pathways():
    with (DOCS / "career_pathways.csv").open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class CareerPathwaysDataTests(unittest.TestCase):
    def test_career_pathways_file_has_rows(self):
        rows = read_career_pathways()
        self.assertTrue(rows)

    def test_no_duplicate_soc_codes_within_a_program(self):
        rows = read_career_pathways()
        seen = set()
        for row in rows:
            key = (row["institution_code"], row["program_code"], row["onet_soc_code"])
            self.assertNotIn(key, seen, f"duplicate career row: {key}")
            seen.add(key)

    def test_cs_program_referenced_exists_in_programs_csv(self):
        programs_text = (DOCS / "programs.csv").read_text(encoding="utf-8")
        rows = read_career_pathways()
        program_codes = {row["program_code"] for row in rows}
        for code in program_codes:
            self.assertIn(f",{code},", programs_text, code)

    def test_soc_codes_look_like_soc_codes(self):
        # xx-xxxx.xx format
        import re

        pattern = re.compile(r"^\d{2}-\d{4}\.\d{2}$")
        for row in read_career_pathways():
            self.assertRegex(row["onet_soc_code"], pattern, row["onet_soc_code"])

    def test_career_page_renders_api_text_without_html_interpolation(self):
        page = (ROOT / "frontend" / "careers.html").read_text(encoding="utf-8")
        self.assertIn("title.textContent = career.title", page)
        self.assertIn("item.textContent = skill", page)
        self.assertNotIn("<span>${career.title}</span>", page)
        self.assertNotIn("skills.map(skill => `<li>${skill}</li>`)", page)
        self.assertIn('href="https://services.onetcenter.org/"', page)


class ListCareersTests(unittest.TestCase):
    def test_list_careers_for_known_program(self):
        result = career_routes.list_careers("BMCC", "CS")
        self.assertEqual("BMCC", result["institution_code"])
        self.assertEqual("CS", result["program_code"])
        self.assertTrue(result["careers"])
        titles = [c["title"] for c in result["careers"]]
        self.assertIn("Software Developers", titles)

    def test_list_careers_is_case_insensitive(self):
        result = career_routes.list_careers("bmcc", "cs")
        self.assertTrue(result["careers"])

    def test_list_careers_for_unknown_program_is_empty_not_an_error(self):
        result = career_routes.list_careers("BMCC", "NOT_A_REAL_PROGRAM")
        self.assertEqual([], result["careers"])

    def test_careers_are_sorted_by_display_order(self):
        result = career_routes.list_careers("BMCC", "CS")
        rows = career_routes.careers_for_program("BMCC", "CS")
        expected_order = [row["onet_soc_code"] for row in sorted(rows, key=lambda r: int(r["display_order"]))]
        self.assertEqual(expected_order, [c["onet_soc_code"] for c in result["careers"]])


class CareerDetailTests(unittest.TestCase):
    def test_missing_api_key_raises_503(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as raised:
                career_routes.get_career_detail("BMCC", "CS", "15-1252.00")
            self.assertEqual(503, raised.exception.status_code)

    def test_soc_code_not_in_program_list_raises_404(self):
        with patch.dict(os.environ, {"ONET_API_KEY": "test-key"}):
            with self.assertRaises(HTTPException) as raised:
                career_routes.get_career_detail("BMCC", "CS", "00-0000.00")
            self.assertEqual(404, raised.exception.status_code)

    def test_detail_payload_shape_with_mocked_onet_responses(self):
        career_routes._detail_cache.clear()
        responses_by_path = {
            "/mnm/careers/15-1252.00/": {
                "title": "Software Developers",
                "what_they_do": "Develop software.",
                "tags": {"bright_outlook": True},
            },
            "/mnm/careers/15-1252.00/job_outlook": {
                "outlook": {"category": "Bright", "description": "Growing fast."},
                "salary": {"soc_code": "15-1252.00", "hourly_median": 55, "hourly_10th_percentile": 30, "hourly_90th_percentile": 85},
            },
            "/mnm/careers/15-1252.00/education": {
                "job_zone": {"code": 4, "title": "Considerable Preparation Needed"},
                "education_usually_needed": ["Bachelor's degree"],
            },
            "/mnm/careers/15-1252.00/technology": [
                {
                    "code": 1,
                    "title": "Database software",
                    "example": [
                        {"title": "MySQL", "hot_technology": True},
                        {"title": "Obscure DB", "hot_technology": False},
                    ],
                }
            ],
            "/mnm/careers/15-1252.00/skills": [
                {
                    "id": "2.A",
                    "name": "Basic Skills",
                    "element": [
                        {"id": "2.A.2.a", "name": "thinking about the pros and cons of different ways to solve a problem"},
                    ],
                },
            ],
        }

        def fake_get(path):
            return responses_by_path[path]

        with patch.dict(os.environ, {"ONET_API_KEY": "test-key"}):
            with patch.object(career_routes, "_onet_get", side_effect=fake_get) as mocked:
                detail = career_routes.get_career_detail("BMCC", "CS", "15-1252.00")
                self.assertEqual("Software Developers", detail["title"])
                self.assertTrue(detail["bright_outlook"])
                self.assertEqual(55, detail["salary"]["hourly_median"])
                self.assertEqual("Bright", detail["outlook"]["category"])
                self.assertEqual(["MySQL"], detail["hard_skills"])
                self.assertEqual(
                    ["thinking about the pros and cons of different ways to solve a problem"],
                    detail["soft_skills"],
                )
                self.assertEqual(5, mocked.call_count)

                # second call should hit the cache, not _onet_get again
                mocked.reset_mock()
                cached_detail = career_routes.get_career_detail("BMCC", "CS", "15-1252.00")
                self.assertEqual(detail, cached_detail)
                mocked.assert_not_called()

        career_routes._detail_cache.clear()

    def test_simultaneous_cold_requests_share_one_fetch(self):
        career_routes._detail_cache.clear()
        calls = 0
        calls_lock = threading.Lock()

        def fake_fetch(soc_code):
            nonlocal calls
            with calls_lock:
                calls += 1
            time.sleep(0.05)
            return {"onet_soc_code": soc_code, "title": "Software Developers"}

        with patch.object(career_routes, "_fetch_career_payload", side_effect=fake_fetch):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(career_routes._get_or_fetch_payload, ["15-1252.00"] * 2))

        self.assertEqual(1, calls)
        self.assertEqual(results[0], results[1])
        career_routes._detail_cache.clear()

    def test_onet_rate_limit_retries_after_documented_delay(self):
        limited = Mock(status_code=429, ok=False)
        success = Mock(status_code=200, ok=True)
        success.json.return_value = {"title": "Software Developers"}
        with patch.dict(os.environ, {"ONET_API_KEY": "test-key"}):
            with patch.object(career_routes.requests, "get", side_effect=[limited, success]) as get:
                with patch.object(career_routes.time, "sleep") as sleep:
                    result = career_routes._onet_get("/mnm/careers/15-1252.00/")
        self.assertEqual("Software Developers", result["title"])
        self.assertEqual(2, get.call_count)
        sleep.assert_called_once_with(0.25)

    def test_cache_warmup_is_disabled_without_an_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(career_routes, "_get_or_fetch_payload") as fetch:
                career_routes.warm_cache()
        fetch.assert_not_called()


class ExtractHardSkillsTests(unittest.TestCase):
    def test_prefers_flagged_technologies(self):
        categories = [
            {
                "example": [
                    {"title": "Python", "hot_technology": True},
                    {"title": "Rarely used tool", "hot_technology": False},
                ]
            }
        ]
        self.assertEqual(["Python"], career_routes._extract_hard_skills(categories))

    def test_falls_back_to_all_examples_when_none_flagged(self):
        categories = [{"example": [{"title": "Some tool"}]}]
        self.assertEqual(["Some tool"], career_routes._extract_hard_skills(categories))


class ExtractSoftSkillsTests(unittest.TestCase):
    def test_flattens_nested_elements_not_category_names(self):
        # The O*NET skills endpoint nests specific, plain-language skills
        # one level below the broad category name (e.g. "Basic Skills").
        # The category name itself is not a useful "skill" to display.
        categories = [
            {
                "name": "Basic Skills",
                "element": [
                    {"id": "2.A.2.a", "name": "reading work-related information"},
                    {"id": "2.A.2.b", "name": "writing things for coworkers or customers"},
                ],
            },
            {"name": "Problem Solving", "element": [{"id": "2.B.2.i", "name": "noticing a problem"}]},
        ]
        self.assertEqual(
            [
                "reading work-related information",
                "writing things for coworkers or customers",
                "noticing a problem",
            ],
            career_routes._extract_soft_skills(categories),
        )

    def test_handles_categories_with_no_elements(self):
        self.assertEqual([], career_routes._extract_soft_skills([{"name": "Empty", "element": []}]))


if __name__ == "__main__":
    unittest.main()
