# Frontend Quality Assurance (QA) Checklist
## Standar Kualitas Rilis Antarmuka (Berdasarkan Front-End-Checklist Standard)

Dokumen ini adalah checklist verifikasi wajib sebelum modul antarmuka dinyatakan selesai (*Ready for Production*).

---

## 1. Keamanan Frontend (Security & IAM Hygiene)
- [ ] **External Links**: Semua tag `<a target="_blank">` WAJIB menyertakan atribut `rel="noopener noreferrer"` untuk mencegah reverse tabnabbing.
- [ ] **Content Security Policy (CSP)**: Header CSP terkonfigurasi untuk mencegah eksekusi inline script tak dikenal (Anti-XSS).
- [ ] **Subresource Integrity (SRI)**: Asset eksternal dari CDN memiliki hash integrity.
- [ ] **Storage Hygiene**: Token rahasia / refresh token DILARANG disimpan di `localStorage` atau `sessionStorage`.
- [ ] **Form Protection**: Semua form memiliki CSRF protection dan sanitasi input client-side.

---

## 2. Aksesibilitas (Accessibility / a11y - WCAG 2.1 AA)
- [ ] **Kontras Warna**: Rasio kontras antara teks dan warna latar belakang minimal **4.5:1** (kecuali teks dekoratif besar minimal 3:1).
- [ ] **Navigasi Keyboard**: Seluruh navigasi, tombol, dan form input dapat dioperasikan 100% menggunakan tombol `Tab`, `Enter`, dan `Spasi`.
- [ ] **Focus Indicator**: Indikator fokus (ring focus) terlihat jelas saat bernavigasi menggunakan keyboard.
- [ ] **Atribut Alt**: Seluruh gambar bermakna informasi memiliki atribut `alt` deskriptif. Gambar murni dekoratif menggunakan `alt=""` atau `aria-hidden="true"`.
- [ ] **Semantic Structure**: Menggunakan tag semantik `<header>`, `<nav>`, `<main>`, `<section>`, dan `<footer>`, bukan sekadar `<div>`.

---

## 3. Performa (Core Web Vitals)
- [ ] **Format Gambar**: Menggunakan format modern (`.webp` atau `.avif`) dengan atribut `loading="lazy"`.
- [ ] **Web Fonts**: Menggunakan `font-display: swap` agar teks langsung terbaca tanpa terhalang unduhan font.
- [ ] **Cumulative Layout Shift (CLS)**: Menetapkan atribut `width` dan `height` eksplisit pada elemen gambar/video untuk mencegah pergeseran layout.
- [ ] **Asset Minification**: Bundling JavaScript dan CSS terkompresi secara optimal.

---

## 4. Metadata, SEO & Social Preview
- [ ] **Favicon**: Tersedia favicon resolusi standar, `apple-touch-icon`, dan manifest file.
- [ ] **OpenGraph Tags**: Tag `og:title`, `og:description`, `og:image`, dan `og:url` terisi lengkap untuk preview di WhatsApp, Telegram, dan media sosial.
- [ ] **Mobile Viewport**: Tag `<meta name="viewport" content="width=device-width, initial-scale=1.0">` terpasang.
- [ ] **Robots & Sitemap**: File `robots.txt` dan `sitemap.xml` tersedia dan valid.

---

## 5. Kepatuhan Privasi (UU PDP Indonesia)
- [ ] **Tautan Kebijakan Privasi**: Tautan jelas ke Privacy Policy dan Terms of Service di footer dan form registrasi.
- [ ] **Consent Banner**: Notifikasi persetujuan pemrosesan data cookie jika menggunakan tracking pihak ketiga.
