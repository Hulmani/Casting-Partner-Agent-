from typing import Iterable, Protocol
from ..models import Opportunity


class SourceAdapter(Protocol):
    """Read contract; live adapters must manage auth and cursors separately."""

    source_id: str
    capabilities: frozenset

    def discover(self) -> Iterable[Opportunity]:
        ...
