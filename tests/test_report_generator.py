import os
from pathlib import Path
import tempfile
import unittest

from src.models import Flag
from src.report_generator import generate_report


class ReportTests(unittest.TestCase):
    def test_imported_fields_are_escaped_and_unicode_is_preserved(self):
        payload = '<script>alert("imported")</script>'
        flag = Flag(payload, "Zoë & <Admin>", "excess_access", payload, "high")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.html"
            generate_report([flag], 1, str(output))
            html = output.read_text(encoding="utf-8")
        self.assertNotIn("<script>", html)
        self.assertEqual(html.count("&lt;script&gt;"), 2)
        self.assertIn("Zoë &amp; &lt;Admin&gt;", html)
        self.assertIn("1 users reviewed", html)
        self.assertIn("1 flags found", html)

    def test_template_resolves_outside_repository_and_empty_report_renders(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                generate_report([], 0, "report.html")
                html = Path("report.html").read_text(encoding="utf-8")
            finally:
                os.chdir(previous)
        self.assertIn("0 users reviewed", html)
        self.assertIn("0 flags found", html)
