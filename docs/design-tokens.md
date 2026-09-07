# Design Tokens & Pipeline

> **Purpose:** Define how design decisions (color, typography, spacing, radius, elevation) flow from a **single source of truth** into every target platform (Web/Tailwind/CSS, Android Compose, iOS SwiftUI, Flutter) — so tokens are written once and consumed everywhere, never hand-copied.
>
> Source tokens live in `docs/ui-design.md` (generated from `docs/ui-design-template.md`, optionally via the `ui-ux-pro-max` skill). This document defines the pipeline that turns them into platform code.

---

## 1. What Is a Design Token?

A **design token** is a named, platform-agnostic design decision — the smallest reusable unit of a design system:

```
color.primary            = #4f46e5
color.danger.soft        = #fee2e2
font.heading.family      = 'Plus Jakarta Sans'
font.body.family         = 'Inter'
spacing.scale.4          = 16px        (4pt grid)
radius.card              = 12px
elevation.card           = 0 1px 3px rgba(15,23,42,.08)
```

**Rule:** Components reference **tokens**, never raw values. ❌ `color: #4f46e5` → ✅ `color: var(--color-primary)` / `theme.colors.primary`.

---

## 2. Token Layers (3 tiers)

| Tier | Name | Example | Purpose |
|---|---|---|---|
| 1 | **Primitive** | `indigo-600 = #4f46e5` | Raw values; never used directly by components |
| 2 | **Semantic** | `color.primary = {indigo-600}` | Meaning-driven; components use these |
| 3 | **Component** | `button.primary.bg = {color.primary}` | Scoped to a component; references semantic |

> The semantic tier is what enables **theming** (light/dark, brand variants) without touching components. Dark mode = swap tier-2 mappings, keep tier-1 primitives.

---

## 3. The Pipeline (Tokens → Platforms)

```
docs/ui-design.md  (source of truth, YAML front-matter)
        │
        ▼
  tokens.json      (normalized, W3C DTCG-inspired format)
        │
        ▼
  Build tool (Style Dictionary — recommended)
        ├─► CSS variables        (--color-primary)
        ├─► Tailwind config      (theme.extend.colors)
        ├─► Android Compose      (Color.kt / Theme.kt)
        ├─► iOS SwiftUI          (Color+Tokens.swift / .xcassets)
        └─► Flutter              (app_theme.dart / tokens.g.dart)
```

### Recommended tool: Style Dictionary (`amzn/style-dictionary`, Apache-2.0)
Industry-standard transform engine: one token file in → many platform formats out. (Status in `docs/research/EXTERNAL-TOOLS.md`: move from 🧪 Experimental → ✅ Adopted when you wire it up.)

**Minimal config (`config.json`):**
```json
{
  "source": ["design/tokens.json"],
  "platforms": {
    "css":     { "transformGroup": "css",     "buildPath": "build/css/",     "files": [{ "destination": "tokens.css", "format": "css/variables" }] },
    "tailwind":{ "transformGroup": "js",      "buildPath": "build/tailwind/","files": [{ "destination": "tokens.js",   "format": "javascript/es6" }] },
    "compose": { "transformGroup": "compose", "buildPath": "build/compose/", "files": [{ "destination": "Tokens.kt",   "format": "compose/object" }] },
    "ios":     { "transformGroup": "ios-swift","buildPath": "build/ios/",    "files": [{ "destination": "Tokens.swift","format": "ios-swift/class.swift" }] }
  }
}
```

---

## 4. Token File Format (tokens.json)

Use the [W3C Design Tokens Community Group](https://tr.designtokens.org/format/)-inspired shape (`$value` / `$type`):

```json
{
  "color": {
    "primitive": {
      "indigo-600": { "$value": "#4f46e5", "$type": "color" },
      "slate-900":  { "$value": "#0f172a", "$type": "color" }
    },
    "semantic": {
      "primary":      { "$value": "{color.primitive.indigo-600}", "$type": "color" },
      "ink-primary":  { "$value": "{color.primitive.slate-900}",  "$type": "color" }
    }
  },
  "spacing": {
    "1": { "$value": "4px",  "$type": "dimension" },
    "4": { "$value": "16px", "$type": "dimension" }
  },
  "radius": {
    "card": { "$value": "12px", "$type": "dimension" }
  }
}
```
`{...}` is a reference to another token — the build tool resolves it per platform.

---

## 5. Platform Consumption

### Web / Tailwind
```js
// tailwind.config.js
import tokens from './build/tailwind/tokens.js'
export default { theme: { extend: { colors: tokens.color, spacing: tokens.spacing } } }
```
```css
/* or plain CSS */
.btn-primary { background: var(--color-primary); border-radius: var(--radius-card); }
```

### Android Compose
```kotlin
// Generated Tokens.kt -> use in your Theme
Button(colors = ButtonDefaults.buttonColors(containerColor = Tokens.ColorPrimary))
```

### iOS SwiftUI
```swift
// Generated Tokens.swift
.foregroundColor(Tokens.colorPrimary)
```

---

## 6. Theming & Dark Mode

- Keep **tier-1 primitives** identical across themes.
- Provide a second set of **tier-2 semantic mappings** for dark mode (`color.canvas`, `color.ink-primary`, `color.surface-card`, etc.).
- Web: emit `[data-theme="dark"] { --color-canvas: ... }` or a `.dark` class; Compose/SwiftUI/Flutter: a dark `ColorScheme`.

---

## 7. Governance & Anti-Drift Rules

1. **Single source:** tokens change ONLY in `docs/ui-design.md` / `tokens.json` — never edit generated files directly.
2. **CI drift-check:** a job regenerates platform outputs and fails if the working tree differs (proves generated files are in sync).
3. **Naming:** `category.property[.variant]` in kebab/dot form; no ad-hoc one-off colors (add a semantic token instead).
4. **Accessibility gate:** any new color token pair used for text must meet WCAG AA contrast (4.5:1) — verify in `docs/frontend-checklist.md`.
5. **Versioning:** token set is versioned with the design system (`version` in the YAML front-matter).

---

## 8. Setup Checklist

- [ ] Tokens authored/normalized into `design/tokens.json` (from `docs/ui-design.md`).
- [ ] Style Dictionary (or equivalent) configured with at least the `css` + `tailwind` platforms.
- [ ] Generated outputs consumed by the app (no raw hex left in components — spot-check).
- [ ] Dark-mode semantic mapping defined.
- [ ] CI drift-check job added.
- [ ] Contrast verified for all text-on-background semantic pairs (WCAG AA).
