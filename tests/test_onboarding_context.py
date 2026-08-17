import unittest
from pathlib import Path


PAGE = Path(__file__).resolve().parents[1] / "frontend" / "program_selector.html"


class OnboardingContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_continue_current_major_restates_selected_program(self):
        self.assertIn('value === "continue_current" && currentProgram', self.html)
        self.assertIn("currentProgram.name", self.html)
        self.assertIn("currentProgram.degree_type", self.html)

    def test_onboarding_carries_explicit_credit_target(self):
        self.assertIn('targetCredits: "15"', self.html)
        self.assertIn('id="smartTargetCredits"', self.html)
        self.assertIn("targetCredits: Number(SMART_STATE.targetCredits)", self.html)


if __name__ == "__main__":
    unittest.main()
