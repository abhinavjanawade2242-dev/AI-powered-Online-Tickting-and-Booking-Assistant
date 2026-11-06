# AB-05: Exploratory QA Audit & Prioritized Bug Report

**Technovate 2.0 | Problem Statement PS-07: AI-Powered Online Ticketing and Booking Assistant**  
**Author:** Deepak & Manohar (Data & QA) (Member 3 â€“ Catalogue/Data + QA Support)  
**Task ID:** AB-05 Exploratory QA  
**Version:** 1.0 | Feature Audit & Defect Tracking  

---

## 1. Feature Audit Worksheet (Section 5 Standard)

This audit inspects existing implementation status across the 7 core functional modules defined in the PS-07 Team Guide:

| Feature / Module | Status | Evidence / File Paths | What was Missing or Fixed? | Next Action / Owner |
| :--- | :--- | :--- | :--- | :--- |
| **Event / venue catalogue** | Existing & Verified | `app/api/endpoints/discovery.py`<br>`data/sample_catalogue.json`<br>`scripts/seed_member3_catalogue.py` | Initial catalogue lacked multi-venue student events. Added 5 venues, 10 events, and 21 INR tiers. | Member 1 (Product Owner) to render cards in UI; Deepak (Backend) to maintain DB migrations. |
| **Search and filters** | Existing & Verified | `app/services/event_service.py`<br>`tests/test_catalogue_search.py` | Query parameter naming mismatch (`q` vs `query` vs `search`) and missing `venue_id` filter. Added alias support. | Member 1 (Product Owner) to hook frontend search bar to `/api/v1/events?search=...`. |
| **Booking and inventory** | Existing & Verified | `app/services/booking_service.py`<br>`tests/test_concurrency_lock.py` | Concurrency lock using Redis + PostgreSQL row-level lock. Stress tested with 30 concurrent users; 0 overbooking. | Deepak (Backend) to verify timeout configurations. |
| **Simulated payment** | Existing & Verified | `app/services/booking_service.py`<br>`app/api/endpoints/bookings.py` | Clear simulated outcome states (`SUCCESS`, `FAILED`, `PENDING`). No real payment credentials. | Member 1 (Product Owner) to display simulation banner on checkout screen. |
| **Ticket generation / retrieval** | Existing & Verified | `app/services/ticket_service.py`<br>`app/api/endpoints/tickets.py` | QR signature verification failed due to re-hashing with a fresh timestamp. Fixed HMAC/SHA-256 signature verification. | Deepak (Backend) to monitor gate scanner performance. |
| **AI assistant / languages** | Existing & Verified | `app/ai/agent.py`<br>`app/ai/tools.py`<br>`app/static/index.html` | Chat tools previously displayed `$`. Updated AI agent to output prices in `â‚¹` (INR). | Deepak & Adithya (AI & Frontend) to add Kannada and Hindi localized prompt datasets. |
| **Authentication / admin** | Partially Implemented | `app/models/__init__.py`<br>`docs/03_Backend_API_and_Database_Specification.docx` | Data models and session structure exist. User auth endpoints are proposed in spec. | Deepak (Backend) to implement JWT auth endpoints in `/api/auth`. |

---

## 2. Prioritized Defect & Fix Register

### Defect BUG-01: QR Code Gate Verification Signature Mismatch
- **Severity**: **HIGH** (Breaks Stage 6/7 gate check-in)
- **Component**: `backend/app/services/ticket_service.py`
- **Steps to Reproduce**:
  1. Confirm a booking and receive a digital ticket with `qr_payload`.
  2. Call `POST /api/v1/tickets/verify` with `{ "qr_payload": ticket.qr_payload }`.
- **Expected Result**: `{"is_valid": true, "status": "ACTIVE"}`.
- **Actual Result**: Returned `{"is_valid": false, "status": "INVALID_SIGNATURE"}`.
- **Root Cause**: `verify_qr_payload` called `generate_qr_payload()`, which generated a new `int(time.time())` timestamp, invalidating the SHA-256 digest.
- **Fix Applied**: Updated `verify_qr_payload` to parse the payload parts and verify the existing signature against `hashlib.sha256(raw_payload.encode()).hexdigest()[:12]` using `hmac.compare_digest`.
- **Verification**: `test_stage_4_5_6_7_booking_lifecycle` passes 100%.

---

### Defect BUG-02: Search Parameter Naming Inconsistency Across Contract
- **Severity**: **MEDIUM** (Inter-member contract mismatch)
- **Component**: `backend/app/api/endpoints/discovery.py` & `event_service.py`
- **Steps to Reproduce**:
  1. Frontend calls `GET /api/v1/events?search=hackathon` or `GET /api/v1/events?q=hackathon`.
  2. Backend discovery endpoint only looked for `query`.
- **Expected Result**: Events matching `hackathon` returned.
- **Actual Result**: `search` and `q` were ignored; all events returned regardless of query.
- **Fix Applied**: Added `q`, `search`, and `venue_id` query parameters as supported aliases to `search_events()` in `discovery.py` and `event_service.py`.
- **Verification**: Verified via `test_tc01_exact_title_search` through `test_tc09_multiword_and_cultural_search`.

---

### Defect BUG-03: Currency Inconsistency (USD `$`) vs Indian Rupee (`INR` `â‚¹`)
- **Severity**: **HIGH** (Violates Technovate 2.0 team baseline)
- **Component**: `app/models/`, `app/schemas/`, `app/ai/tools.py`, `app/static/index.html`
- **Steps to Reproduce**:
  1. Inspect default schemas and AI agent tool responses.
  2. Prices were displayed as `$250.00` instead of `â‚¹2,500.00`.
- **Expected Result**: Standardized Indian Rupee representation throughout.
- **Fix Applied**: Updated data models, schemas, seed scripts, AI tools, and frontend templates to use `currency="INR"` and the `â‚¹` symbol with Indian numbering formatting (`en-IN`).
- **Verification**: Verified in SQLite database, API responses, and AI assistant chat responses.

---

### Defect BUG-04: Draft / Inactive Event Visibility in Search
- **Severity**: **LOW** (Operational / Data Privacy)
- **Component**: `backend/app/services/event_service.py`
- **Steps to Reproduce**:
  1. Create an event with `status="INACTIVE"`.
  2. Query `GET /api/v1/events`.
- **Expected Result**: Inactive events should be hidden from public attendees.
- **Fix Applied**: Enforced `where(Event.status == "ACTIVE")` in `search_events()` query builder.
- **Verification**: Verified via `test_tc07_inactive_event_excluded_from_public_search`.

---

## 3. QA Recommendations for Teammates
1. **For Member 1 (Product Owner) (Frontend)**:
   - Use `GET /api/v1/events?search={query}&category={category}&venue_id={venueId}` for catalogue filtering.
   - All monetary amounts from the API are numbers; prefix them with `â‚¹` using `price.toLocaleString('en-IN')`.
2. **For Deepak (Backend) (Backend)**:
   - Ensure new migrations preserve `Venue.city` and `Venue.amenities` columns added for student accessibility.
   - Run `pytest tests/test_catalogue_search.py -v` whenever making changes to discovery endpoints.
3. **For Deepak & Adithya (AI & Frontend) (AI/Localization)**:
   - Sample queries in English, Kannada, and Hindi can safely test against the 10 student/cultural events seeded in `data/sample_catalogue.json`.


