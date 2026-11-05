import unittest
from dataclasses import replace
from casting_agent.demo import DemoSource
from casting_agent.store import OpportunityStore


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.store = OpportunityStore()
        self.addCleanup(self.store.close)
        self.record = next(iter(DemoSource().discover()))

    def test_repeat_and_new_observation_do_not_duplicate_listing(self):
        self.assertEqual(self.store.ingest([self.record])["created"], 1)
        later = replace(self.record, observed_at="2026-11-05T18:00:00-05:00")
        self.assertEqual(self.store.ingest([later])["unchanged"], 1)
        self.assertEqual(len(self.store.list_opportunities()), 1)
        self.assertEqual(self.store.connection.execute("SELECT COUNT(*) FROM revisions").fetchone()[0], 1)

    def test_changed_post_is_preserved_as_revision(self):
        self.store.ingest([self.record])
        edited = replace(self.record, evidence_text="Fictional role cancelled.")
        self.assertEqual(self.store.ingest([edited])["updated"], 1)
        self.assertEqual(self.store.list_opportunities()[0]["evidence_text"], edited.evidence_text)
        self.assertEqual(self.store.connection.execute("SELECT COUNT(*) FROM revisions").fetchone()[0], 2)

    def test_ids_from_different_sources_remain_separate(self):
        self.store.ingest([self.record, replace(self.record, source_id="demo:other-agency")])
        self.assertEqual(len(self.store.list_opportunities()), 2)

    def test_failed_batch_rolls_back(self):
        def broken_source():
            yield self.record
            raise RuntimeError("source unavailable")
        with self.assertRaises(RuntimeError):
            self.store.ingest(broken_source())
        self.assertEqual(self.store.list_opportunities(), [])

    def test_incomplete_preview_cannot_claim_completeness(self):
        with self.assertRaises(ValueError):
            replace(self.record, complete=True)

    def test_credential_urls_and_naive_times_are_rejected(self):
        with self.assertRaises(ValueError):
            replace(self.record, original_url="https://user:secret@example.com/")
        with self.assertRaises(ValueError):
            replace(self.record, observed_at="2026-11-04T18:00:00")


if __name__ == "__main__":
    unittest.main()
