# UI Design Concept & Design System
## Standar Desain Antarmuka Modern, Bersih, dan Berkarakter

| | |
|---|---|
| **Platform Utama** | Web App (Mobile-first Responsive, PWA Ready) |
| **Prinsip Utama** | Cepat, Intuitif, Modern, dan Ringan |
| **Font Utama** | **Plus Jakarta Sans** (Heading/Display/Angka) + **Inter** (Body) |
| **Styling Framework**| Tailwind CSS + Radix UI / shadcn/ui primitives |

---

# BAGIAN 1 — FILOSOFI DESAIN

## 1.1 Tiga Prinsip Inti
1. **"Satu Layar, Satu Pekerjaan Utama":**
   Setiap tampilan memiliki Call-to-Action (CTA) yang jelas dan dominan. Pengguna tidak boleh bingung mencari langkah selanjutnya.
2. **"Data & Konten adalah Protagonis":**
   Angka, status penting, dan hasil kerja adalah elemen visual paling kontras. Elemen dekorasi tidak boleh mengaburkan keterbacaan data.
3. **"Modernitas Tanpa Clutter":**
   Gunakan ruang napas (*whitespace*) yang lapang, sudut membulat yang lembut (radius 16px untuk kartu), dan bayangan halus (*subtle elevation*). Hindari gaya enterprise kuno yang padat dan kaku.

## 1.2 Personality Visual
| Kami ADALAH | Kami BUKAN |
|---|---|
| Bersih, lapang, dan berkarakter | Kaku, formal berlebihan, dan birokratis |
| Tipografi modern dengan kontras tajam | Font default browser (Times/Arial generik) |
| Micro-interactions yang halus dan cepat | Penuh animasi lambat yang mengganggu flow |
| Konsisten pada makna warna fungsional | Warna-warni tanpa hierarki tujuan |

---

# BAGIAN 2 — DESIGN SYSTEM TOKENS

## 2.1 Palet Warna

### Warna Brand
| Token | Hex Contoh | Penggunaan |
|---|---|---|
| `brand-primary` | `#4F46E5` (Indigo modern) | Tombol CTA utama, status aktif, highlight penting |
| `brand-primary-hover` | `#4338CA` | State hover / active pada tombol utama |
| `brand-soft` | `#EEF2FF` | Background badge, kartu aksen, state selected |

### Warna Fungsional
| Token | Hex | Makna & Penggunaan |
|---|---|---|
| `success` | `#16A34A` (Emerald) | Status berhasil, transaksi masuk, verifikasi valid |
| `danger` | `#DC2626` (Red) | Pesan error, aksi destruktif, peringatan kritis |
| `warning` | `#F59E0B` (Amber) | Peringatan lembut, kuota menipis, pending review |
| `info` | `#2563EB` (Blue) | Petunjuk informatif, link navigasi |

### Warna Netral
| Token | Hex | Penggunaan |
|---|---|---|
| `surface-bg` | `#F8FAFC` (Slate-50) | Background halaman utama aplikasi |
| `surface-card` | `#FFFFFF` | Background kartu, modal, popover |
| `border-subtle` | `#E2E8F0` (Slate-200) | Garis pembatas kartu halus |
| `text-primary` | `#0F172A` (Slate-900) | Judul, angka utama, teks dengan kontras tinggi |
| `text-secondary` | `#475569` (Slate-600) | Label sekunder, deskripsi pendukung |
| `text-muted` | `#94A3B8` (Slate-400) | Placeholder form, teks non-aktif |

---

## 2.2 Tipografi

- **Display / Heading / Angka:** `Plus Jakarta Sans` (font modern rancangan desainer Indonesia).
- **Body / Paragraf / Form:** `Inter` (optimal untuk keterbacaan tinggi di berbagai ukuran layar).
- **Angka Nominal / Statistik:** Wajib menggunakan class CSS `tabular-nums` agar digit angka sejajar vertikal saat ditampilkan dalam tabel atau daftar.

---

## 2.3 Radius, Spacing & Elevation

| Elemen | Token / Nilai | Catatan Implementasi |
|---|---|---|
| Kartu Konten (`Card`) | `rounded-2xl` (16px) | Menghasilkan kesan ramah dan modern |
| Tombol & Input Form | `rounded-xl` (12px) | Ukuran target sentuh minimal 48px tinggi |
| Badge & Avatar | `rounded-full` | Elemen visual bulat penuh |
| Card Shadow | `shadow-sm` | `0 1px 3px 0 rgba(0, 0, 0, 0.05)` |
| Modal Dialog Shadow | `shadow-xl` | Bayangan tegas dengan backdrop blur lembut |
| Card Border | `border border-slate-100` | Border tipis untuk pemisah visual yang bersih |

---

# BAGIAN 3 — POLA KOMPONEN

1. **Empty State:** Tidak boleh layar kosong; wajib ada ilustrasi/icon sederhana, pesan ramah, dan tombol aksi untuk membuat item pertama.
2. **Skeleton Loading:** Gunakan skeleton loading shimmer daripada spinner layar penuh untuk persepsi kecepatan render yang lebih baik.
3. **Form Feedback:** Validasi inline real-time saat field kehilangan fokus (*onBlur*), dengan pesan error yang ramah di bawah input.
