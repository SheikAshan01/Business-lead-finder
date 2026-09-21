from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.business import LeadStatus, WebsiteStatus


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    enabled: bool
    business_count: int = 0


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class LocationDistrictOut(BaseModel):
    district: str
    count: int = 0


class LocationTalukOut(BaseModel):
    district: str
    taluk: str


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contact_name: str
    designation: str | None = None
    phone: str | None = None
    email: str | None = None
    is_primary: bool = False


class SocialProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    platform: str
    profile_url: str


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    business_id: int
    user_id: int | None = None
    note: str
    created_at: datetime


class NoteCreate(BaseModel):
    note: str = Field(min_length=1, max_length=4000)


class StatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    old_status: str
    new_status: str
    reason: str | None = None
    created_at: datetime


class StatusUpdate(BaseModel):
    status: LeadStatus
    reason: str | None = None


class BusinessCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=240)
    client_name: str | None = None
    category_id: int | None = None
    phone: str | None = None
    alternate_phone: str | None = None
    email: str | None = None
    address: str | None = None
    area: str | None = None
    taluk: str | None = None
    district: str | None = None
    state: str = "Tamil Nadu"
    pincode: str | None = None
    website_url: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    youtube_url: str | None = None
    whatsapp_url: str | None = None
    source: str | None = None
    source_url: str | None = None


class BusinessUpdate(BaseModel):
    business_name: str | None = None
    client_name: str | None = None
    phone: str | None = None
    alternate_phone: str | None = None
    email: str | None = None
    address: str | None = None
    district: str | None = None
    website_url: str | None = None
    lead_status: LeadStatus | None = None


class BulkDeleteRequest(BaseModel):
    ids: list[int]


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    business_name: str
    client_name: str | None = None
    category_id: int | None = None
    category_name: str | None = None
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
    website_status: WebsiteStatus
    website_verified: bool = False
    website_checked_at: datetime | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    youtube_url: str | None = None
    whatsapp_url: str | None = None
    source: str | None = None
    source_url: str | None = None
    source_record_id: str | None = None
    lead_score: int = 0
    score_reasons: str | None = None
    lead_status: LeadStatus = LeadStatus.NEW
    is_saved: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    notes: list[NoteOut] = []
    status_history: list[StatusHistoryOut] = []
    contacts: list[ContactOut] = []
    social_profiles: list[SocialProfileOut] = []


class PaginatedBusinesses(BaseModel):
    items: list[BusinessOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScrapeRequest(BaseModel):
    category: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=160)


class ScrapeJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    location: str
    status: str
    progress: int
    discovered: int
    valid: int
    duplicates: int
    no_website: int
    website_found: int
    errors: int
    error_message: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class DashboardStats(BaseModel):
    total: int
    no_website: int
    website_found: int
    saved: int
    converted: int
    phone: int
    email: int
    high_score: int


class ChartItem(BaseModel):
    label: str
    count: int


class DashboardCharts(BaseModel):
    by_category: list[ChartItem]
    by_district: list[ChartItem]
    no_website_by_district: list[ChartItem]
    status_distribution: list[ChartItem]


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    source_type: str
    enabled: bool
    rate_limit: int
    terms_url: str | None = None
