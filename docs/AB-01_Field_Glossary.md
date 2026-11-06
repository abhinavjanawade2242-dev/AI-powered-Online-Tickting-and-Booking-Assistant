# AB-01: Catalogue Field Glossary & Data Dictionary

**Technovate 2.0 | Problem Statement PS-07: AI-Powered Online Ticketing and Booking Assistant**  
**Author:** Deepak & Manohar (Data & QA) (Member 3 â€“ Catalogue/Data + QA Support)  
**Task ID:** AB-01 Understand Data Fields  
**Version:** 1.0 | Baseline Specification  

---

## 1. Overview
This document establishes the official data dictionary and field glossary for all catalogue-related entities in the PS-07 application. It covers constraints, data types, validation rules, relationships, and representative examples for **Venues**, **Events**, and **Ticket Tiers**, ensuring clean cross-functional contract alignment between Backend (Deepak (Backend)), Frontend (Member 1 (Product Owner)), and AI Assistant (Deepak & Adithya (AI & Frontend)).

---

## 2. Venue Entity (`venues`)

Venues represent physical campus auditoriums, open-air amphitheatres, technical innovation labs, and civic cultural centres.

| Field Name | Type | Required | Constraints / Validation | Description | Realistic Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `String(36)` | Yes | Primary Key, Unique, Slug or UUID format | Immutable unique identifier for the venue | `"venue-campus-audi"` |
| `name` | `String(255)` | Yes | 3â€“255 chars, trimmed | Official human-readable name of the facility | `"APJ Abdul Kalam Central Auditorium"` |
| `category` | `String(100)` | Yes | Non-empty string | Classification of venue type | `"Campus Auditorium"`, `"Open Air Amphitheatre"` |
| `city` | `String(100)` | Yes | Non-empty string, indexed | City or municipal locality | `"Bengaluru"` |
| `address` | `String(255)` | Yes | Min 5 chars | Physical location / campus landmark | `"Campus Main Block, Ground Floor, RV Vidyaniketan, Bengaluru 560059"` |
| `capacity` | `Integer` | Yes | Must be integer > 0 | Maximum physical hall/grounds capacity | `1200` |
| `amenities` | `Text` | No | Comma-separated or text | Key facility highlights for accessibility | `"Dual 4K Laser Projection, Central AC, Wheelchair Accessible"` |
| `description`| `Text` | No | Optional summary | Paragraph highlighting venue characteristics | `"Acoustically treated auditorium for conferences and summits."` |
| `active` | `Boolean` | Yes | Default `true` | Operational status of facility | `true` |

---

## 3. Event Entity (`events`)

Events represent scheduled hackathons, cultural fests, theatre dramas, esports tournaments, workshops, and symposiums.

| Field Name | Type | Required | Constraints / Validation | Description | Realistic Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `String(36)` | Yes | Primary Key, Unique, Slug or UUID | Immutable unique identifier for the event | `"event-technovate-hack"` |
| `venue_id` | `String(36)` | Yes | Foreign Key -> `venues.id` | Reference to venue hosting the event | `"venue-tech-hub"` |
| `title` | `String(255)` | Yes | Min 5 chars, trimmed, indexed | Headline event title | `"Technovate 2026: 36-Hour National Hackathon"` |
| `description`| `Text` | Yes | Min 15 chars | Detailed synopsis of activities, prizes, guests | `"Build innovative solutions in AI, Climate Tech, and FinTech..."` |
| `category` | `String(100)` | Yes | Allowed: `Technical`, `Cultural`, `Sports`, `Workshop`, `Conference`, `Comedy`, `Concert` | Categorical taxonomy used for search and filters | `"Technical"` |
| `start_time` | `DateTime` | Yes | Valid ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`), must be `< end_time` | Event commencement timestamp | `"2026-11-20T09:00:00+05:30"` |
| `end_time` | `DateTime` | Yes | Valid ISO 8601, must be `> start_time` | Event conclusion timestamp | `"2026-11-21T21:00:00+05:30"` |
| `status` | `String(50)` | Yes | Allowed: `ACTIVE`, `INACTIVE`, `CANCELLED`, `COMPLETED` | Lifecycle state. Only `ACTIVE` events are publicly bookable | `"ACTIVE"` |
| `image_url` | `String(500)`| No | Valid HTTPS URL or placeholder | High-resolution visual banner | `"https://images.unsplash.com/photo-1504384308090-c894fdcc538d"` |

---

## 4. Ticket Tier Entity (`ticket_tiers`)

Ticket tiers define inventory quotas and pricing per event category (e.g., Student, Early Bird, VIP).

| Field Name | Type | Required | Constraints / Validation | Description | Realistic Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `String(36)` | Yes | Primary Key, Unique | Unique identifier for tier slot | `"tier-tech-early"` |
| `event_id` | `String(36)` | Yes | Foreign Key -> `events.id` | Target event reference | `"event-technovate-hack"` |
| `name` | `String(100)` | Yes | Min 2 chars | Tier designation | `"Early Bird Hacker Pass"` |
| `price` | `Numeric(10,2)`| Yes| Decimal >= 0.00 | Admission price | `299.00` |
| `currency` | `String(10)` | Yes | Mandatory: `"INR"` (`â‚¹`) | Standard billing currency | `"INR"` |
| `total_quantity`| `Integer`| Yes | Positive Integer > 0 | Total allocated seats / inventory | `80` |
| `available_quantity`| `Integer`| Yes | Integer: `0 <= available <= total` | Remaining unsold inventory | `80` |
| `version` | `Integer` | Yes | Integer >= 1 | Optimistic concurrency control lock counter | `1` |

---

## 5. Prohibited Practices & Integrity Rules
1. **No Negative Quantities**: `available_quantity` must never drop below 0.
2. **Strict Currency Rule**: Per finalized team decisions, currency is exclusively `INR` (`â‚¹`); no foreign currencies (`USD`, `EUR`) are accepted.
3. **No Phantom Venues**: Events cannot reference unseeded or non-existent `venue_id`s.
4. **Temporal Ordering**: An event's `end_time` must strictly occur after `start_time`.
5. **Private vs Public Visibility**: Inactive events (`status != 'ACTIVE'`) must never be returned in public discovery listings.


