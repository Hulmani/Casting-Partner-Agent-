from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Opportunity:
    source_id: str
    external_id: str
    title: str
    original_url: str
    observed_at: str
    evidence_text: str
    complete: bool = False
    missing_fields: Tuple[str, ...] = ()
    location: Optional[str] = None
    shoot_dates: Tuple[str, ...] = ()

    def __post_init__(self):
        for field in ("source_id", "external_id", "title", "evidence_text"):
            if not isinstance(getattr(self, field), str) or not getattr(self, field).strip():
                raise ValueError(f"{field} must contain text")
        parsed = urlsplit(self.original_url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("original_url must be an HTTPS URL without embedded credentials")
        timestamp = datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError("observed_at needs an explicit timezone")
        if type(self.complete) is not bool:
            raise ValueError("complete must be a boolean")
        if self.complete and self.missing_fields:
            raise ValueError("a complete listing cannot have missing fields")
        for value in self.shoot_dates:
            datetime.strptime(value, "%Y-%m-%d")
