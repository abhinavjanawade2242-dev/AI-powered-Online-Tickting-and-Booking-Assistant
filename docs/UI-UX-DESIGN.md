
# PS-07 – AI-Powered Online Ticketing and Booking Assistant

## UI/UX Design Specification

### 1. Project Overview

The application provides an accessible and responsive platform for discovering events, selecting General Admission tickets, and completing bookings with AI-powered assistance.

Users can browse events, view event details, choose ticket quantities, review booking information, and proceed through a sandbox payment flow.

The interface is designed for students and college communities, with multilingual support for English, Kannada, and Hindi.

### 2. Design Goals

- Provide a simple and user-friendly interface.
- Make event discovery and ticket booking easy.
- Support users with different levels of digital literacy.
- Provide responsive layouts for mobile, tablet, and desktop.
- Clearly communicate ticket availability and booking status.
- Support multilingual interaction.
- Provide accessible navigation, readable text, and clear feedback.
- Avoid showing a confirmed booking until the backend verifies it.

### 3. User Journey

The main General Admission booking journey is:

1. Open the application.
2. Browse or search for events.
3. Select an event.
4. View event information, date, time, venue, and ticket price.
5. Select the required ticket quantity.
6. Review the booking summary.
7. Enter customer details.
8. Proceed to sandbox payment, if payment is required.
9. Display the confirmed booking and digital QR ticket only after backend confirmation.

For free events, the payment step may be skipped according to the backend booking flow.

### 4. Main UI Screens

#### Screen 1 – Event Browsing

Purpose: Help users discover available events.

Elements:
- Application logo and navigation.
- Language selection.
- Event search bar.
- Event category filters.
- Event cards with image, event name, date, venue, and price.
- Event details or booking action.
- AI assistant entry point.

Layout:
- Desktop: Multi-column event card grid.
- Tablet: Two-column event card grid.
- Mobile: Single-column event card layout.

#### Screen 2 – Event Details and Ticket Selection

Purpose: Display event information and allow users to choose General Admission ticket quantities.

Elements:
- Event image and name.
- Event description.
- Date and showtime.
- Venue and location.
- General Admission ticket type.
- Ticket price.
- Quantity increase and decrease controls.
- Total ticket price.
- Continue button.

Rules:
- Users select ticket quantities, not individual seats.
- No assigned-seat map or seating arrangement is displayed.
- Quantity limits and availability should follow backend information.
- The interface must prevent invalid quantities.

#### Screen 3 – Booking Summary and Checkout

Purpose: Allow users to review their booking before payment.

Elements:
- Selected event information.
- General Admission ticket type.
- Selected quantity.
- Ticket subtotal.
- Applicable fees and taxes, if provided by the backend.
- Final payable amount.
- Customer name.
- Customer email.
- Customer phone, if required.
- Back and Continue to Payment buttons.

Rules:
- Display the complete price breakdown.
- Validate required customer information.
- Do not assume a booking is confirmed when the user reaches checkout.

#### Screen 4 – Payment

Purpose: Complete the sandbox payment process.

Elements:
- Booking reference.
- Amount payable.
- Sandbox payment action.
- Payment processing indicator.
- Payment success, failure, and pending messages.

Rules:
- Use sandbox payment only.
- Display payment status returned by the backend.
- A failed or pending payment must not display a confirmed ticket.
- Prevent repeated payment actions while a request is processing.

#### Screen 5 – Booking Confirmation

Purpose: Display the result of a successfully confirmed booking.

Elements:
- Booking reference.
- Booking status.
- Event name and date.
- Venue.
- General Admission ticket type.
- Ticket quantity.
- Digital QR ticket.
- Download or print ticket option.
- Return to event browsing action.

Rules:
- Display the digital QR ticket only after backend confirmation.
- Do not generate a valid entry ticket for pending or failed bookings.
- Clearly communicate unsuccessful or pending booking status.

#### Screen 6 – AI Chat Assistant

Purpose: Help users discover events and understand the booking process.

Elements:
- User and assistant messages.
- Text input.
- Send button.
- Suggested questions.
- Language selection.
- Clear response and error messages.

Future enhancements:
- Voice input.
- Context-aware event recommendations.
- Offline request synchronization information.

The assistant must not claim that a booking is confirmed without backend verification.

### 5. Ticket Availability and Booking States

Since the project follows General Admission booking, availability states apply to ticket inventory rather than individual seats.

| State | Visual indicator | Behaviour |
|---|---|---|
| Available | Green + check icon | Tickets can be requested |
| Locked / Held | Amber + lock icon | Inventory is temporarily held during the reservation period |
| Sold Out | Red + unavailable icon | No tickets can be reserved |
| Sync Pending | Blue + spinner icon | Offline request is waiting for synchronization |
| Confirmed | Green + confirmation icon | Backend has confirmed the booking |

Important rules:
- State must be communicated through text and icons, not color alone.
- A queued offline request is not a confirmed reservation.
- The backend is the authority for inventory and booking status.
- The frontend must update the displayed state using backend responses.

### 6. Design System and Visual Guidelines

#### Color Palette

The current frontend uses a dark purple visual theme.

| Token | Color | Purpose |
|---|---|---|
| Background | #080B18 | Main application background |
| Foreground | #F8FAFC | Primary text |
| Surface | #15152D | Cards and panels |
| Secondary Surface | #1C2038 | Secondary sections |
| Primary | #7C3AED | Main buttons and actions |
| Accent | #A78BFA | Highlights and interactive elements |
| Muted | #A1A1AA | Secondary text |
| Border | #30304D | Dividers and outlines |

Status colors should be selected and checked for sufficient contrast before final approval.

#### Typography

- Use a consistent sans-serif font throughout the application.
- Use clear heading hierarchy.
- Use readable body text.
- Use medium or bold font weights for important actions and headings.
- Avoid excessively small text.

#### Spacing

- Use consistent spacing between sections and components.
- Keep sufficient padding inside cards and forms.
- Maintain consistent button heights and input spacing.
- Use responsive spacing for smaller screens.

#### Components

Reusable UI components include:
- Navigation bar.
- Event cards.
- Search and category filters.
- Ticket quantity selector.
- Booking summary.
- Form inputs.
- Payment status messages.
- Booking confirmation.
- AI chat interface.

### 7. Accessibility

- Support keyboard navigation.
- Provide visible focus indicators.
- Maintain readable font sizes.
- Target WCAG 2.2 AA contrast requirements.
- Use accessible labels for form fields.
- Display validation errors near the relevant field.
- Provide clear success and failure messages.
- Use sufficiently large touch targets.
- Provide meaningful alternative text for images.
- Ensure icons have accessible names when they communicate important information.
- Do not use color alone to communicate status.
- Respect reduced-motion preferences.

### 8. Responsive Design

#### Desktop
- Multi-column event browsing layout.
- Spacious event cards.
- Clearly separated booking summary and checkout sections.
- Easily accessible navigation.

#### Tablet
- Flexible event grid.
- Adjusted card widths and spacing.
- Responsive checkout layout.

#### Mobile
- Single-column event cards.
- Compact navigation.
- Full-width form controls and buttons where appropriate.
- Easy-to-use ticket quantity controls.
- Readable booking summary.
- Chat assistant adapted to smaller screens.

### 9. Error, Loading, and Feedback States

| Situation | Expected UI behaviour |
|---|---|
| Loading events | Display loading indicator or skeleton cards |
| No events found | Display a helpful empty-state message |
| Invalid quantity | Display a validation message |
| Network failure | Display connection information and retry action |
| Reservation conflict | Inform the user that tickets are no longer available |
| Reservation pending | Clearly show pending status |
| Payment failure | Display failure message and available next action |
| Payment pending | Do not display a confirmed ticket |
| Offline request queued | Explain that the request is waiting for synchronization |
| Booking confirmed | Display booking reference and valid digital ticket |

### 10. Review and Approval

The proposed design should be reviewed by:

- Member 1 – PRD and requirements.
- Member 3 – Backend and API contracts.
- Member 4 – Payment integration.

Review checklist:
- [ ] Main user flows are represented.
- [ ] General Admission booking is reflected in all screens.
- [ ] Ticket availability states are distinguishable.
- [ ] Responsive layouts are considered.
- [ ] Accessibility requirements are documented.
- [ ] Error and loading states are documented.
- [ ] Design tokens are consistent with the frontend.
- [ ] Team review and feedback are completed.

### 11. Design Status

The initial UI implementation is available in the frontend.

This specification has been updated to follow the General Admission booking approach.

Final design approval and team review are pending.
