import asyncio
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models.business import (
    Business,
    BusinessContact,
    BusinessSocialProfile,
    Category,
    ScrapeJob,
    ScrapeJobResult,
    Source,
    WebsiteStatus,
)
from app.scrapers.adapters.google_places import GooglePlacesAdapter
from app.scrapers.adapters.osm_overpass import OSMOverpassAdapter
from app.scrapers.deduplicator import Deduplicator, DuplicateStatus
from app.scrapers.lead_scorer import LeadScorer
from app.scrapers.validator import BusinessValidator
from app.scrapers.website_detector import verify_website

logger = logging.getLogger("sra_leads.jobs")


def get_active_adapters(db: Session):
    adapters = []
    # Check configured sources in DB
    osm_source = db.query(Source).filter(Source.name == "OpenStreetMap Overpass TN").first()
    if not osm_source or osm_source.enabled:
        adapters.append(OSMOverpassAdapter())

    google_source = db.query(Source).filter(Source.name == "Google Places API").first()
    if google_source and google_source.enabled:
        adapters.append(GooglePlacesAdapter())

    return adapters


def execute_job(db: Session, job: ScrapeJob) -> None:
    """Execute the full end-to-end business discovery, validation, and scoring pipeline."""
    try:
        logger.info(f"Starting ScrapeJob #{job.id} for Category='{job.category}', Location='{job.location}'")
        job.status = "RUNNING"
        job.progress = 8
        db.commit()

        adapters = get_active_adapters(db)
        if not adapters:
            # Fallback to default OSM adapter
            adapters = [OSMOverpassAdapter()]

        # Step 1: Discover Businesses from Permitted Adapters
        job.progress = 15
        db.commit()

        discovered_raw = []
        for adapter in adapters:
            try:
                logger.info(f"Querying adapter: {adapter.name}")
                found = adapter.search(job.category, job.location, limit=60)
                discovered_raw.extend(found)
            except Exception as ex:
                logger.error(f"Adapter {adapter.name} failed: {ex}")
                job.errors += 1
                db.commit()

        job.discovered = len(discovered_raw)
        job.progress = 32
        db.commit()
        logger.info(f"Job #{job.id} discovered {job.discovered} raw records")

        if not discovered_raw:
            job.status = "COMPLETED"
            job.progress = 100
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        # Find or match category in DB
        cat_obj = db.query(Category).filter(Category.name.ilike(job.category.strip())).first()
        category_id = cat_obj.id if cat_obj else None

        # Step 2: Normalize, Validate, Deduplicate, Verify Website, Score, and Store
        total_items = len(discovered_raw)

        # Run async website verification in event loop
        async def verify_all():
            results = []
            for item in discovered_raw:
                try:
                    res = await verify_website(item.website_url)
                    results.append(res)
                except Exception:
                    results.append((WebsiteStatus.UNKNOWN, False, datetime.utcnow()))
            return results

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In nested event loop
                import nest_asyncio
                nest_asyncio.apply()
                website_results = loop.run_until_complete(verify_all())
            else:
                website_results = loop.run_until_complete(verify_all())
        except Exception:
            website_results = asyncio.run(verify_all())

        for idx, (raw, (web_status, web_verified, web_checked_at)) in enumerate(zip(discovered_raw, website_results)):
            try:
                # 2a. Validation
                cleaned = BusinessValidator.clean_and_validate(raw)
                if not cleaned:
                    job.errors += 1
                    res_entry = ScrapeJobResult(
                        job_id=job.id,
                        business_id=None,
                        status="REJECTED",
                        error_details="Failed name or structure validation",
                    )
                    db.add(res_entry)
                    continue

                job.valid += 1

                # 2b. Deduplication Check
                dup_status, match_business, reason = Deduplicator.check_duplicate(cleaned, db)
                if dup_status == DuplicateStatus.DUPLICATE and match_business:
                    job.duplicates += 1
                    res_entry = ScrapeJobResult(
                        job_id=job.id,
                        business_id=match_business.id,
                        status="DUPLICATE",
                        error_details=reason,
                    )
                    db.add(res_entry)
                    continue

                # 2c. Website counters
                if web_status == WebsiteStatus.NO_WEBSITE:
                    job.no_website += 1
                elif web_status == WebsiteStatus.WEBSITE_FOUND:
                    job.website_found += 1

                # 2d. Lead Scoring
                score, reasons, reasons_json = LeadScorer.score_raw(cleaned, web_status)

                # 2e. Create Business record
                new_business = Business(
                    business_name=cleaned.business_name,
                    client_name=cleaned.client_name,
                    category_id=category_id,
                    phone=cleaned.phone,
                    alternate_phone=cleaned.alternate_phone,
                    email=cleaned.email,
                    address=cleaned.address,
                    area=cleaned.area,
                    taluk=cleaned.taluk,
                    district=cleaned.district or job.location,
                    state=cleaned.state or "Tamil Nadu",
                    pincode=cleaned.pincode,
                    latitude=cleaned.latitude,
                    longitude=cleaned.longitude,
                    website_url=cleaned.website_url,
                    website_status=web_status,
                    website_verified=web_verified,
                    website_checked_at=web_checked_at,
                    facebook_url=cleaned.facebook_url,
                    instagram_url=cleaned.instagram_url,
                    youtube_url=cleaned.youtube_url,
                    whatsapp_url=cleaned.whatsapp_url,
                    source=cleaned.source,
                    source_url=cleaned.source_url,
                    source_record_id=cleaned.source_record_id,
                    lead_score=score,
                    score_reasons=reasons_json,
                    is_saved=False,
                )
                db.add(new_business)
                db.flush()  # obtain ID

                # Social profiles
                if cleaned.facebook_url:
                    db.add(BusinessSocialProfile(business_id=new_business.id, platform="facebook", profile_url=cleaned.facebook_url))
                if cleaned.instagram_url:
                    db.add(BusinessSocialProfile(business_id=new_business.id, platform="instagram", profile_url=cleaned.instagram_url))
                if cleaned.whatsapp_url:
                    db.add(BusinessSocialProfile(business_id=new_business.id, platform="whatsapp", profile_url=cleaned.whatsapp_url))

                # Primary contact
                if cleaned.client_name or cleaned.phone or cleaned.email:
                    db.add(
                        BusinessContact(
                            business_id=new_business.id,
                            contact_name=cleaned.client_name or cleaned.business_name,
                            phone=cleaned.phone,
                            email=cleaned.email,
                            is_primary=True,
                        )
                    )

                # Record job result link
                res_entry = ScrapeJobResult(
                    job_id=job.id,
                    business_id=new_business.id,
                    status="SAVED",
                    error_details=None,
                )
                db.add(res_entry)

                # Update progress smoothly
                current_prog = 35 + int(((idx + 1) / total_items) * 63)
                job.progress = min(current_prog, 98)
                db.commit()

            except Exception as row_err:
                logger.error(f"Error processing record {raw.business_name}: {row_err}")
                job.errors += 1
                db.rollback()

        job.status = "COMPLETED"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        db.commit()
        logger.info(
            f"Completed ScrapeJob #{job.id}: discovered={job.discovered}, valid={job.valid}, "
            f"duplicates={job.duplicates}, no_website={job.no_website}, website_found={job.website_found}"
        )

    except Exception as e:
        logger.error(f"Fatal error in ScrapeJob #{job.id}: {e}")
        db.rollback()
        job.status = "FAILED"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
