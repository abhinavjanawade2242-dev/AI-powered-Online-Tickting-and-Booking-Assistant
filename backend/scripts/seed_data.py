import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models import Venue, Event, TicketTier, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticketing.seed")


async def seed():
    logger.info("Initializing database schema...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        existing_venue = await session.execute(select(Venue))
        if existing_venue.scalars().first():
            logger.info("Database already seeded with venue and event data. Skipping.")
            return

        logger.info("Seeding venues...")
        msg = Venue(
            id="venue-msg-ny",
            name="Madison Square Garden",
            description="The World's Most Famous Arena, hosting iconic concerts and athletic spectacles.",
            address="4 Pennsylvania Plaza",
            city="New York",
            capacity=20789,
            amenities="VIP Lounges, Premium Catering, Wheelchair Accessible, Coat Check"
        )
        chicago_theatre = Venue(
            id="venue-chicago-th",
            name="The Chicago Theatre",
            description="Historic landmark auditorium renowned for top-tier comedy and acoustic concerts.",
            address="175 N State St",
            city="Chicago",
            capacity=3600,
            amenities="Full Bar, Historic Grand Lobby, Balcony Suites"
        )
        red_rocks = Venue(
            id="venue-red-rocks",
            name="Red Rocks Amphitheatre",
            description="Spectacular open-air rock structure amphitheatre with breathtaking natural acoustics.",
            address="18300 W Alameda Pkwy",
            city="Denver",
            capacity=9525,
            amenities="Open Air Seating, Tailgate Area, Visitor Center"
        )
        session.add_all([msg, chicago_theatre, red_rocks])
        await session.flush()

        logger.info("Seeding events & ticket tiers...")
        now = datetime.utcnow()

        # Event 1: Coldplay Concert
        coldplay = Event(
            id="event-coldplay-nyc",
            venue_id=msg.id,
            title="Coldplay: Music of the Spheres Tour",
            description="Experience an exhilarating night of lights, cosmic soundscapes, and timeless anthems.",
            category="Concert",
            start_time=now + timedelta(days=14, hours=19),
            end_time=now + timedelta(days=14, hours=23),
            status="ACTIVE",
            image_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745"
        )
        # Event 2: Comedy Night
        comedy = Event(
            id="event-comedy-chi",
            venue_id=chicago_theatre.id,
            title="Dave Chappelle & Friends Live Comedy Special",
            description="An uncensored, unforgettable evening of razor-sharp stand-up comedy.",
            category="Comedy",
            start_time=now + timedelta(days=7, hours=20),
            end_time=now + timedelta(days=7, hours=22, minutes=30),
            status="ACTIVE",
            image_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819"
        )
        # Event 3: Electronic Music Festival
        festival = Event(
            id="event-red-rocks-edm",
            venue_id=red_rocks.id,
            title="Odesza: The Last Goodbye Live at Red Rocks",
            description="Immersive cinematic live performance featuring drumlines, brass, and stunning visuals.",
            category="Concert",
            start_time=now + timedelta(days=21, hours=18),
            end_time=now + timedelta(days=21, hours=23, minutes=45),
            status="ACTIVE",
            image_url="https://images.unsplash.com/photo-1492684223066-81342ee5ff30"
        )
        session.add_all([coldplay, comedy, festival])
        await session.flush()

        logger.info("Seeding ticket tiers with inventory slots...")
        tiers = [
            # Coldplay Tiers
            TicketTier(
                id="tier-coldplay-vip",
                event_id=coldplay.id,
                name="VIP Floor Access",
                price=2500.00,
                currency="INR",
                total_quantity=20,
                available_quantity=20,
            ),
            TicketTier(
                id="tier-coldplay-ga",
                event_id=coldplay.id,
                name="General Admission Lower Bowl",
                price=1200.00,
                currency="INR",
                total_quantity=100,
                available_quantity=100,
            ),
            TicketTier(
                id="tier-coldplay-balcony",
                event_id=coldplay.id,
                name="Upper Balcony Reserved",
                price=650.00,
                currency="INR",
                total_quantity=150,
                available_quantity=150,
            ),

            # Comedy Tiers
            TicketTier(
                id="tier-comedy-front",
                event_id=comedy.id,
                name="Front Row Orchestra",
                price=1850.00,
                currency="INR",
                total_quantity=15,
                available_quantity=15,
            ),
            TicketTier(
                id="tier-comedy-standard",
                event_id=comedy.id,
                name="Standard Seating",
                price=850.00,
                currency="INR",
                total_quantity=80,
                available_quantity=80,
            ),

            # Festival Tiers
            TicketTier(
                id="tier-odesza-early",
                event_id=festival.id,
                name="Early Bird Amphitheatre Pass",
                price=950.00,
                currency="INR",
                total_quantity=50,
                available_quantity=50,
            ),
            TicketTier(
                id="tier-odesza-vip",
                event_id=festival.id,
                name="VIP Backstage & Soundboard Access",
                price=3200.00,
                currency="INR",
                total_quantity=10,
                available_quantity=10,
            ),
        ]
        session.add_all(tiers)

        # Seed sample customer
        customer = User(
            id="user-sample-01",
            full_name="Sarah Jenkins",
            email="sarah.jenkins@example.com",
            phone="+1-212-555-0182"
        )
        session.add(customer)

        await session.commit()
        logger.info("Database seeding completed successfully! Seeded 3 Venues, 3 Events, 7 Ticket Tiers.")


if __name__ == "__main__":
    asyncio.run(seed())

