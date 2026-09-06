# Frontend Quality Assurance (QA) Checklist
## UI Release Quality Standards (Based on Front-End Checklist Standard)

This document serves as a mandatory verification checklist before any user interface module is marked as *Ready for Production*.

---

## 1. Frontend Security (Security & IAM Hygiene)
- [ ] **External Links**: All `<a target="_blank">` tags MUST include the `rel="noopener noreferrer"` attribute to prevent reverse tabnabbing.
- [ ] **Content Security Policy (CSP)**: CSP header is configured to prevent the execution of untrusted inline scripts (Anti-XSS).
- [ ] **Subresource Integrity (SRI)**: External CDN assets include valid subresource integrity hashes.
- [ ] **Storage Hygiene**: Secret tokens and refresh tokens MUST NEVER be stored in `localStorage` or `sessionStorage`.
- [ ] **Form Protection**: All forms enforce CSRF protection and client-side input sanitization.

---

## 2. Accessibility (a11y - WCAG 2.1 AA)
- [ ] **Color Contrast**: Contrast ratio between text and background color is at least **4.5:1** (except for large decorative text, which requires at least 3:1).
- [ ] **Keyboard Navigation**: All navigation, buttons, and form inputs are 100% operable using `Tab`, `Enter`, and `Space`.
- [ ] **Focus Indicator**: Focus indicator (focus ring) is clearly visible when navigating via keyboard.
- [ ] **Alt Attributes**: All informative images have descriptive `alt` attributes. Purely decorative images use `alt=""` or `aria-hidden="true"`.
- [ ] **Semantic Structure**: Semantic HTML tags (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`) are used rather than generic `<div>` containers.

---

## 3. Performance (Core Web Vitals)
- [ ] **Image Formats**: Modern formats (`.webp` or `.avif`) are utilized with `loading="lazy"` attributes.
- [ ] **Web Fonts**: `font-display: swap` is implemented so text remains readable without blocking font downloads.
- [ ] **Cumulative Layout Shift (CLS)**: Explicit `width` and `height` attributes are set on image and video elements to prevent layout shifts.
- [ ] **Asset Minification**: JavaScript and CSS bundles are minified and compressed optimally.

---

## 4. Metadata, SEO & Social Preview
- [ ] **Favicon**: Standard-resolution favicon, `apple-touch-icon`, and web app manifest file are provided.
- [ ] **OpenGraph Tags**: `og:title`, `og:description`, `og:image`, and `og:url` tags are fully populated for previews on WhatsApp, Telegram, and social media platforms.
- [ ] **Mobile Viewport**: `<meta name="viewport" content="width=device-width, initial-scale=1.0">` tag is present.
- [ ] **Robots & Sitemap**: `robots.txt` and `sitemap.xml` files are available and valid.

---

## 5. Privacy Compliance (Data Privacy Laws (e.g., GDPR))
- [ ] **Privacy Policy Links**: Clear links to the Privacy Policy and Terms of Service are present in the footer and registration forms.
- [ ] **Consent Banner**: Cookie and data processing consent notification is implemented if third-party tracking is used.
