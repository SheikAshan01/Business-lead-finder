from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class WebsiteStatus(str, Enum):
    NO_WEBSITE = "NO_WEBSITE"
    WEBSITE_FOUND = "WEBSITE_FOUND"
    WEBSITE_UNVERIFIED = "WEBSITE_UNVERIFIED"
    WEBSITE_BROKEN = "WEBSITE_BROKEN"
    SOCIAL_ONLY = "SOCIAL_ONLY"
    UNKNOWN = "UNKNOWN"


class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    INTERESTED = "INTERESTED"
    FOLLOW_UP = "FOLLOW_UP"
    CONVERTED = "CONVERTED"
    NOT_INTERESTED = "NOT_INTERESTED"


class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"


# 1. Users Table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default=UserRole.AGENT.value, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    notes: Mapped[list["LeadNote"]] = relationship("LeadNote", back_populates="user")
    status_history: Mapped[list["LeadStatusHistory"]] = relationship("LeadStatusHistory", back_populates="user")
    saved_leads: Mapped[list["SavedLead"]] = relationship("SavedLead", back_populates="user")


# 2. Categories Table
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    businesses: Mapped[list["Business"]] = relationship("Business", back_populates="category_rel")


# 3. Locations Table (Hierarchical: State -> District -> Taluk -> Area -> Pincode)
class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[str] = mapped_column(String(80), default="Tamil Nadu", index=True)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    taluk: Mapped[str | None] = mapped_column(String(100), index=True)
    area: Mapped[str | None] = mapped_column(String(120))
    pincode: Mapped[str | None] = mapped_column(String(10), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# 4. Businesses Table
class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_name: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(160))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), index=True)
    phone: Mapped[str | None] = mapped_column(String(20), index=True)
    alternate_phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    address: Mapped[str | None] = mapped_column(Text)
    area: Mapped[str | None] = mapped_column(String(120))
    taluk: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(80), default="Tamil Nadu", index=True)
    pincode: Mapped[str | None] = mapped_column(String(10), index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    website_url: Mapped[str | None] = mapped_column(String(500))
    website_status: Mapped[WebsiteStatus] = mapped_column(String(32), default=WebsiteStatus.UNKNOWN, index=True)
    website_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    website_checked_at: Mapped[datetime | None] = mapped_column(DateTime)

    facebook_url: Mapped[str | None] = mapped_column(String(500))
    instagram_url: Mapped[str | None] = mapped_column(String(500))
    youtube_url: Mapped[str | None] = mapped_column(String(500))
    whatsapp_url: Mapped[str | None] = mapped_column(String(500))

    source: Mapped[str | None] = mapped_column(String(120), index=True)
    source_url: Mapped[str | None] = mapped_column(String(500))
    source_record_id: Mapped[str | None] = mapped_column(String(180), index=True)

    lead_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    score_reasons: Mapped[str | None] = mapped_column(Text)
    lead_status: Mapped[LeadStatus] = mapped_column(String(32), default=LeadStatus.NEW, index=True)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    category_rel: Mapped[Category | None] = relationship("Category", back_populates="businesses")
    contacts: Mapped[list["BusinessContact"]] = relationship("BusinessContact", back_populates="business", cascade="all, delete-orphan")
    social_profiles: Mapped[list["BusinessSocialProfile"]] = relationship("BusinessSocialProfile", back_populates="business", cascade="all, delete-orphan")
    notes: Mapped[list["LeadNote"]] = relationship("LeadNote", back_populates="business", cascade="all, delete-orphan", order_by="desc(LeadNote.created_at)")
    status_history: Mapped[list["LeadStatusHistory"]] = relationship("LeadStatusHistory", back_populates="business", cascade="all, delete-orphan", order_by="desc(LeadStatusHistory.created_at)")
    saved_entries: Mapped[list["SavedLead"]] = relationship("SavedLead", back_populates="business", cascade="all, delete-orphan")


# 5. Business Contacts Table
class BusinessContact(Base):
    __tablename__ = "business_contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    contact_name: Mapped[str] = mapped_column(String(160), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    business: Mapped[Business] = relationship("Business", back_populates="contacts")


# 6. Business Social Profiles Table
class BusinessSocialProfile(Base):
    __tablename__ = "business_social_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # facebook, instagram, youtube, whatsapp
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    business: Mapped[Business] = relationship("Business", back_populates="social_profiles")


# 7. Scrape Jobs Table
class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    discovered: Mapped[int] = mapped_column(Integer, default=0)
    valid: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    no_website: Mapped[int] = mapped_column(Integer, default=0)
    website_found: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    results: Mapped[list["ScrapeJobResult"]] = relationship("ScrapeJobResult", back_populates="job", cascade="all, delete-orphan")


# 8. Scrape Job Results Table
class ScrapeJobResult(Base):
    __tablename__ = "scrape_job_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("scrape_jobs.id"), index=True, nullable=False)
    business_id: Mapped[int | None] = mapped_column(ForeignKey("businesses.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="SAVED")  # SAVED, DUPLICATE, REJECTED, ERROR
    error_details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    job: Mapped[ScrapeJob] = relationship("ScrapeJob", back_populates="results")


# 9. Sources Table
class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), default="OPEN_DATA")  # API, OPEN_DATA, DIRECTORY
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit: Mapped[int] = mapped_column(Integer, default=30)  # requests/min
    terms_url: Mapped[str | None] = mapped_column(String(500))
    config_json: Mapped[str | None] = mapped_column(Text)


# 10. Saved Leads Table
class SavedLead(Base):
    __tablename__ = "saved_leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    saved_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User | None] = relationship("User", back_populates="saved_leads")
    business: Mapped[Business] = relationship("Business", back_populates="saved_entries")


# 11. Lead Notes Table
class LeadNote(Base):
    __tablename__ = "lead_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    business: Mapped[Business] = relationship("Business", back_populates="notes")
    user: Mapped[User | None] = relationship("User", back_populates="notes")


# 12. Lead Status History Table
class LeadStatusHistory(Base):
    __tablename__ = "lead_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    old_status: Mapped[str] = mapped_column(String(32), nullable=False)
    new_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    business: Mapped[Business] = relationship("Business", back_populates="status_history")
    user: Mapped[User | None] = relationship("User", back_populates="status_history")


# 13. Audit Logs Table
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer)
    details: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
