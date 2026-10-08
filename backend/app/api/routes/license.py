from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.license import (
    activate_license,
    get_hardware_id,
    load_agency_branding,
    load_license,
    save_agency_branding,
)

router = APIRouter(prefix="/license", tags=["license & settings"])


class ActivateRequest(BaseModel):
    license_key: str


class BrandingUpdateRequest(BaseModel):
    agency_name: str | None = None
    tagline: str | None = None
    support_phone: str | None = None
    support_email: str | None = None
    currency: str | None = None


@router.get("/status")
def get_license_status():
    return load_license()


@router.post("/activate")
def activate_software(payload: ActivateRequest):
    res = activate_license(payload.license_key)
    if not res.get("valid"):
        raise HTTPException(status_code=400, detail=res.get("error", "Invalid license key"))
    return res


@router.get("/branding")
def get_branding():
    return load_agency_branding()


@router.post("/branding")
def update_branding(payload: BrandingUpdateRequest):
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return save_agency_branding(update_data)
