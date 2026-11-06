#!/usr/bin/env python3
"""
Seed Member 3 Catalogue Dataset into Database
Technovate 2.0 | PS-07 AI-Powered Online Tickting and Booking Assistant
Member 3: Abhilash (Catalogue/Data + QA Support)
Task: AB-02 Seed Proposal Integration

Seeds all 5 multi-venue campus/civic facilities, 10 college/technical/cultural events,
and 21 INR ticket tiers directly into the database.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models import Venue, Event, TicketTier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("member3.seed")


async def seed_member3_data():
    catalogue_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_catalogue.json")
    if not os.path.exists(catalogue_path):
        catalogue_path = os.path.join("..", "data", "sample_catalogue.json")

    logger.info("Initializing database schema...")
    await init_db()

    with open(catalogue_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(Venue).where(Venue.id == "venue-campus-audi"))
        existing_venue = res.scalar_one_or_none()
        if existing_venue:
            logger.info("Member 3 catalogue already exists in database. Updating and verifying inventory...")
        else:
            logger.info("Seeding %d venues from Member 3 dataset...", len(data["venues"]))
            for v_data in data["venues"]:
                venue = Venue(
                    id=v_data["id"],
                    name=v_data["name"],
                    city=v_data.get("city", "Bengaluru"),
                    address=v_data["address"],
                    capacity=v_data["capacity"],
                    description=v_data.get("description", ""),
                    amenities=v_data.get("amenities", "")
                )
                session.add(venue)
            await session.commit()
            logger.info("Venues committed successfully.")

        # Seed events and ticket tiers
        for ev_data in data["events"]:
            res_ev = await session.execute(select(Event).where(Event.id == ev_data["id"]))
            existing_ev = res_ev.scalar_one_or_none()

            start_dt = datetime.fromisoformat(ev_data["start_time"].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(ev_data["end_time"].replace("Z", "+00:00"))

            if not existing_ev:
                event = Event(
                    id=ev_data["id"],
                    venue_id=ev_data["venue_id"],
                    title=ev_data["title"],
                    description=ev_data["description"],
                    category=ev_data["category"],
                    start_time=start_dt,
                    end_time=end_dt,
                    status=ev_data.get("status", "ACTIVE"),
                    image_url=ev_data.get("image_url")
                )
                session.add(event)
                await session.flush()
                logger.info("Added event: %s (%s)", event.title, event.category)
            else:
                logger.info("Event '%s' already exists.", ev_data["id"])

            for tier_data in ev_data.get("ticket_tiers", []):
                res_tier = await session.execute(select(TicketTier).where(TicketTier.id == tier_data["id"]))
                existing_tier = res_tier.scalar_one_or_none()
                if not existing_tier:
                    tier = TicketTier(
                        id=tier_data["id"],
                        event_id=ev_data["id"],
                        name=tier_data["name"],
                        price=tier_data["price"],
                        currency=tier_data.get("currency", "INR"),
                        total_quantity=tier_data["total_quantity"],
                        available_quantity=tier_data["available_quantity"],
                        version=1
                    )
                    session.add(tier)
                    logger.info("  -> Added tier: %s (₹%.2f, %d seats)", tier.name, tier.price, tier.total_quantity)

        await session.commit()
        logger.info("✅ All Member 3 catalogue records successfully seeded into the database!")


if __name__ == "__main__":
    asyncio.run(seed_member3_data())
