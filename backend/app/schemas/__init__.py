from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ==============================================================================
# Common Response Schemas
# ==============================================================================

class ApiResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# ==============================================================================
# Venue Schemas
# ==============================================================================

class VenueBase(BaseModel):
    name: str = Field(..., example="Madison Square Garden")
    description: Optional[str] = Field(None, example="Iconic multi-purpose indoor arena")
    address: str = Field(..., example="4 Pennsylvania Plaza")
    city: str = Field(..., example="New York")
    capacity: int = Field(..., ge=1, example=20000)
    amenities: Optional[str] = Field(None, example="Parking, VIP Lounge, Wheelchair Access, Food Court")


class VenueCreate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Ticket Tier & Slot Schemas (Stage 3 & 4)
# ==============================================================================

class TicketTierBase(BaseModel):
    name: str = Field(..., example="General Admission")
    price: float = Field(..., ge=0.0, example=850.00)
    currency: str = Field(default="INR", example="INR")
    total_quantity: int = Field(..., ge=1, example=500)


class TicketTierCreate(TicketTierBase):
    pass


class TicketTierResponse(TicketTierBase):
    id: str
    event_id: str
    available_quantity: int
    version: int
    model_config = ConfigDict(from_attributes=True)


class TicketTierAvailability(BaseModel):
    tier_id: str
    name: str
    price: float
    currency: str
    available_quantity: int
    is_sold_out: bool
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Event Schemas (Stage 1 & 2: Discovery & Recommendation)
# ==============================================================================

class EventBase(BaseModel):
    title: str = Field(..., example="Coldplay: Music of the Spheres World Tour")
    description: Optional[str] = Field(None, example="Live stadium performance with dazzling light show")
    category: str = Field(..., example="Concert")
    start_time: datetime
    end_time: datetime
    status: str = Field(default="ACTIVE", example="ACTIVE")
    image_url: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1470225620780-dba8ba36b745")


class EventCreate(EventBase):
    venue_id: str
    ticket_tiers: List[TicketTierCreate] = []


class EventResponse(EventBase):
    id: str
    venue_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventResponse):
    venue: Optional[VenueResponse] = None
    ticket_tiers: List[TicketTierResponse] = []
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    total_available_tickets: Optional[int] = None


# ==============================================================================
# Customer Schemas
# ==============================================================================

class CustomerBase(BaseModel):
    full_name: str = Field(..., example="Jane Doe")
    email: EmailStr = Field(..., example="jane.doe@example.com")
    phone: Optional[str] = Field(None, example="+1-555-0199")


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: str
    role: str = "customer"
    preferred_language: str = "en"
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Authentication & User Management Schemas
# ==============================================================================

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, example="Adithya Gowda")
    email: EmailStr = Field(..., example="adithya@example.com")
    password: str = Field(..., min_length=6, max_length=100, example="SecurePass123!")
    phone: Optional[str] = Field(None, example="+91-9876543210")
    role: Optional[str] = Field("customer", description="Role: customer, organizer, or admin")
    preferred_language: Optional[str] = Field("en", description="Preferred language: en, kn, or hi")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="adithya@example.com")
    password: str = Field(..., example="SecurePass123!")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: str
    email: str
    full_name: str
    role: str
    preferred_language: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    preferred_language: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None


# ==============================================================================
# Event Management Operations (Organizer & Admin CRUD)
# ==============================================================================

class EventCreateRequest(BaseModel):
    venue_id: str = Field(..., example="venue-tech-hub")
    title: str = Field(..., min_length=5, max_length=255, example="Bangalore AI & Web3 Summit 2026")
    description: Optional[str] = Field(None, example="Annual summit bringing together student developers and founders.")
    category: str = Field(..., example="Technical")
    start_time: datetime = Field(..., example="2026-12-15T09:00:00")
    end_time: datetime = Field(..., example="2026-12-15T18:00:00")
    image_url: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1540575467063-178a50c2df87")
    ticket_tiers: List[TicketTierCreate] = []


class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    image_url: Optional[str] = None


# ==============================================================================
# WhatsApp Cloud API Schemas
# ==============================================================================

class WhatsAppSimulateRequest(BaseModel):
    sender_phone: str = Field(..., example="919876543210", description="Sender phone number with country code")
    message: str = Field(..., example="ನಮಸ್ಕಾರ, ಬೆಂಗಳೂರಿನಲ್ಲಿ ನಡೆಯುವ ಹ್ಯಾಕಥಾನ್ ತಿಳಿಸಿ", description="Message text")


class WhatsAppSimulateResponse(BaseModel):
    sender_phone: str
    session_id: str
    incoming_message: str
    assistant_reply: str
    current_stage: str
    language: str
    delivered: bool = True
    delivery_channel: str = "Meta WhatsApp Cloud API (Simulated)"


# ==============================================================================
# Booking Schemas (Stage 4 & 5: Selection & Booking)
# ==============================================================================

class BookingReservationRequest(BaseModel):
    """
    Step 4/5: Customer selects ticket type and quantity.
    Acquires distributed lock and reserves tickets with a temporary hold.
    """
    event_id: str = Field(..., description="Target event ID")
    tier_id: str = Field(..., description="Ticket tier / category ID")
    quantity: int = Field(..., ge=1, le=10, description="Number of tickets requested")
    customer_name: str = Field(..., example="John Smith")
    customer_email: EmailStr = Field(..., example="john.smith@example.com")
    customer_phone: Optional[str] = Field(None, example="+1-555-1234")
    promo_code: Optional[str] = Field(None, description="Optional coupon or promo code (e.g., TECH20, STUDENT10)", example="TECH20")


class BookingConfirmRequest(BaseModel):
    """
    Step 5/6: Finalizes booking and generates digital tickets.
    """
    booking_reference: str = Field(..., example="BK-83F1A2")
    payment_reference: Optional[str] = Field(None, example="PAY-ONLINE-9871")


class BookingCancelRequest(BaseModel):
    """
    Step 7: Post-booking cancellation request.
    """
    booking_reference: str = Field(..., example="BK-83F1A2")
    reason: Optional[str] = Field("Customer requested cancellation", example="Schedule conflict")


class OfflineSyncRequest(BaseModel):
    """
    Offline Queue Replay Request.
    Submitted by client after network reconnection to revalidate and hold seats.
    """
    client_request_id: str = Field(..., example="c1f7a28e-4a89-4e76-8f3b-5a123456789a")
    event_id: str = Field(..., example="event-technovate-hack")
    tier_id: str = Field(..., example="tier-tech-early")
    quantity: int = Field(..., ge=1, le=10, example=2)
    customer_name: str = Field(..., example="Adithya Frontend")
    customer_email: EmailStr = Field(..., example="adithya@example.com")
    queued_offline_at: Optional[datetime] = None


class OfflineSyncResponse(BaseModel):
    client_request_id: str
    status: str  # ACCEPTED_LOCKED or REJECTED_SOLD_OUT
    booking_reference: Optional[str] = None
    hold_expires_at: Optional[datetime] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = "INR"
    checkout_url: Optional[str] = None
    message: str


class DigitalTicketResponse(BaseModel):
    id: str
    ticket_code: str
    tier_id: str
    tier_name: Optional[str] = None
    qr_payload: str
    status: str
    issued_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentSimulationRequest(BaseModel):
    """
    Sandbox Payment Simulation Request.
    Supports deterministic test outcomes: SUCCESS, FAILURE, PENDING.
    """
    simulated_outcome: str = Field("SUCCESS", description="One of: SUCCESS, FAILURE, PENDING")
    payment_method: Optional[str] = Field("SIMULATED_UPI", example="SIMULATED_UPI")


class PaymentSimulationResponse(BaseModel):
    booking_reference: str
    status: str
    payment_status: str
    simulated_outcome: str
    total_amount: float
    currency: str
    message: str
    tickets: List[DigitalTicketResponse] = []


class BookingResponse(BaseModel):
    id: str
    booking_reference: str
    event_id: str
    event_title: Optional[str] = None
    tier_id: str
    tier_name: Optional[str] = None
    quantity: int
    unit_price: float
    total_amount: float
    currency: str
    status: str
    hold_expires_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    refund_amount: Optional[float] = None
    refund_status: Optional[str] = None
    customer: Optional[CustomerResponse] = None
    tickets: List[DigitalTicketResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Pricing Schemas
# ==============================================================================

class PriceQuoteRequest(BaseModel):
    tier_id: str = Field(..., example="tier-tech-early", description="Ticket tier ID")
    quantity: int = Field(..., ge=1, le=10, example=2, description="Number of tickets requested")
    promo_code: Optional[str] = Field(None, example="TECH20", description="Promo discount code (e.g., TECH20, STUDENT10, EARLYBIRD, FREEPASS)")


class PriceQuoteResponse(BaseModel):
    unit_price: float
    quantity: int
    base_amount: float
    discount_amount: float
    discount_description: Optional[str] = None
    convenience_fee: float
    tax_amount: float
    total_payable: float
    currency: str = "INR"
    is_free: bool


# ==============================================================================
# AI Conversational Chat Schemas
# ==============================================================================

class ChatRequest(BaseModel):
    message: str = Field(..., example="Find tech events in Bengaluru")
    session_id: Optional[str] = Field(None, description="Session ID for ongoing conversation context")
    user_id: Optional[str] = Field(None, description="Optional identified user ID")
    language: Optional[str] = Field("en", description="Preferred language: 'en' (English), 'kn' (Kannada), 'hi' (Hindi)")


class ChatActionSuggestion(BaseModel):
    label: str
    action_type: str
    payload: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    session_id: str
    message: str
    current_stage: str = Field(..., description="One of: Discovery, Recommendation, Availability, Selection, Booking, Confirmation, Post-booking")
    language: str = Field(default="en", description="Response language: 'en', 'kn', or 'hi'")
    context_data: Dict[str, Any] = {}
    suggested_actions: List[ChatActionSuggestion] = []
    tool_calls_executed: List[str] = []

