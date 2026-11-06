# AB-04: Catalogue Search & Filter Test Cases

**Technovate 2.0 | Problem Statement PS-07: AI-Powered Online Ticketing and Booking Assistant**  
**Author:** Deepak & Manohar (Data & QA) (Member 3 â€“ Catalogue/Data + QA Support)  
**Task ID:** AB-04 Search Test Cases  
**Version:** 1.0 | 10 Reproducible Test Scenarios  

---

## 1. Overview
This test specification outlines 10 reproducible test cases validating event discovery, text search, category filtering, venue filtering, case insensitivity, empty results, and inactive event exclusion.

All test cases are codified and automatically verifiable via `pytest` at [`backend/tests/test_catalogue_search.py`](file:///d:/deepak/AI-powered-Online-Tickting-and-Booking-Assistant/backend/tests/test_catalogue_search.py).

---

## 2. Test Case Matrix

| TC ID | Test Scenario | Input Query / Parameters | Expected Behavior | Automated Test Reference | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | **Exact Title Search** | `GET /api/v1/events?search=Technovate 2026` | Returns `event-technovate-hack` as top result; HTTP 200. | `test_tc01_exact_title_search` | âœ… PASS |
| **TC-02** | **Partial Keyword Search** | `GET /api/v1/events?search=hackathon` | Returns events containing "hackathon" in title or description. | `test_tc02_partial_keyword_search` | âœ… PASS |
| **TC-03** | **Category Filter (Technical)** | `GET /api/v1/events?category=Technical` | Returns all technical events (Hackathon, Robotics, Startups). All returned items have `category == "Technical"`. | `test_tc03_category_filtering_technical` | âœ… PASS |
| **TC-04** | **Category Filter (Cultural)** | `GET /api/v1/events?category=Cultural` | Returns cultural events (Dhwani Fest, Kannada Drama, Classical Fusion). | `test_tc04_category_filtering_cultural` | âœ… PASS |
| **TC-05** | **Venue ID Filtering** | `GET /api/v1/events?venue_id=venue-tech-hub` | Returns only events hosted at the Turing Innovation Center. | `test_tc05_venue_filtering` | âœ… PASS |
| **TC-06** | **Zero Matches / Empty Search** | `GET /api/v1/events?search=NonExistentQuantumTeleportation2099` | Returns an empty JSON array `[]` with HTTP 200; no 500 error or crash. | `test_tc06_empty_result_nonexistent_query` | âœ… PASS |
| **TC-07** | **Inactive Event Exclusion** | `GET /api/v1/events` | Draft or inactive events (`event-draft-robot-wars`) must NOT appear in public discovery. | `test_tc07_inactive_event_excluded_from_public_search` | âœ… PASS |
| **TC-08** | **Case Insensitivity** | `GET /api/v1/events?search=TECHNOVATE` vs `?search=technovate` | Both uppercase and lowercase queries return identical event ID sets. | `test_tc08_case_insensitive_search` | âœ… PASS |
| **TC-09** | **Multi-Word & Cultural Query** | `GET /api/v1/events?search=Kannada Drama` | Matches theatrical production 'Tughlaq' based on cultural keywords. | `test_tc09_multiword_and_cultural_search` | âœ… PASS |
| **TC-10** | **Inventory & Currency Audit** | `GET /api/v1/events/{id}/availability` | All returned tiers have positive quantity and `currency == "INR"`. | `test_tc10_availability_and_inr_currency` | âœ… PASS |

---

## 3. How to Run the Automated Search Test Suite
Teammates can reproduce all 10 test cases locally at any time:
```powershell
.\.venv\Scripts\pytest.exe tests/test_catalogue_search.py -v
```
**Test Result Output:**
```text
tests/test_catalogue_search.py::test_tc01_exact_title_search PASSED      [ 10%]
tests/test_catalogue_search.py::test_tc02_partial_keyword_search PASSED  [ 20%]
tests/test_catalogue_search.py::test_tc03_category_filtering_technical PASSED [ 30%]
tests/test_catalogue_search.py::test_tc04_category_filtering_cultural PASSED [ 40%]
tests/test_catalogue_search.py::test_tc05_venue_filtering PASSED         [ 50%]
tests/test_catalogue_search.py::test_tc06_empty_result_nonexistent_query PASSED [ 60%]
tests/test_catalogue_search.py::test_tc07_inactive_event_excluded_from_public_search PASSED [ 70%]
tests/test_catalogue_search.py::test_tc08_case_insensitive_search PASSED [ 80%]
tests/test_catalogue_search.py::test_tc09_multiword_and_cultural_search PASSED [ 90%]
tests/test_catalogue_search.py::test_tc10_availability_and_inr_currency PASSED [100%]

============================= 10 passed in 0.19s ==============================
```


