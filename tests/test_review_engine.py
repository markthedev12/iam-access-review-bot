from datetime import date, timedelta
import unittest

from src.models import Entitlement, User
from src.review_engine import review_user, review_all_users


class ReviewTests(unittest.TestCase):
    today = date(2026, 11, 8)
    baseline = {"Analyst": {"expected_systems": ["Directory"],
                            "expected_groups": ["Support"],
                            "max_privileged_access": False}}

    def user(self, days=0, system="Directory", privileged=False):
        return User("u1", "Sample User", "Analyst", [
            Entitlement(system, "Support", self.today - timedelta(days=days), privileged)
        ])

    def test_expected_access_has_no_flags(self):
        self.assertEqual(review_user(self.user(), self.baseline, self.today), [])

    def test_stale_boundary(self):
        for days, count in [(89, 0), (90, 0), (91, 1)]:
            with self.subTest(days=days):
                flags = review_user(self.user(days), self.baseline, self.today)
                self.assertEqual([f.flag_type for f in flags], ["stale_access"] * count)

    def test_multiple_findings_are_not_short_circuited(self):
        flags = review_user(self.user(91, "Unknown", True), self.baseline, self.today)
        self.assertEqual({f.flag_type for f in flags},
                         {"excess_access", "stale_access", "privilege_violation"})
        self.assertEqual({f.risk_level for f in flags}, {"low", "medium", "high"})

    def test_unknown_role_requires_review(self):
        flags = review_user(self.user(), {}, self.today)
        self.assertEqual(len(flags), 1)
        self.assertIn("cannot validate", flags[0].detail)

    def test_explicit_date_is_used_for_entire_batch(self):
        flags = review_all_users([self.user(91), self.user(90)], self.baseline, self.today)
        self.assertEqual(len(flags), 1)

    def test_privileged_role_is_allowed(self):
        baseline = {"Analyst": {**self.baseline["Analyst"], "max_privileged_access": True}}
        self.assertEqual(review_user(self.user(privileged=True), baseline, self.today), [])
