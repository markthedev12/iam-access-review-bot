import json
from pathlib import Path
import tempfile
import unittest
from src.loader import load_access_export, load_role_baseline

HEADER = "user_id,name,role,system,group,last_reviewed,privileged\n"
ROW = "u1,Sample,Nurse,EHR,Clinical,2026-01-01,false\n"

class LoaderTests(unittest.TestCase):
    def load_csv(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_text(content, encoding="utf-8")
            return load_access_export(path)

    def test_groups_users_and_accepts_bom(self):
        users = self.load_csv("\ufeff" + HEADER + ROW + ROW)
        self.assertEqual(len(users), 1)
        self.assertEqual(len(users[0].entitlements), 2)
        self.assertFalse(users[0].entitlements[0].privileged)

    def test_rejects_bad_boolean_date_and_identity(self):
        for content in (HEADER + ROW.replace("false", "yes"),
                        HEADER + ROW.replace("2026-01-01", "2026-99-99"),
                        HEADER + ROW + ROW.replace("Sample", "Other")):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "row"):
                self.load_csv(content)

    def test_rejects_missing_headers_and_values(self):
        for content in ("wrong\nvalue\n", HEADER + ROW.replace("Sample", "")):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.load_csv(content)

    def test_rejects_string_boolean_in_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "baseline.json"
            path.write_text(json.dumps({"Nurse": {"expected_systems": [], "expected_groups": [], "max_privileged_access": "false"}}))
            with self.assertRaisesRegex(ValueError, "boolean"):
                load_role_baseline(path)
