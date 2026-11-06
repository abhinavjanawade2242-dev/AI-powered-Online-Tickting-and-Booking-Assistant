from fastapi import APIRouter
from app.api.endpoints.discovery import router as discovery_router, venues_router
from app.api.endpoints.availability import router as availability_router
from app.api.endpoints.bookings import router as bookings_router
from app.api.endpoints.pricing import router as pricing_router
from app.api.endpoints.tickets import router as tickets_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.offline import router as offline_router

api_router = APIRouter()

# Mount all endpoint routers
api_router.include_router(discovery_router)
api_router.include_router(venues_router)
api_router.include_router(availability_router)
api_router.include_router(bookings_router)
api_router.include_router(pricing_router)
api_router.include_router(tickets_router)
api_router.include_router(chat_router)
api_router.include_router(offline_router)

