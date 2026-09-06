---
version: 1.0.0
name: Aegis-Forge-Enterprise-Design-System
description: A modern, clean, and highly functional enterprise interface system optimized for SaaS, Web Apps, and Financial Dashboards. Anchored on a spacious Slate canvas and Modern Indigo (#4f46e5) as the primary brand voltage. The typography relies on a dual-stack: Plus Jakarta Sans for crisp, geometric headings and numbers, with Inter providing supreme legibility for dense data tables and body copy. Unlike rigid traditional enterprise software, the system uses generous whitespace, gentle 12-16px corner radii, and subtle elevation to reduce cognitive load while maintaining high data density.

colors:
  primary: "#4f46e5"
  primary-hover: "#4338ca"
  primary-soft: "#eef2ff"
  primary-disabled: "#a5b4fc"
  success: "#16a34a"
  success-soft: "#dcfce7"
  danger: "#dc2626"
  danger-hover: "#b91c1c"
  danger-soft: "#fee2e2"
  warning: "#f59e0b"
  warning-soft: "#fef3c7"
  info: "#2563eb"
  ink-primary: "#0f172a"
  ink-secondary: "#475569"
  ink-muted: "#94a3b8"
  border-subtle: "#f1f5f9"
  border-default: "#e2e8f0"
  border-strong: "#cbd5e1"
  canvas: "#f8fafc"
  surface-card: "#ffffff"
  surface-hover: "#f8fafc"
  on-primary: "#ffffff"
  on-dark: "#ffffff"
  scrim: "#0f172a"

typography:
  display-xl:
    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif"
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.02em
  display-lg:
    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif"
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.33
    letterSpacing: -0.01em
  title-md:
    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif"
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: 0
  tabular-metric:
    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif"
    fontSize: 36px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
    fontVariantNumeric: "tabular-nums"
  body-md:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.57
    letterSpacing: 0
  body-sm:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  caption:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.33
    letterSpacing: 0
  badge-label:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.33
    letterSpacing: 0.02em
  button-md:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.43
    letterSpacing: 0.01em
  nav-link:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: 0

rounded:
  none: 0px
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px

spacing:
  xxs: 2px
  xs: 4px
  sm: 8px
  md: 12px
  base: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  section: 64px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.lg}"
    padding: 10px 16px
    height: 40px
  button-primary-active:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.lg}"
  button-secondary:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink-primary}"
    border: "1px solid {colors.border-default}"
    typography: "{typography.button-md}"
    rounded: "{rounded.lg}"
    padding: 10px 16px
    height: 40px
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.lg}"
    padding: 10px 16px
    height: 40px
  content-card:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink-primary}"
    border: "1px solid {colors.border-subtle}"
    rounded: "{rounded.xl}"
    padding: 24px
  data-table-header:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.caption}"
    padding: 12px 16px
  data-table-row:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink-primary}"
    typography: "{typography.body-md}"
    borderBottom: "1px solid {colors.border-subtle}"
    padding: 16px
  status-badge-success:
    backgroundColor: "{colors.success-soft}"
    textColor: "{colors.success}"
    typography: "{typography.badge-label}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  status-badge-danger:
    backgroundColor: "{colors.danger-soft}"
    textColor: "{colors.danger}"
    typography: "{typography.badge-label}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  text-input:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink-primary}"
    border: "1px solid {colors.border-default}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: 10px 12px
    height: 40px
  side-nav-active:
    backgroundColor: "{colors.primary-soft}"
    textColor: "{colors.primary}"
    typography: "{typography.nav-link}"
    rounded: "{rounded.md}"
    padding: 8px 12px
  side-nav-inactive:
    backgroundColor: transparent
    textColor: "{colors.ink-secondary}"
    typography: "{typography.nav-link}"
    rounded: "{rounded.md}"
    padding: 8px 12px
---

## Overview

The Aegis Forge design system breaks away from the dated, cluttered aesthetic of legacy enterprise software. It embraces a clean, breathable interface optimized for SaaS, Web Apps, and Financial Dashboards. The base canvas is **Slate-50** (`{colors.canvas}` — #f8fafc) providing a gentle contrast against pure white (`{colors.surface-card}` — #ffffff) content cards. **Modern Indigo** (`{colors.primary}` — #4f46e5) acts as the central brand voltage, steering the user towards primary actions and active states. 

The system utilizes a dual-font strategy. **Plus Jakarta Sans** is deployed for display headings and critical metrics (`{typography.tabular-metric}`), giving the interface a crisp, geometric modernity. **Inter** handles all body copy, data tables, and forms, providing unparalleled legibility for data-dense environments.

Unlike traditional enterprise interfaces that use sharp, severe corners, Aegis Forge employs a welcoming shape language. Buttons and inputs utilize a 12px radius (`{rounded.lg}`), while major content cards use a 16px radius (`{rounded.xl}`). This softness reduces cognitive fatigue when scanning complex dashboards.

**Key Characteristics:**
- **Dual Typography:** `Plus Jakarta Sans` for headers and numbers; `Inter` for dense body text and data tables.
- **Data as the Protagonist:** Metrics and table data use high-contrast Slate-900 (`{colors.ink-primary}`). Decorative elements never compete with data readability.
- **Semantic Status Markers:** Deep reliance on green (`{colors.success}`) and red (`{colors.danger}`) paired with soft background tints for immediate visual parsing of transaction states and system health.
- **Tabular Numerals:** All numeric statistics and currency values strictly use `tabular-nums` so columns align perfectly.
- **One Screen, One Primary Action:** Layouts prioritize a single, distinct primary CTA button per view, eliminating decision fatigue.

## Colors

### Brand & Canvas
- **Modern Indigo** (`{colors.primary}` — #4f46e5): The single brand color. Used for primary CTA backgrounds, active navigation states, and key data highlights.
- **Indigo Hover** (`{colors.primary-hover}` — #4338ca): The press / pointer-hover variant — slightly darker for tactile feedback.
- **Canvas** (`{colors.canvas}` — #f8fafc): The default page floor. A very light slate gray that allows white cards to pop.
- **Card Surface** (`{colors.surface-card}` — #ffffff): Pure white. Used for all data tables, modals, and content containers.

### Text & Ink
- **Ink Primary** (`{colors.ink-primary}` — #0f172a): Slate-900. The dominant text color for headings, primary data, and user inputs. Highly legible, but softer than pure black.
- **Ink Secondary** (`{colors.ink-secondary}` — #475569): Slate-600. Used for table headers, sub-labels, and supporting descriptions.
- **Ink Muted** (`{colors.ink-muted}` — #94a3b8): Slate-400. Reserved for input placeholders and disabled text.

### Semantic & Status
- **Success** (`{colors.success}` — #16a34a): Used for approved Maker-Checker requests, successful transactions, and positive metrics. Typically paired with `{colors.success-soft}` for badge backgrounds.
- **Danger** (`{colors.danger}` — #dc2626): Used for destructive actions (Delete, Reject), system errors, and negative metrics. Paired with `{colors.danger-soft}`.
- **Warning** (`{colors.warning}` — #f59e0b): Used for pending reviews, quota limits, and soft alerts.
- **Info** (`{colors.info}` — #2563eb): Used for informational tooltips and system updates.

### Borders
- **Border Subtle** (`{colors.border-subtle}` — #f1f5f9): Barely-there dividers for clean row separation in dense data tables.
- **Border Default** (`{colors.border-default}` — #e2e8f0): The default outline for inputs, secondary buttons, and card borders.

## Typography

### Font Family
The system mandates a dual-stack: **Plus Jakarta Sans** for display/numeric and **Inter** for body. Fallbacks route to standard system UI fonts.

### Hierarchy

| Token | Size | Weight | Line Height | Use |
|---|---|---|---|---|
| `{typography.tabular-metric}` | 36px | 700 | 1.1 | Dashboard primary KPIs, total balances (tabular-nums applied) |
| `{typography.display-xl}` | 32px | 700 | 1.25 | Page primary titles |
| `{typography.display-lg}` | 24px | 600 | 1.33 | Modal headers, major section titles |
| `{typography.title-md}` | 18px | 600 | 1.4 | Card titles, form section headers |
| `{typography.body-md}` | 14px | 400 | 1.57 | Default running text, form inputs, table row data |
| `{typography.body-sm}` | 13px | 400 | 1.5 | Secondary text, timestamp logs |
| `{typography.caption}` | 12px | 500 | 1.33 | Table column headers, input field labels |
| `{typography.badge-label}` | 12px | 600 | 1.33 | Text inside status pills and tags |
| `{typography.button-md}` | 14px | 500 | 1.43 | Primary and secondary button text |

### Principles
Enterprise software handles complex data, so typography must prioritize clarity over character. The `body-md` size is set to 14px (rather than 16px consumer standard) to allow for greater data density in grids and tables without feeling cramped. The `tabular-metric` token is strictly utilized for financial figures to ensure decimal points align flawlessly in vertical stacks.

## Layout

### Spacing System
- **Base unit:** 4px (Tailwind standard scale).
- **Tokens:** `{spacing.xs}` 4px · `{spacing.sm}` 8px · `{spacing.md}` 12px · `{spacing.base}` 16px · `{spacing.lg}` 24px · `{spacing.xl}` 32px · `{spacing.section}` 64px.
- **Card internal padding:** `{spacing.lg}` (24px) for major `{component.content-card}`.
- **Data table density:** `{spacing.base}` (16px) padding for standard rows; can compress to `{spacing.md}` (12px) for high-density variants.

### Grid & Container
- **Dashboard Layout:** Typically a sticky side-navigation (250px width) with a fluid main content area. Max content width is generally capped at 1440px to prevent unreadable line lengths on ultrawide monitors.
- **Forms:** Split into maximum 2-column grids. Single-column preferred for linear flows (e.g., Maker-Checker submissions).

### Whitespace Philosophy
Unlike legacy enterprise tools that cram every pixel, Aegis Forge uses whitespace to group related information conceptually (Gestalt proximity). Sections within a form should be separated by `{spacing.xl}` (32px), creating distinct visual zones without requiring heavy divider lines.

## Elevation

Shadows are used strictly to communicate z-index depth and interactivity, not for decoration.

- **Flat (No Shadow):** The page canvas, form inputs, and flat badges.
- **Card Shadow (`shadow-sm`):** `0 1px 3px 0 rgba(0, 0, 0, 0.05)`. Used on `{component.content-card}` to separate the white surface from the slate canvas.
- **Dropdown/Popover (`shadow-md`):** `0 4px 6px -1px rgba(0, 0, 0, 0.1)`. Used for context menus, select dropdowns, and date pickers.
- **Modal Dialog (`shadow-xl`):** `0 20px 25px -5px rgba(0, 0, 0, 0.1)`. The highest elevation tier, used exclusively for center-screen modals (e.g., confirmation dialogs) paired with a `{colors.scrim}` backdrop blur.

## Components

### Buttons

**`button-primary`** — Indigo fill, white text, 12px radius, 10x16px padding, 40px height. The dominant action on the screen (Save, Submit, Approve).

**`button-secondary`** — White fill, Slate-900 text, 1px Slate-200 border. Used for secondary actions (Cancel, Back, Filter).

**`button-danger`** — Red fill (`{colors.danger}`), white text. Used exclusively for destructive, irreversible actions (Delete Account, Reject Transaction).

### Status Badges

**`status-badge-success`** — A soft green pill (`{colors.success-soft}`) with dark green text (`{colors.success}`). Fully rounded (`{rounded.full}`). Used to mark "Active", "Approved", or "Completed".

**`status-badge-danger`** — A soft red pill with dark red text. Used for "Failed", "Rejected", or "Suspended".

### Data Tables

**`data-table-header`** — Canvas-colored background (`#f8fafc`), Slate-600 uppercase/caption text. Distinct from row data to provide a clear anchor for scanning.

**`data-table-row`** — White surface, Slate-900 text. A subtle 1px border (`{colors.border-subtle}`) separates rows. Pointer cursor and a very faint background tint on hover to assist eye-tracking across wide rows.

### Navigation

**`side-nav-active`** — The active menu item in the sidebar. Uses a soft indigo background (`{colors.primary-soft}`) with deep indigo text. 8px radius (`{rounded.md}`).

**`side-nav-inactive`** — Transparent background, Slate-600 text. Elevates to slightly darker text and background on hover.

### Forms

**`text-input`** — White surface, 1px default border, 12px radius, 40px height. On focus, the border transitions to Modern Indigo (`{colors.primary}`) with a subtle focus ring to ensure WCAG accessibility compliance.

## Responsive Behavior

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Sidebar collapses into a hamburger menu; Data tables overflow horizontally with scroll snap or collapse into card-lists; Form columns stack 1-up. |
| Tablet | 768–1024px | Sidebar can iconify; Grid components flow into 2-up configurations. |
| Desktop | > 1024px | Sidebar pinned left; Data tables display full columns; Forms utilize 2-up grids for related fields. |

## Interactivity & Feedback

- **Empty States:** Never leave a table or dashboard widget blank. Always provide a friendly illustration, a brief explanation of what belongs there, and a `{component.button-primary}` to create the first record.
- **Skeleton Loading:** Use skeleton loading (shimmer) rather than full-screen spinners for dashboards to improve perceived performance and keep the user contextually anchored.
- **Inline Validation:** Forms must validate *onBlur* (when a field loses focus), displaying `{colors.danger}` text immediately below the field instead of waiting for a form submission error.
