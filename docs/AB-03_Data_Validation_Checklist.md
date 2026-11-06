# AB-03: Data Validation Checklist & Audit Log

**Technovate 2.0 | Problem Statement PS-07: AI-Powered Online Ticketing and Booking Assistant**  
**Author:** Deepak & Manohar (Data & QA) (Member 3 â€“ Catalogue/Data + QA Support)  
**Task ID:** AB-03 Validate Catalogue  
**Version:** 1.0  

---

## 1. Validation Criteria & Quality Gates

Every dataset added to the repository must satisfy the following automated validation rules before being integrated into development or production databases:

| Check ID | Verification Rule | Target Threshold | Validation Logic | Status |
| :--- | :--- | :--- | :--- | :--- |
| **VAL-01** | **Primary Key Uniqueness** | 0 duplicates | Venues, Events, and Tiers must each contain unique non-null IDs. | âœ… PASS |
| **VAL-02** | **Foreign Key Integrity** | 100% resolution | Every `event.venue_id` must resolve to a valid registered `venues.id`. | âœ… PASS |
| **VAL-03** | **Temporal Consistency** | 100% valid | `start_time` must be an ISO 8601 string and strictly earlier than `end_time`. | âœ… PASS |
| **VAL-04** | **Currency Compliance** | 100% INR | All ticket tier `currency` fields must be `"INR"`. Zero foreign currencies allowed. | âœ… PASS |
| **VAL-05** | **Price Non-Negativity** | Price >= 0.00 | No negative pricing allowed. Free student events must be `0.00`. | âœ… PASS |
| **VAL-06** | **Inventory Bounds** | `0 <= available <= total` | Total quantity must be > 0. Available quantity cannot exceed total quantity. | âœ… PASS |
| **VAL-07** | **Physical Venue Capacity** | Total Tier Quota <= Venue Cap | Sum of all event ticket tier quantities must not exceed physical venue capacity. | âœ… PASS |
| **VAL-08** | **Content Completeness** | Title >= 5 chars, Desc >= 15 | Titles and descriptions must have sufficient detail for AI indexing and search. | âœ… PASS |
| **VAL-09** | **Active Status Validity** | Allowed status set | Event status must be in `{'ACTIVE', 'INACTIVE', 'CANCELLED', 'COMPLETED'}`. | âœ… PASS |

---

## 2. Automated Audit Execution Log

**Executed Script:** [`backend/scripts/validate_catalogue.py`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/backend/scripts/validate_catalogue.py)  
**Target File:** `data/sample_catalogue.json`  
**Execution Timestamp:** 2026-11-06T12:16:40+05:30  
**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/validate_catalogue.py ../data/sample_catalogue.json
```

```text
======================================================================
PS-07 CATALOGUE DATA INTEGRITY & VALIDATION AUDIT
Target Dataset: ../data/sample_catalogue.json
======================================================================
Loaded 5 venues and 10 events.
----------------------------------------------------------------------
âœ“ Checked 5 venues: 5 unique venue IDs.
âœ“ Checked 10 events and 21 ticket tiers.
----------------------------------------------------------------------
âœ… VALIDATION SUCCESSFUL: All constraints, schema checks, and business rules PASSED!
   â€¢ Venues: 5 verified
   â€¢ Events: 10 verified
   â€¢ Ticket Tiers: 21 verified
   â€¢ Currency: All tiers confirmed in INR (â‚¹)
   â€¢ Referential Integrity: 100% valid venue associations
   â€¢ Inventory Boundaries: 0 <= available_quantity <= total_quantity for all tiers
======================================================================
```

---

## 3. Discovered & Resolved Data Anomalies
During initial data authoring, the following edge cases were identified and resolved:
1. **Venue Capacity vs Tier Sum**: In early drafts of `event-dhwani-fest`, total tiers initially summed to 2,500 seats at `venue-open-amphi` (which holds 2,000). Reduced total seats to 950 (800 General Admission + 150 VIP) to respect physical safety and capacity boundaries.
2. **Timezone Representation**: Standardized all dates to explicit UTC/IST offsets (`+05:30`) to avoid parsing discrepancies across clients.
3. **Currency Alignment**: Replaced legacy default `"USD"` values with explicit `"INR"` to match team hackathon commitments.


