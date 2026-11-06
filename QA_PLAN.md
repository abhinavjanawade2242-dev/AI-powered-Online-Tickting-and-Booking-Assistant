# QUALITY ASSURANCE PLAN & CI/CD WORKFLOW PLAN

**Project:** AI-Powered Online Ticketing and Booking Assistant
**Owner:** Member 4 â€“ QA, Security and Integration Lead
**Reviewer:** Member 1
**Version:** 1.0
**Status:** Draft â€“ Pending Approval

---

## 1. OBJECTIVE

The objective of this document is to establish software quality standards, accessibility requirements, automated testing strategies and CI/CD workflows for the project.

The plan ensures that the application is reliable, secure, accessible, maintainable and ready for deployment.

## 2. ISO/IEC 25010 QUALITY CHECKLIST

The project will follow the ISO/IEC 25010:2023 product quality model.

| Quality characteristic | Verification requirements |
|---|---|
| Functional suitability | All booking, ticketing and payment features work correctly. |
| Performance efficiency | APIs respond within agreed performance limits. |
| Compatibility | Frontend, backend and external services communicate correctly. |
| Interaction capability | Interfaces are understandable and accessible. |
| Reliability | Application handles errors and recovers from failures. |
| Security | Authentication, authorization and sensitive data are protected. |
| Maintainability | Code is modular, documented and testable. |
| Flexibility | Application can adapt to different environments and configurations. |
| Safety | System prevents harmful outcomes such as accidental duplicate bookings or incorrect transactions. |

**Quality verification:** Each characteristic must have documented test evidence or an approved inspection before release.

## 3. WCAG 2.1 AA ACCESSIBILITY CHECKLIST

The application will follow the four WCAG principles (POUR).

### Perceivable
- Images must have meaningful alternative text.
- Normal text contrast must be at least 4.5:1.
- Large text contrast must be at least 3:1.
- Information must not depend on colour alone.

### Operable
- All interactive controls must support keyboard navigation.
- Keyboard focus must be visible.
- No keyboard traps.
- Interactive elements must have sufficient accessible labels.

### Understandable
- Forms must have clear labels.
- Error messages must explain how to correct mistakes.
- Navigation must remain consistent.
- Instructions must be understandable.

### Robust
- Use semantic HTML.
- Provide accessible names and roles.
- Support assistive technologies and screen readers.

**Testing tools:** Lighthouse, axe DevTools and manual keyboard testing.

## 4. GITHUB ACTIONS CI WORKFLOW PLAN

**Objective:** Automatically validate code changes before they are merged into the main branch.

### Workflow steps

1. Developer pushes code to GitHub.
2. GitHub Actions starts automatically.
3. Checkout the repository.
4. Set up the required Python version.
5. Install project dependencies.
6. Execute Python linting using Ruff.
7. Run automated tests using Pytest.
8. Run security checks using Bandit.
9. Audit dependencies using pip-audit.
10. Report success or failure.

### Trigger events

- Push to feature branches.
- Pull requests targeting main.
- Changes merged into main.

**Workflow file:**

`.github/workflows/ci.yml`

### Expected results

- Valid code passes all configured checks.
- Failed tests produce visible failure reports.
- Security findings are reported for review.
- Pull requests cannot be considered validated until required checks pass.

## 5. NETLIFY DEPLOYMENT PREVIEW PLAN

**Objective:** Provide temporary preview deployments for frontend changes before production release.

### Deployment process

1. Connect the GitHub repository to Netlify.
2. Configure the frontend build command.
3. Configure the publish directory.
4. Create a feature branch.
5. Open a pull request.
6. Netlify generates a deployment preview URL.
7. Team members inspect the preview.
8. Approve and merge changes.
9. Deploy the approved production version.

**Expected result:** Every eligible frontend pull request receives a preview that can be reviewed before production deployment.

**Note:** Netlify hosts the frontend deployment. The Python backend requires a separately configured hosting environment.

## 6. AUTOMATED TESTING STRATEGY

### 6.1 API Testing

**Tools:** Pytest, HTTPX and pytest-asyncio.

Test scenarios:
- Valid API requests.
- Invalid input validation.
- Authentication and authorization.
- Missing resources.
- Payment API responses.
- Error handling.

Expected results:
- Successful requests return appropriate success status codes.
- Invalid requests are rejected.
- Unauthorized requests cannot access protected resources.
- Error responses do not expose internal application details.

### 6.2 Concurrency and Load Testing

**Tools:** Locust and asyncio.

Test scenarios:
- 10 simultaneous users.
- 50 simultaneous users.
- 100 simultaneous users.
- Multiple users selecting the same available seat.
- Concurrent booking and payment requests.

Expected results:
- No duplicate confirmed bookings for the same seat and event.
- No corrupted database records.
- No unexpected server crashes.
- Consistent booking and payment states.
- Response times and failure rates are recorded.

Performance thresholds will be agreed upon with Member 1.

### 6.3 Security Testing

**Tools:** Pytest, Bandit and pip-audit.

Test scenarios:
- Incorrect login credentials.
- Invalid and expired authentication tokens.
- Unauthorized API access.
- SQL injection attempts.
- Sensitive information exposure.
- Payment verification tampering.
- Dependency vulnerability checks.

Expected results:
- Unauthorized access is rejected.
- Passwords are not stored in plaintext.
- Invalid payment verification is rejected.
- Sensitive information is not exposed.
- Security findings are documented and addressed.

### 6.4 End-to-End Testing

**Objective:** Validate complete user workflows.

Example workflow:

1. User opens the application.
2. User logs in.
3. User searches for an event.
4. User selects available seats.
5. User initiates payment.
6. Payment is verified.
7. Booking is saved.
8. User receives booking confirmation.

Expected result: The complete workflow succeeds and booking information remains consistent across the application.

## 7. FIVE WORKED TEST CASES

The following are provisional scenarios for the ticketing application. They must be confirmed against the team's actual five worked cases.

### TC-01: User Authentication

**Input:** Valid username and password.

**Expected result:** User successfully logs in and receives valid authentication credentials.

**Failure condition:** Invalid credentials must not grant access.

### TC-02: Event Search and Availability

**Input:** User searches for an available event.

**Expected result:** Relevant events and their available seats are displayed correctly.

**Failure condition:** Invalid searches must be handled without application crashes.

### TC-03: Concurrent Seat Booking

**Input:** Two users attempt to book the same seat simultaneously.

**Expected result:** Only one booking is confirmed. The other user receives an appropriate unavailable-seat response.

**Failure condition:** Duplicate confirmed bookings must never occur.

### TC-04: Payment Processing

**Input:** A user initiates a payment through the payment sandbox.

**Expected result:** Successful payment is verified and booking status is updated.

**Failure condition:** Failed or unverified payments must not generate confirmed bookings.

### TC-05: Offline Synchronization

**Input:** User performs supported operations while offline and reconnects.

**Expected result:** Valid pending changes synchronize without duplicate records or data corruption.

**Failure condition:** Failed synchronization must be reported and safely retried.

### Test result recording

Every test case will contain:

- Test case ID.
- Preconditions.
- Test input.
- Execution steps.
- Expected result.
- Actual result.
- Pass/fail status.
- Evidence or screenshot.

## 8. CI/CD ACCEPTANCE CRITERIA

The workflow will be considered ready when:

- Automated checks execute on configured GitHub events.
- Tests produce clear pass/fail results.
- Security checks are included.
- Deployment previews are available for frontend pull requests.
- Production deployment follows team approval.
- Testing evidence is documented.

## 9. COMPLETION CHECKLIST

- [ ] ISO/IEC 25010 quality checklist documented.
- [ ] WCAG 2.1 AA accessibility checklist documented.
- [ ] GitHub Actions CI workflow plan prepared.
- [ ] Netlify deployment preview plan prepared.
- [ ] API testing strategy defined.
- [ ] Concurrency testing strategy defined.
- [ ] Security testing strategy defined.
- [ ] End-to-end testing strategy defined.
- [ ] Five worked cases documented and confirmed.
- [ ] Member 1 approval obtained.

## 10. REVIEW AND APPROVAL

**Prepared by:** Member 4 â€“ QA, Security and Integration Lead

**Reviewed by:** Member 1

**Approval status:** Pending

**Reviewer comments:** To be updated after review.

**Approval date:** To be confirmed.
