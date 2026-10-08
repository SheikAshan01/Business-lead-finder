#!/usr/bin/env python3
"""SRA Business Lead Finder - Vendor License Key Generator.

Run this script to generate official customer activation keys.

Usage:
  python scripts/generate_license.py --hwid SRA-XXXX-XXXX-XXXX-XXXX --type LIFETIME --client "Chennai Agency"
  python scripts/generate_license.py --hwid current  (Activates this computer)
"""

import argparse
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.license import (
    activate_license,
    compute_license_signature,
    get_hardware_id,
    load_license,
)


def main():
    parser = argparse.ArgumentParser(description="SRA Lead Finder - License Generator")
    parser.add_argument("--hwid", type=str, default="current", help="Client's Hardware ID (or 'current')")
    parser.add_argument("--type", type=str, default="LIFETIME", choices=["LIFETIME", "1YEAR", "30DAYS", "PRO"], help="License Type")
    parser.add_argument("--client", type=str, default="Valued Client", help="Buyer or Company Name")
    parser.add_argument("--activate-now", action="store_true", help="Instantly activate this machine with the key")

    args = parser.parse_args()

    target_hwid = get_hardware_id() if args.hwid == "current" else args.hwid.strip().upper()
    license_key = compute_license_signature(target_hwid, args.type)

    print("=" * 64)
    print("  SRA BUSINESS LEAD FINDER - OFFICIAL LICENSE KEY GENERATOR")
    print("=" * 64)
    print(f"  Client Name  : {args.client}")
    print(f"  Hardware ID  : {target_hwid}")
    print(f"  License Type : {args.type}")
    print(f"  LICENSE KEY  : {license_key}")
    print("=" * 64)

    if args.activate_now or args.hwid == "current":
        res = activate_license(license_key)
        print(f"  Local Machine Status: {res.get('message', 'Activated!')}")
        print("=" * 64)

    print("\nCopy & send this key to your customer:")
    print(f"Hardware ID: {target_hwid}")
    print(f"License Key: {license_key}")
    print()


if __name__ == "__main__":
    main()
