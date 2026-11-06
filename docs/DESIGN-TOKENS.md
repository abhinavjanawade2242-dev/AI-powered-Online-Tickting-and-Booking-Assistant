
# PS-07 – Design Tokens

## 1. Overview

This document defines the reusable visual design tokens for the AI-Powered Online Ticketing and Booking Assistant.

The frontend uses a dark navy and purple theme to provide a consistent appearance across event browsing, ticket selection, checkout, payment, and booking confirmation.

## 2. Color Palette

| Token | CSS Variable | Value | Purpose |
|---|---|---|---|
| Background | --background | #080B18 | Main application background |
| Foreground | --foreground | #F8FAFC | Primary text |
| Surface | --surface | #15152D | Cards and panels |
| Secondary Surface | --surface-secondary | #1C2038 | Secondary sections |
| Primary | --primary | #7C3AED | Primary buttons and actions |
| Accent | --accent | #A78BFA | Highlights and interactive elements |
| Muted | --muted | #A1A1AA | Secondary text |
| Border | --border | #30304D | Borders and separators |

## 3. Status Colors

These colors represent General Admission ticket availability and booking states.

| State | Suggested Color | Purpose |
|---|---|---|
| Available | #22C55E | Tickets are available |
| Locked / Held | #F59E0B | Tickets are temporarily held |
| Sold Out | #EF4444 | No tickets are available |
| Sync Pending | #38BDF8 | Offline request is waiting for synchronization |
| Confirmed | #22C55E | Booking is confirmed by backend |

Important:
- Always combine status colors with meaningful text and icons.
- Do not use color as the only way to communicate a status.
- Backend responses determine the actual booking state.

## 4. Typography

Font family: Sans-serif.

The current application uses a sans-serif font stack. The final implementation should use one consistent font across the application.

| Element | Recommended Size | Weight |
|---|---|---|
| Page heading | 28–36px | 700 |
| Section heading | 20–24px | 600 |
| Card heading | 16–18px | 600 |
| Body text | 14–16px | 400 |
| Caption | 13–14px | 400 |
| Small text | 12px | 400 |

Typography guidelines:
- Use clear heading hierarchy.
- Keep body text readable.
- Use stronger font weights for important actions.
- Avoid very small text for important information.

## 5. Spacing Scale

| Token | Value |
|---|---|
| XS | 4px |
| SM | 8px |
| MD | 16px |
| LG | 24px |
| XL | 32px |
| XXL | 48px |

Use consistent spacing between sections, cards, buttons, and form elements.

## 6. Component Radius

| Component | Recommended Radius |
|---|---|
| Buttons | 8px |
| Input fields | 8px |
| Cards | 12px |
| Dialogs | 16px |
| Large panels | 16px |

## 7. Accessibility Tokens

| Property | Value |
|---|---|
| Focus outline | 3px solid #A78BFA |
| Focus outline offset | 2px |
| Minimum recommended touch target | 44px × 44px |
| Normal text contrast target | 4.5:1 |
| Large text contrast target | 3:1 |

Accessibility guidelines:
- Provide visible keyboard focus.
- Maintain sufficient foreground and background contrast.
- Use accessible labels for inputs.
- Provide clear validation messages.
- Support keyboard navigation.
- Respect reduced-motion preferences.

## 8. Responsive Breakpoints

| Device | Width |
|---|---|
| Mobile | Below 640px |
| Tablet | 640px – 1023px |
| Desktop | 1024px and above |

Responsive guidelines:
- Mobile: Single-column layouts and full-width controls where appropriate.
- Tablet: Flexible grids and adjusted spacing.
- Desktop: Multi-column event browsing and spacious content layouts.

## 9. Interactive States

| Component State | Visual Behaviour |
|---|---|
| Default | Normal component appearance |
| Hover | Slight visual highlight |
| Focus | Visible accent outline |
| Active | Clear pressed or selected appearance |
| Disabled | Reduced emphasis and disabled interaction |
| Loading | Loading indicator with appropriate message |
| Error | Clear error message and visual indicator |
| Success | Confirmation message and status indicator |

## 10. General Admission Booking States

- Available: Users can request tickets.
- Locked / Held: Inventory is temporarily held during a reservation.
- Sold Out: Ticket inventory is unavailable.
- Sync Pending: An offline request is waiting for backend synchronization.
- Confirmed: Backend has confirmed the booking.

These states apply to ticket inventory, not individual seats.

## 11. Implementation Notes

- Use centralized CSS variables wherever possible.
- Reuse design tokens across components.
- Maintain consistent colors, spacing, typography, and border radius.
- Ensure responsive behaviour across screen sizes.
- Validate color contrast and keyboard focus during accessibility testing.
- Update tokens when the final design is approved by the team.

## 12. Design Status

The tokens are aligned with the current dark purple frontend theme.

Final typography, status colors, accessibility checks, and design approval are pending team review.
