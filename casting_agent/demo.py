import json
from .models import Opportunity
from .store import OpportunityStore


class DemoSource:
    source_id = "demo:fictional-agency"
    capabilities = frozenset({"discover", "read"})

    def discover(self):
        yield Opportunity(
            source_id=self.source_id,
            external_id="fictional-role-001",
            title="FICTIONAL DEMO: Cafe patrons",
            original_url="https://example.com/casting/fictional-role-001",
            observed_at="2026-11-04T18:00:00-05:00",
            evidence_text="Fictional notification preview: cafe patrons wanted. Open original for details.",
            missing_fields=("shoot_dates", "pay", "requirements", "deadline"),
            location="Toronto",
        )


def main():
    store = OpportunityStore()
    try:
        source = DemoSource()
        print(json.dumps({"first_run": store.ingest(source.discover()), "repeat_run": store.ingest(source.discover()), "opportunities": store.list_opportunities()}, indent=2))
    finally:
        store.close()


if __name__ == "__main__":
    main()
