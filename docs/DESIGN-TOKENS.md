
# PS-07 – Design Tokens

## 1. Color Palette

| Token | Value | Purpose |
|---|---|---|
| Primary | #4F46E5 | Primary buttons and links |
| Secondary | #7C3AED | Secondary actions |
| Accent | #DB2777 | Highlights |
| Background | #F8FAFC | Main background |
| Surface | #FFFFFF | Cards and panels |
| Text | #0F172A | Main text |
| Muted | #475569 | Secondary text |
| Border | #CBD5E1 | Borders |

## 2. Seat State Colors

| State | Background | Text |
|---|---|---|
| Available | #DCFCE7 | #166534 |
| Locked | #FEF3C7 | #92400E |
| Booked | #FEE2E2 | #991B1B |
| Syncing | #E0F2FE | #075985 |

## 3. Typography

Font family: Inter

| Element | Size | Weight |
|---|---|---|
| Page heading | 28px | 700 |
| Section heading | 20px | 600 |
| Card heading | 16px | 600 |
| Body | 16px | 400 |
| Caption | 14px | 400 |
| Small text | 12px | 400 |

## 4. Spacing

| Token | Value |
|---|---|
| XS | 4px |
| SM | 8px |
| MD | 16px |
| LG | 24px |
| XL | 32px |
| XXL | 48px |

## 5. Component Radius

| Component | Radius |
|---|---|
| Buttons | 8px |
| Input fields | 8px |
| Cards | 12px |
| Dialogs | 16px |

## 6. Accessibility Tokens

- Focus outline: 3px solid #4338CA
- Focus outline offset: 2px
- Minimum recommended touch target: 44px × 44px
- Normal text contrast target: 4.5:1
- Large text contrast target: 3:1

## 7. Responsive Breakpoints

| Device | Width |
|---|---|
| Mobile | Below 640px |
| Tablet | 640px – 1023px |
| Desktop | 1024px and above |

## 8. Seat Interaction

- Available: Can be selected.
- Locked: Cannot be selected.
- Booked: Cannot be selected.
- Syncing: Temporarily disable interaction until synchronization finishes.

## 9. Implementation Notes

Use centralized CSS variables for these tokens. All components should reuse the same colors, typography, spacing and radius values.

These values are proposed design tokens and should be finalized after team review.
