# UI Design Concept & Design System
## Modern, Clean, and Distinctive Interface Design Standards

| | |
|---|---|
| **Primary Platform** | Web App (Mobile-first Responsive, PWA Ready) |
| **Core Principles** | Fast, Intuitive, Modern, and Lightweight |
| **Primary Fonts** | **Plus Jakarta Sans** (Heading/Display/Numbers) + **Inter** (Body) |
| **Styling Framework**| Tailwind CSS + Radix UI / shadcn/ui primitives |

---

# SECTION 1 — DESIGN PHILOSOPHY

## 1.1 Three Core Principles
1. **"One Screen, One Primary Action":**
   Every view has a clear and dominant Call-to-Action (CTA). Users should never be confused about what step to take next.
2. **"Data & Content Are the Protagonists":**
   Metrics, critical statuses, and actionable outputs are the highest visual contrast elements. Decorative elements must never compromise data readability.
3. **"Modernity Without Clutter":**
   Leverage generous whitespace, gentle rounded corners (16px radius for cards), and subtle elevation shadows. Avoid dated, dense, and rigid enterprise aesthetics.

## 1.2 Visual Personality
| We ARE | We are NOT |
|---|---|
| Clean, spacious, and distinctive | Rigid, overly formal, and bureaucratic |
| Modern typography with crisp contrast | Browser default fonts (generic Times/Arial) |
| Smooth and responsive micro-interactions | Packed with sluggish animations that disrupt user flow |
| Consistent functional color semantics | Colorful without clear purpose or hierarchy |

---

# SECTION 2 — DESIGN SYSTEM TOKENS

## 2.1 Color Palette

### Brand Colors
| Token | Example Hex | Usage |
|---|---|---|
| `brand-primary` | `#4F46E5` (Modern Indigo) | Primary CTA buttons, active state, key highlights |
| `brand-primary-hover` | `#4338CA` | Hover / active state on primary buttons |
| `brand-soft` | `#EEF2FF` | Badge backgrounds, accent cards, selected state |

### Functional Colors
| Token | Hex | Meaning & Usage |
|---|---|---|
| `success` | `#16A34A` (Emerald) | Success status, incoming transactions, valid verification |
| `danger` | `#DC2626` (Red) | Error messages, destructive actions, critical warnings |
| `warning` | `#F59E0B` (Amber) | Soft warnings, quota limits, pending review |
| `info` | `#2563EB` (Blue) | Informational hints, navigation links |

### Neutral Colors
| Token | Hex | Usage |
|---|---|---|
| `surface-bg` | `#F8FAFC` (Slate-50) | Main application page background |
| `surface-card` | `#FFFFFF` | Card background, modals, popovers |
| `border-subtle` | `#E2E8F0` (Slate-200) | Subtle card borders and dividers |
| `text-primary` | `#0F172A` (Slate-900) | Headings, primary metrics, high-contrast text |
| `text-secondary` | `#475569` (Slate-600) | Secondary labels, supporting descriptions |
| `text-muted` | `#94A3B8` (Slate-400) | Form placeholders, disabled text |

---

## 2.2 Typography

- **Display / Heading / Numbers:** `Plus Jakarta Sans` (modern geometric sans-serif optimized for display legibility).
- **Body / Paragraphs / Forms:** `Inter` (optimized for high legibility across all screen sizes).
- **Numeric / Statistics:** Must use CSS class `tabular-nums` so numeric digits align vertically in tables or lists.

---

## 2.3 Radius, Spacing & Elevation

| Element | Token / Value | Implementation Notes |
|---|---|---|
| Content Card (`Card`) | `rounded-2xl` (16px) | Delivers a welcoming, modern appearance |
| Buttons & Form Inputs | `rounded-xl` (12px) | Minimum touch target size of 48px height |
| Badges & Avatars | `rounded-full` | Fully rounded pill/circle visual elements |
| Card Shadow | `shadow-sm` | `0 1px 3px 0 rgba(0, 0, 0, 0.05)` |
| Modal Dialog Shadow | `shadow-xl` | Distinct elevation with soft backdrop blur |
| Card Border | `border border-slate-100` | Thin border for clean visual separation |

---

# SECTION 3 — COMPONENT PATTERNS

1. **Empty State:** Never leave a screen blank; always include a simple illustration/icon, friendly copy, and an action button to create the first item.
2. **Skeleton Loading:** Use skeleton loading shimmer effects rather than full-screen spinners for better perceived render performance.
3. **Form Feedback:** Real-time inline validation when a field loses focus (*onBlur*), with friendly error messages below the input field.
