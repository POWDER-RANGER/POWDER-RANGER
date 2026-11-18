"""Offline tests for profile activity rendering."""
import unittest
from scripts.update_activity import START, END, replace_section, summarize


class ActivityTests(unittest.TestCase):
    def test_only_confirmed_merges(self):
        events = [
            {"type": "PullRequestEvent", "repo": {"name": "team/project"},
             "payload": {"action": "closed", "pull_request": {"number": 12, "merged": False}}},
            {"type": "PullRequestEvent", "repo": {"name": "team/project"},
             "payload": {"action": "closed", "pull_request": {"number": 13, "merged": True}}},
        ]
        self.assertEqual(summarize(events), [
            "- **Merged a pull request** in [team/project](<https://github.com/team/project/pull/13>)"
        ])

    def test_excludes_profile_and_bad_payloads(self):
        events = [
            {"type": "PushEvent", "repo": {"name": "POWDER-RANGER/POWDER-RANGER"}},
            {"type": "PushEvent", "repo": {"name": "team/../unsafe"}},
            {"type": "PushEvent", "repo": {"name": "team/project"}, "payload": None},
            {"type": "PushEvent", "repo": {"name": "team/project"}, "payload": {}},
        ]
        # Duplicate events from the same repository collapse to one line.
        self.assertEqual(len(summarize(events)), 1)

    def test_empty_preserves_content(self):
        source = f"before\n{START}\nexisting\n{END}\nafter"
        self.assertEqual(replace_section(source, []), source)

    def test_markers_required(self):
        with self.assertRaises(ValueError):
            replace_section("no markers", ["hello"])

    def test_max_six(self):
        events = [
            {"type": "PushEvent", "repo": {"name": f"team/repo{i}"}, "payload": {}}
            for i in range(20)
        ]
        self.assertEqual(len(summarize(events)), 6)


if __name__ == "__main__":
    unittest.main()
