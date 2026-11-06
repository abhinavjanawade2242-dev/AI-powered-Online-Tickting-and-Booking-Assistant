
# PS-07 – AI-Powered Online Ticketing and Booking Assistant

## UI/UX Design Specification

### 1. Project Overview
The application provides an accessible platform for discovering events, selecting tickets, choosing seats and completing bookings with AI-powered assistance.

### 2. Design Goals
- Simple and user-friendly interface.
- Easy event discovery and ticket selection.
- Accessible for users with low digital literacy.
- Support for mobile, tablet and desktop.
- Clear booking and payment status.
- Support for multilingual interaction.

### 3. User Journey
1. Open the application.
2. Browse or search for events.
3. Select an event and date.
4. View available tickets.
5. Select seats.
6. Review the price summary.
7. Proceed to payment.
8. Receive booking confirmation after backend verification.

### 4. Main UI Screens

#### Screen 1 – Event Listing
- Application logo and navigation.
- Event search bar.
- Event categories.
- Event cards with image, date, location and price.
- View Details and Book Now buttons.

#### Screen 2 – Seat Selection
- Selected event information.
- Date and showtime.
- Seating arrangement.
- Seat-state legend.
- Selected seat summary.
- Continue button.

#### Screen 3 – Checkout
- Event and seat information.
- Ticket subtotal.
- Convenience fee.
- Applicable taxes.
- Discounts, if applicable.
- Final payable amount.
- Payment button.

#### Screen 4 – Chat Assistant
- User and assistant messages.
- Text and voice input.
- Language selection.
- Online/offline status.
- Retry and synchronization messages.

#### Screen 5 – Booking Confirmation
- Booking reference.
- Booking status.
- Event and seat details.
- Digital QR ticket after backend confirmation.

### 5. Seat States

| State | Visual indicator | Behaviour |
|---|---|---|
| Available | Green + check | Selectable |
| Locked | Amber + lock | Temporarily unavailable |
| Booked | Red + cross | Not selectable |
| Syncing | Blue + spinner | Waiting for synchronization |

Seat states must be communicated using icons and labels, not color alone.

### 6. Accessibility
- Support keyboard navigation.
- Provide visible focus indicators.
- Use readable font sizes.
- Maintain WCAG AA contrast targets.
- Provide accessible form labels.
- Display clear validation and error messages.
- Use sufficiently large touch targets.
- Support screen readers.

### 7. Responsive Design
- Desktop: Multi-column event listing and detailed seat layout.
- Tablet: Flexible grid and adjusted seat layout.
- Mobile: Single-column event cards and compact checkout.

### 8. Error and Loading States
- Loading: Show a loading indicator.
- Validation: Display errors near the relevant field.
- Network failure: Display connection status and retry option.
- Seat conflict: Inform the user that the seat is no longer available.
- Booking pending: Never display confirmed until the backend confirms it.

### 9. Review and Approval
The proposed design must be reviewed by:
- Member 1 – PRD and requirements.
- Member 3 – Backend and API contracts.
- Member 4 – Payment integration.

### 10. Design Status
Initial design specification prepared. Awaiting team review and approval.
