"""Outreach & Sales Automation Route.

Generates hyper-personalized B2B pitches, WhatsApp messages, and Cold Emails
customized for Tamil Nadu business prospects.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.license import load_agency_branding
from app.db import get_db
from app.models.business import Business, WebsiteStatus

router = APIRouter(prefix="/outreach", tags=["outreach & pitches"])


class PitchRequest(BaseModel):
    business_id: int
    pitch_type: str = "website_pitch"  # website_pitch, seo_reputation, ecommerce_catalog, cold_email
    language: str = "tamil"  # tamil, english, tanglish


@router.post("/generate-pitch")
def generate_custom_pitch(payload: PitchRequest, db: Session = Depends(get_db)):
    biz = db.get(Business, payload.business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    branding = load_agency_branding()
    agency_name = branding.get("agency_name") or "SRA Software Solutions"
    support_phone = branding.get("support_phone") or ""
    support_email = branding.get("support_email") or ""

    contact_suffix = f"\n\n- {agency_name}"
    if support_phone:
        contact_suffix += f"\nPhone: {support_phone}"
    if support_email:
        contact_suffix += f"\nEmail: {support_email}"

    b_name = biz.business_name
    district = biz.district or "Tamil Nadu"
    category = biz.category_rel.name if biz.category_rel else "வணிகம்"
    has_website = biz.website_status == WebsiteStatus.WEBSITE_FOUND and bool(biz.website_url)
    phone = biz.phone or ""

    if payload.language == "tamil":
        if payload.pitch_type == "website_pitch":
            text = (
                f"வணக்கம்! {district}-ல் உள்ள உங்கள் \"{b_name}\" நிறுவனத்திற்கு வாழ்த்துகள்!\n\n"
                f"இன்றைய காலகட்டத்தில் {district}-ல் 80% வாடிக்கையாளர்கள் தங்களுக்கு தேவையான {category} "
                f"தேடும்போது முதலில் கூகுளில் தான் பார்க்கிறார்கள்.\n\n"
                f"உங்கள் நிறுவனத்திற்கு நவீன, வேகமான Mobile-Friendly Website அமைத்து தருவதன் மூலம்:\n"
                f"✅ கூகுள் தேடலில் முதல் பக்கத்தில் வரலாம்\n"
                f"✅ வாடிக்கையாளர்கள் நேரடியாக WhatsApp-ல் ஆர்டர் செய்யலாம்\n"
                f"✅ உங்கள் நம்பகத்தன்மை (Brand Value) இருமடங்காகும்\n\n"
                f"உங்கள் நிறுவனத்திற்கென நாங்கள் உருவாக்கியுள்ள இலவச Demo Website Design பார்க்க விருப்பமா?\n"
                f"பதிலளிக்கவும், உடனடியாக காட்டுகிறோம்!"
            )
            subject = f"{b_name} நிறுவனத்திற்கு புதிய Website & Google Search Ranking வாய்ப்பு"
        elif payload.pitch_type == "ecommerce_catalog":
            text = (
                f"வணக்கம்! \"{b_name}\" வாடிக்கையாளர்கள் உங்கள் {category} பொருட்களை "
                f"நேரடியாக ஆன்லைனிலேயே பார்த்து, WhatsApp மூலம் ஆர்டர் செய்யும் Digital Catalog அமைத்து தருகிறோம்!\n\n"
                f"📱 மொபைலில் எளிதாக இயங்கும்\n"
                f"🛒 நேரடி WhatsApp Order Booking\n"
                f"💳 QR Code & UPI Payment வசதி\n\n"
                f"குறைந்த முதலீட்டில் உங்கள் விற்பனையை அதிகரிக்க விரும்பினால் பேசலாமா?"
            )
            subject = f"{b_name} - உங்கள் கடைக்கான நேரடி WhatsApp Catalog & Online Store"
        elif payload.pitch_type == "cold_email":
            text = (
                f"அன்புடையீர்,\n\n"
                f"{district}-ல் சிறப்பாக இயங்கி வரும் உங்கள் \"{b_name}\" நிறுவனத்தின் வளர்ச்சியை கண்டு மகிழ்ச்சி.\n\n"
                f"உங்கள் {category} துறையில் ஆன்லைன் மூலம் புதிய கஸ்டமர்களை கொண்டு சேர்க்கும் பிரத்யேக "
                f"Digital Growth திட்டத்தை நாங்கள் வைத்துள்ளோம். "
                f"ஏற்கனவே பல நிறுவனங்களுக்கு இதன் மூலம் மாதம் 30+ புதிய Leads கிடைக்கின்றன.\n\n"
                f"இதுகுறித்து 5 நிமிடங்கள் பேச உங்களுக்கு எப்போது வசதியாக இருக்கும்?\n\n"
                f"நன்றி,\n{agency_name}" + (f"\nPhone: {support_phone}" if support_phone else "") + (f"\nEmail: {support_email}" if support_email else "")
            )
            subject = f"{b_name} - Digital Growth & B2B Lead Generation"
        else:
            text = (
                f"வணக்கம்! {district}-ல் உள்ள மக்கள் கூகுளில் \"Best {category} in {district}\" என்று தேடும்போது "
                f"உங்கள் \"{b_name}\" முதல் 3 இடங்களில் வர வைக்க Google Business Profile & Local SEO செய்கிறோம்! "
                f"இலவச தணிக்கை அறிக்கை (Free Audit Report) பெற விரும்புகிறீர்களா?{contact_suffix}"
            )
            subject = f"{b_name} - Google Maps & Local Search Ranking Audit"

    elif payload.language == "tanglish":
        if payload.pitch_type == "website_pitch":
            text = (
                f"Vanakkam! {district}-la irukura unga \"{b_name}\"-kku official website illadha notice pannom.\n\n"
                f"Ippo daily hundreds of customers {district}-la {category} thedi Google-la search panranga. "
                f"Unga shop-kku oru modern, high-speed mobile website panni tharom:\n"
                f"✅ Direct WhatsApp Order Button\n"
                f"✅ Google First Page Ranking\n"
                f"✅ Products Photo Gallery\n\n"
                f"Unga business-kku oru Free Demo Design paaka viruppama? Reply pannunga, udane share panren!{contact_suffix}"
            )
            subject = f"{b_name} - Exclusive Website Demo for your Business"
        else:
            text = (
                f"Hello! Unga \"{b_name}\" business-ah Google Maps-la first position kondu vandhu, "
                f"daily genuine customer calls athigamaaga panna mudiyum. "
                f"Free SEO & Local Ranking details venuma? Let's discuss!{contact_suffix}"
            )
            subject = f"{b_name} - Google Local Ranking & Growth"

    else:  # English
        if payload.pitch_type == "website_pitch":
            text = (
                f"Hello,\n\n"
                f"We noticed that your business \"{b_name}\" in {district} does not currently have an active official website.\n\n"
                f"Over 75% of local buyers in {district} search online before visiting stores. "
                f"We specialize in designing high-converting, mobile-friendly websites with instant WhatsApp ordering and Google SEO.\n\n"
                f"Would you be interested in viewing a free, tailored website design demo for {b_name}?\n\n"
                f"Best regards,\n{agency_name}" + (f"\nPhone: {support_phone}" if support_phone else "")
            )
            subject = f"Website Design & Digital Visibility Demo for {b_name}"
        elif payload.pitch_type == "cold_email":
            text = (
                f"Hi {biz.client_name or 'there'},\n\n"
                f"I came across {b_name} while analyzing prominent {category} businesses in {district}.\n\n"
                f"We help local businesses generate high-intent inbound inquiries through automated local search positioning and modern digital presence.\n\n"
                f"Would you be open to a brief 5-minute call this week to see how we could drive 20-30 qualified leads every month for {b_name}?\n\n"
                f"Best regards,\n{agency_name}" + (f"\nPhone: {support_phone}" if support_phone else "") + (f"\nEmail: {support_email}" if support_email else "")
            )
            subject = f"Driving more local customer inquiries for {b_name}"
        else:
            text = (
                f"Hello!\n\n"
                f"Did you know {b_name} can capture 3x more local inquiries in {district} by appearing at the top of Google Local searches?\n\n"
                f"We have prepared a complimentary digital presence audit for {b_name}. Would you like us to share it over WhatsApp or Email?\n\n"
                f"Best regards,\n{agency_name}" + (f"\nPhone: {support_phone}" if support_phone else "")
            )
            subject = f"Local Search Visibility Audit for {b_name}"

    encoded_whatsapp = ""
    if phone:
        import urllib.parse
        clean_num = "".join(filter(str.isdigit, phone))
        if len(clean_num) == 10:
            clean_num = "91" + clean_num
        encoded_whatsapp = f"https://wa.me/{clean_num}?text={urllib.parse.quote_plus(text)}"

    return {
        "business_id": biz.id,
        "business_name": b_name,
        "district": district,
        "pitch_type": payload.pitch_type,
        "language": payload.language,
        "subject": subject,
        "message": text,
        "whatsapp_url": encoded_whatsapp,
    }
