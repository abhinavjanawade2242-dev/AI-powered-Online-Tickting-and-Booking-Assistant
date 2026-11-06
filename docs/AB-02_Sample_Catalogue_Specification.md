# AB-02: Sample Catalogue Dataset Specification

**Technovate 2.0 | Problem Statement PS-07: AI-Powered Online Ticketing and Booking Assistant**  
**Author:** Deepak & Manohar (Data & QA) (Member 3 â€“ Catalogue/Data + QA Support)  
**Task ID:** AB-02 Create Sample Catalogue  
**Version:** 1.0  

---

## 1. Domain & Scope
In accordance with Technovate 2.0 PS-07 decisions:
- **Domain**: Multi-venue platform prioritizing college, technical, cultural events, and featuring a second civic venue category (heritage cultural centre).
- **Target Audience**: Students, college societies, academic attendees, and cultural audiences.
- **Currency**: All pricing is strictly in Indian Rupees (`INR`, `â‚¹`).
- **Inventory Model**: Fixed ticket quantities per tier with zero assigned seating.

---

## 2. Seed Dataset Files
The complete dataset has been created, validated, and normalized in the `data/` directory:
- [`data/sample_catalogue.json`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/data/sample_catalogue.json): Hierarchical JSON dataset with venues, events, and embedded ticket tiers.
- [`data/sample_catalogue.csv`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/data/sample_catalogue.csv): Flattened CSV sheet for spreadsheet review and data analysts.
- [`data/venues.json`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/data/venues.json): Normalized venues entity file (5 venues).
- [`data/events.json`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/data/events.json): Normalized events entity file (10 events).
- [`data/ticket_tiers.json`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/data/ticket_tiers.json): Normalized ticket tiers entity file (21 tiers).

---

## 3. Venue Inventory

| Venue ID | Name | Category | City | Capacity | Highlights / Amenities |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `venue-campus-audi` | APJ Abdul Kalam Central Auditorium | Campus Auditorium | Bengaluru | 1,200 | Dual 4K Laser Projection, Central AC, Wheelchair Accessible |
| `venue-tech-hub` | Turing Innovation & Incubation Center | Technology Lab | Bengaluru | 350 | 1Gbps Dedicated LAN, Ergonomic Desking, 3D Printers |
| `venue-open-amphi` | Kuvempu Open Air Amphitheatre | Open Air Amphitheatre | Bengaluru | 2,000 | 10kW Line Array Sound, Stepped Tier Seating, Food Court |
| `venue-sports-arena` | Netaji Subhas Indoor Sports Complex | Sports & Esports Arena| Bengaluru | 800 | Maple Hardwood Court, Fiber LAN for Esports, Dugouts |
| `venue-city-centre` | Sir M. Visvesvaraya Memorial Cultural Center | Civic Cultural Center | Bengaluru | 600 | Heritage Civic Hall, Classic Theatre Stage, Parking |

---

## 4. Event Inventory & Tier Pricing Summary

| Event ID | Event Title | Category | Venue | Tier Breakdown & Prices |
| :--- | :--- | :--- | :--- | :--- |
| `event-technovate-hack` | Technovate 2026: 36-Hour National Hackathon | Technical | Turing Center | Early Bird (â‚¹299), Standard Team (â‚¹599), VIP Pack (â‚¹1,199) |
| `event-dhwani-fest` | Dhwani '26: Cultural Fest & Battle of Bands | Cultural | Open Amphitheatre | General Admission (â‚¹150), VIP Moshpit (â‚¹450) |
| `event-ai-robotics-summit` | National Student AI & Robotics Summit 2026 | Technical | Central Auditorium | Student Pass (â‚¹350), Workshop Full Access (â‚¹850) |
| `event-esports-championship`| Campus Valorant & BGMI Esports Finals | Sports | Sports Complex | Spectator (â‚¹100), Competitor Team (â‚¹250), VIP Dugout (â‚¹500) |
| `event-kannada-theatre` | 'Tughlaq' Classic Kannada Drama | Cultural | City Cultural Center | Balcony (â‚¹120), Main Orchestra (â‚¹250), Patron (â‚¹500) |
| `event-startup-pitch-fest` | VentureNest Student Startup Pitch Day | Technical | Turing Center | Student Observer (â‚¹200), Founder Pitch (â‚¹500) |
| `event-classical-fusion` | Raag & Rhythm: Indo-Western Fusion Night | Cultural | Central Auditorium | Student Pass (â‚¹180), VIP Stage View (â‚¹400) |
| `event-cybersec-bootcamp` | Hands-on Ethical Hacking & Cyber Bootcamp | Workshop | Turing Center | Bootcamp Certification Pass (â‚¹499) |
| `event-tedx-campus` | TEDx Youth: Innovating for Tomorrow's Bharat | Conference | Central Auditorium | Standard Delegate (â‚¹400), VIP Speakers Lunch (â‚¹950) |
| `event-draft-robot-wars` | RoboClash: Inter-University Combat Robotics | Technical | Sports Complex | *Draft / Inactive event for QA testing* (â‚¹150) |

---

## 5. Seed Integration Script
A dedicated seeding script is provided at [`backend/scripts/seed_member3_catalogue.py`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/backend/scripts/seed_member3_catalogue.py).  
It can be executed at any time using:
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe scripts/seed_member3_catalogue.py
```
This guarantees that any teammate pulling the repository can initialize a full, realistic, student-oriented multi-venue database with a single command.


