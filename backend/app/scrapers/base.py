from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RawBusiness:
    business_name: str
    client_name: str | None = None
    category: str | None = None
    phone: str | None = None
    alternate_phone: str | None = None
    email: str | None = None
    address: str | None = None
    area: str | None = None
    taluk: str | None = None
    district: str | None = None
    state: str = "Tamil Nadu"
    pincode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    website_url: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    youtube_url: str | None = None
    whatsapp_url: str | None = None
    source: str = "unknown"
    source_url: str | None = None
    source_record_id: str | None = None
    extra_tags: dict = field(default_factory=dict)


class BaseSourceAdapter(ABC):
    """Abstract interface that all data source adapters must implement."""

    name: str
    source_type: str = "OPEN_DATA"  # API, OPEN_DATA, DIRECTORY
    enabled: bool = True
    rate_limit: int = 30  # requests per minute
    terms_url: str | None = None

    @abstractmethod
    def search(self, category: str, location: str, limit: int = 50) -> list[RawBusiness]:
        """Discover and return normalized RawBusiness records from the authorized source."""
        raise NotImplementedError
