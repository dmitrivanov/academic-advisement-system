import unittest

from app import retrieve


class RetrievalTests(unittest.TestCase):
    def test_crsp_stipend(self):
        matches = retrieve("How much does CRSP pay?")
        self.assertTrue(matches)
        self.assertIn("CRSP", matches[0][1]["question"])

    def test_mentor(self):
        matches = retrieve("Do I need a professor before I apply?")
        self.assertTrue(matches)
        self.assertIn("mentor", (matches[0][1]["question"] + matches[0][1]["keywords"]).lower())


if __name__ == "__main__":
    unittest.main()
