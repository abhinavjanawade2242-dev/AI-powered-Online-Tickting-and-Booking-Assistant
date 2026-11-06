#!/usr/bin/env python3
"""
Catalogue Validation Script
Technovate 2.0 | PS-07 AI-Powered Online Ticketing and Booking Assistant
Member 3: Abhilash (Catalogue/Data + QA Support)
Task: AB-03 Validate Catalogue

Validates schema constraints, referential integrity, price/inventory boundaries,
and temporal consistency for all venues, events, and ticket tiers in the catalogue dataset.
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Any


def validate_catalogue(file_path: str) -> bool:
    print("=" * 70)
    print("PS-07 CATALOGUE DATA INTEGRITY & VALIDATION AUDIT")
    print(f"Target Dataset: {file_path}")
    print("=" * 70)

    if not os.path.exists(file_path):
        print(f"❌ [CRITICAL] File not found: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ [CRITICAL] Invalid JSON syntax: {e}")
            return False

    errors: List[str] = []
    warnings: List[str] = []
    venues: List[Dict[str, Any]] = data.get("venues", [])
    events: List[Dict[str, Any]] = data.get("events", [])

    print(f"Loaded {len(venues)} venues and {len(events)} events.")
    print("-" * 70)

    # 1. Venues Validation
    venue_ids = set()
    venue_capacities = {}
    for idx, v in enumerate(venues):
        vid = v.get("id")
        if not vid or not isinstance(vid, str):
            errors.append(f"Venue #{idx}: missing or non-string 'id'")
        elif vid in venue_ids:
            errors.append(f"Duplicate venue ID: '{vid}'")
        else:
            venue_ids.add(vid)

        name = v.get("name")
        if not name or len(name.strip()) < 3:
            errors.append(f"Venue '{vid}': name is too short or missing")

        cat = v.get("category")
        if not cat:
            errors.append(f"Venue '{vid}': category is missing")

        cap = v.get("capacity")
        if not isinstance(cap, int) or cap <= 0:
            errors.append(f"Venue '{vid}': capacity must be a positive integer (got {cap})")
        else:
            venue_capacities[vid] = cap

        addr = v.get("address")
        if not addr or len(addr.strip()) < 5:
            errors.append(f"Venue '{vid}': address is missing or too brief")

    print(f"✓ Checked {len(venues)} venues: {len(venue_ids)} unique venue IDs.")

    # 2. Events & Ticket Tiers Validation
    event_ids = set()
    tier_ids = set()
    allowed_categories = {"Technical", "Cultural", "Sports", "Workshop", "Conference", "Comedy", "Concert"}
    allowed_statuses = {"ACTIVE", "INACTIVE", "CANCELLED", "COMPLETED"}

    for idx, ev in enumerate(events):
        eid = ev.get("id")
        if not eid or not isinstance(eid, str):
            errors.append(f"Event #{idx}: missing or non-string 'id'")
        elif eid in event_ids:
            errors.append(f"Duplicate event ID: '{eid}'")
        else:
            event_ids.add(eid)

        # Referential integrity: venue_id
        vid = ev.get("venue_id")
        if not vid or vid not in venue_ids:
            errors.append(f"Event '{eid}': references unknown venue_id '{vid}'")

        # Title
        title = ev.get("title")
        if not title or len(title.strip()) < 5:
            errors.append(f"Event '{eid}': title is missing or too short (< 5 chars)")

        # Description
        desc = ev.get("description")
        if not desc or len(desc.strip()) < 15:
            errors.append(f"Event '{eid}': description is missing or too brief (< 15 chars)")

        # Category
        cat = ev.get("category")
        if cat not in allowed_categories:
            warnings.append(f"Event '{eid}': category '{cat}' is not in standard set {allowed_categories}")

        # Status
        status = ev.get("status")
        if status not in allowed_statuses:
            errors.append(f"Event '{eid}': status '{status}' not in allowed statuses {allowed_statuses}")

        # Date & Time parsing
        start_str = ev.get("start_time")
        end_str = ev.get("end_time")
        start_dt = None
        end_dt = None

        try:
            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        except Exception:
            errors.append(f"Event '{eid}': invalid ISO 8601 start_time '{start_str}'")

        try:
            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except Exception:
            errors.append(f"Event '{eid}': invalid ISO 8601 end_time '{end_str}'")

        if start_dt and end_dt:
            if start_dt >= end_dt:
                errors.append(f"Event '{eid}': start_time ({start_str}) must be strictly earlier than end_time ({end_str})")

        # Ticket tiers
        tiers = ev.get("ticket_tiers", [])
        if not tiers or len(tiers) == 0:
            errors.append(f"Event '{eid}': must have at least one ticket tier")

        event_capacity_sum = 0
        for tidx, tier in enumerate(tiers):
            tid = tier.get("id")
            if not tid or not isinstance(tid, str):
                errors.append(f"Event '{eid}' tier #{tidx}: missing or non-string 'id'")
            elif tid in tier_ids:
                errors.append(f"Duplicate ticket tier ID: '{tid}'")
            else:
                tier_ids.add(tid)

            tname = tier.get("name")
            if not tname or len(tname.strip()) < 2:
                errors.append(f"Tier '{tid}': name is missing or too short")

            price = tier.get("price")
            if not isinstance(price, (int, float)) or price < 0:
                errors.append(f"Tier '{tid}': price must be >= 0 (got {price})")

            currency = tier.get("currency")
            if currency != "INR":
                errors.append(f"Tier '{tid}': currency must be 'INR' (got '{currency}')")

            total_qty = tier.get("total_quantity")
            avail_qty = tier.get("available_quantity")

            if not isinstance(total_qty, int) or total_qty <= 0:
                errors.append(f"Tier '{tid}': total_quantity must be positive integer (got {total_qty})")
            else:
                event_capacity_sum += total_qty

            if not isinstance(avail_qty, int) or avail_qty < 0:
                errors.append(f"Tier '{tid}': available_quantity must be non-negative integer (got {avail_qty})")
            elif isinstance(total_qty, int) and avail_qty > total_qty:
                errors.append(f"Tier '{tid}': available_quantity ({avail_qty}) exceeds total_quantity ({total_qty})")

        # Check total event capacity vs venue capacity
        venue_cap = venue_capacities.get(vid)
        if venue_cap and event_capacity_sum > venue_cap:
            warnings.append(
                f"Event '{eid}': sum of tier quantities ({event_capacity_sum}) exceeds physical venue capacity ({venue_cap}) for venue '{vid}'"
            )

    print(f"✓ Checked {len(events)} events and {len(tier_ids)} ticket tiers.")
    print("-" * 70)

    # 3. Output Summary
    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")
        print("-" * 70)

    if errors:
        print(f"❌ VALIDATION FAILED WITH {len(errors)} ERRORS:")
        for err in errors:
            print(f"   ✖ {err}")
        print("=" * 70)
        return False

    print("✅ VALIDATION SUCCESSFUL: All constraints, schema checks, and business rules PASSED!")
    print(f"   • Venues: {len(venues)} verified")
    print(f"   • Events: {len(events)} verified")
    print(f"   • Ticket Tiers: {len(tier_ids)} verified")
    print(f"   • Currency: All tiers confirmed in INR (₹)")
    print(f"   • Referential Integrity: 100% valid venue associations")
    print(f"   • Inventory Boundaries: 0 <= available_quantity <= total_quantity for all tiers")
    print("=" * 70)
    return True


if __name__ == "__main__":
    default_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_catalogue.json")
    if not os.path.exists(default_path):
        default_path = os.path.join("..", "data", "sample_catalogue.json")
    if len(sys.argv) > 1:
        default_path = sys.argv[1]

    success = validate_catalogue(default_path)
    sys.exit(0 if success else 1)

