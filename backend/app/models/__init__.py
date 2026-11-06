import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class Venue(Base):
    __tablename__ = "venues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    amenities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    venue_id = Column(String(36), ForeignKey("venues.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)  # Concert, Comedy, Sports, Theater, etc.
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, CANCELLED, COMPLETED
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    venue = relationship("Venue", back_populates="events")
    ticket_tiers = relationship("TicketTier", back_populates="event", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="event")


class TicketTier(Base):
    """
    Ticket Tier represents seat categories, inventory slots and pricing for an event.
    Includes concurrency fields: `available_quantity` and `version` for optimistic locking.
    """
    __tablename__ = "ticket_tiers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # VIP, General Admission, Early Bird, Front Row
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)  # Optimistic concurrency check
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="ticket_tiers")
    bookings = relationship("Booking", back_populates="ticket_tier")
    tickets = relationship("DigitalTicket", back_populates="ticket_tier")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for guest checkout compatibility
    role = Column(String(50), default="customer", nullable=False)  # customer, organizer, admin
    preferred_language = Column(String(10), default="en", nullable=False)  # en, kn, hi
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="user")


class Booking(Base):
    """
    Booking record tracking lifecycle:
    PENDING (temporary inventory hold) -> CONFIRMED (paid/finalized) -> CANCELLED or EXPIRED
    """
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_reference = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(String(36), ForeignKey("events.id", ondelete="RESTRICT"), nullable=False, index=True)
    tier_id = Column(String(36), ForeignKey("ticket_tiers.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, CONFIRMED, CANCELLED, EXPIRED
    hold_expires_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(255), nullable=True)
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_status = Column(String(50), default="NONE", nullable=True)  # NONE, PENDING, REFUNDED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings", lazy="selectin")
    event = relationship("Event", back_populates="bookings", lazy="selectin")
    ticket_tier = relationship("TicketTier", back_populates="bookings", lazy="selectin")
    tickets = relationship("DigitalTicket", back_populates="booking", cascade="all, delete-orphan", lazy="selectin")


class DigitalTicket(Base):
    """
    Digital Ticket generated upon confirmed booking.
    Contains unique barcode/ticket code, gate-scan QR payload, and security signature.
    """
    __tablename__ = "digital_tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_code = Column(String(50), unique=True, index=True, nullable=False)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    tier_id = Column(String(36), ForeignKey("ticket_tiers.id", ondelete="RESTRICT"), nullable=False)
    seat_number = Column(String(50), nullable=True)
    qr_payload = Column(Text, nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, USED, CANCELLED
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="tickets")
    ticket_tier = relationship("TicketTier", back_populates="tickets")


class ChatSession(Base):
    """
    Conversation session recording the user's booking journey stage
    and context data across multiple turns.
    """
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True)  # Can be UUID or client session string
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    current_stage = Column(String(50), default="Discovery", nullable=False)
    context_data = Column(Text, default="{}", nullable=False)  # Serialized JSON state
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)  # JSON formatted tool calls
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

