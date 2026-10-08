"""SRA Business Lead Finder - Hardware ID & Cryptographic License Activation System.

Protects the software from unauthorized distribution.
Binds licenses to client machine hardware (CPU / Motherboard / Windows GUID).
"""

import hashlib
import hmac
import json
import os
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

MASTER_SALT = "SRA_LEAD_FINDER_MASTER_SECRET_2026_TAMILNADU"
LICENSE_FILE = Path(os.path.expandvars(r"%LOCALAPPDATA%\SRA Lead Finder\license.json"))
CONFIG_FILE = Path(os.path.expandvars(r"%LOCALAPPDATA%\SRA Lead Finder\agency_config.json"))


def get_raw_machine_guid() -> str:
    """Retrieve unique machine identifier across Windows installations."""
    # 1. Try Windows Registry MachineGuid
    if platform.system() == "Windows":
        try:
            cmd = ['reg', 'query', r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography', '/v', 'MachineGuid']
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                if "MachineGuid" in line:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        return parts[-1].strip()
        except Exception:
            pass

        # 2. Try WMIC CSPRODUCT UUID
        try:
            cmd = ['wmic', 'csproduct', 'get', 'uuid']
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            lines = [l.strip() for l in out.splitlines() if l.strip() and "UUID" not in l]
            if lines and lines[0] and lines[0] != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
                return lines[0]
        except Exception:
            pass

    # 3. Fallback: MAC node
    return str(uuid.getnode())


def get_hardware_id() -> str:
    """Generate a clean, user-friendly Hardware ID (e.g. SRA-7A9B-4D1C-88E2)."""
    raw_id = get_raw_machine_guid()
    h = hashlib.sha256(f"{raw_id}:{MASTER_SALT}".encode("utf-8")).hexdigest().upper()
    return f"SRA-{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


def compute_license_signature(hardware_id: str, license_type: str = "LIFETIME") -> str:
    """Cryptographically sign a Hardware ID and License Type."""
    key = MASTER_SALT.encode("utf-8")
    msg = f"{hardware_id.strip().upper()}:{license_type.strip().upper()}".encode("utf-8")
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest().upper()
    # Format as 4 groups of 4: SRA-XXXX-XXXX-XXXX-XXXX
    return f"LIC-{sig[0:4]}-{sig[4:8]}-{sig[8:12]}-{sig[12:16]}"


def verify_license_key(hardware_id: str, license_key: str) -> dict:
    """Check if the provided key matches LIFETIME, 1YEAR, or 30DAYS signature."""
    clean_key = license_key.strip().upper()
    hw = hardware_id.strip().upper()

    for l_type in ["LIFETIME", "1YEAR", "30DAYS", "PRO"]:
        expected = compute_license_signature(hw, l_type)
        if clean_key == expected:
            return {
                "valid": True,
                "license_type": l_type,
                "hardware_id": hw,
                "created_at": datetime.utcnow().isoformat(),
            }

    # Universal master override key (for emergency support / owner use)
    master_key = compute_license_signature("SRA-UNIVERSAL-MASTER", "LIFETIME")
    if clean_key == master_key:
        return {
            "valid": True,
            "license_type": "LIFETIME (MASTER)",
            "hardware_id": hw,
            "created_at": datetime.utcnow().isoformat(),
        }

    return {"valid": False, "error": "Invalid License Key for this machine."}


def load_license() -> dict:
    """Load local license state, providing a generous default trial if unactivated."""
    hwid = get_hardware_id()
    if LICENSE_FILE.exists():
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("hardware_id") == hwid and data.get("is_activated"):
                    return {
                        "hardware_id": hwid,
                        "is_activated": True,
                        "license_type": data.get("license_type", "LIFETIME"),
                        "license_key": data.get("license_key", ""),
                        "activated_at": data.get("activated_at"),
                        "status": "ACTIVATED",
                    }
        except Exception:
            pass

    # Unactivated / Free Trial Mode
    return {
        "hardware_id": hwid,
        "is_activated": False,
        "license_type": "TRIAL",
        "license_key": "",
        "status": "TRIAL_ACTIVE",
        "trial_message": "Evaluation Mode • Activate for Unlimited B2B Discovery & Full Commercial Rights",
    }


def activate_license(license_key: str) -> dict:
    """Attempt activation using input key."""
    hwid = get_hardware_id()
    check = verify_license_key(hwid, license_key)
    if not check["valid"]:
        return check

    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "is_activated": True,
        "license_key": license_key.strip().upper(),
        "hardware_id": hwid,
        "license_type": check["license_type"],
        "activated_at": datetime.utcnow().isoformat(),
    }
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return {"valid": True, "message": "Software successfully activated!", "license": payload}


def load_agency_branding() -> dict:
    """Load customized agency name, contact details, and tagline."""
    defaults = {
        "agency_name": "SRA Software Solutions",
        "tagline": "Find. Verify. Connect. • Tamil Nadu Edition",
        "support_phone": "+91 98400 12345",
        "support_email": "support@srasoftware.com",
        "currency": "INR",
        "lead_export_watermark": "Generated by SRA Lead Finder",
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults


def save_agency_branding(new_config: dict) -> dict:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    current = load_agency_branding()
    current.update(new_config)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    return current
