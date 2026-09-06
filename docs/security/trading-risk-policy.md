# Institutional Trading Risk Management Policy

Kebijakan ini adalah aturan wajib (*Mandatory Risk Policy*) yang mengikat seluruh bot trading, Expert Advisor (EA), dan algoritma kuantitatif yang dikembangkan menggunakan Baseline ini.

---

## 🛑 1. Prinsip Utama: Proteksi Modal (Capital Preservation First)

Tujuan utama sistem trading algoritmik bukanlah memaksimalkan persentase keuntungan jangka pendek, melainkan **menjaga ketahanan modal terhadap kebangkrutan (*Risk of Ruin = 0%*)** di segala rezim pasar (ekstrem, sideways, atau krisis likuiditas).

---

## 📊 2. Batas Parameter Risiko Wajib (Mandatory Thresholds)

| Parameter Risiko | Batas Maksimum yang Diizinkan | Tindakan Otomatis Sistem |
| :--- | :--- | :--- |
| **Maksimum Risiko per Trade** | **1.0% s.d. 2.0%** dari total Equity | Lot dihitung dinamis; tolak order jika risiko melebihi 2%. |
| **Maksimum Daily Drawdown** | **5.0%** dari saldo awal hari (00:00 GMT) | **Circuit Breaker:** Tutup seluruh posisi, batalkan pending orders, kunci trading hari itu. |
| **Maksimum Total Drawdown** | **10.0%** dari High Watermark Equity | **Hard Kill-Switch:** EA dinonaktifkan total; wajib evaluasi manual arsitektur. |
| **Maksimum Open Exposure** | **3 Posisi Bersamaan** per pair mata uang | Tolak sinyal baru hingga ada posisi yang ditutup. |
| **Maksimum Spread Toleransi** | **2.5x** dari rata-rata spread normal | Tolak eksekusi order (cegah spread melebar saat rilis berita). |

---

## ⚡ 3. Protokol Circuit Breaker & Emergency Kill-Switch

Setiap EA wajib memiliki fungsi pemutus sirkuit mandiri (*Autonomous Circuit Breaker*):

```
┌────────────────────────────────────────────────────────┐
│               MONITORING EKUITAS SETIAP TICK            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
          Apakah Floating Loss >= 5% Equity Hari Ini?
             ├─── TIDAK ──> Lanjutkan Operasional Normal
             │
             └─── YA (RISIKO TERCAPAI)
                    │
                    ▼
          ┌──────────────────────────────────────────────┐
          │     🚨 EKSEKUSI CIRCUIT BREAKER AKTIF        │
          ├──────────────────────────────────────────────┤
          │ 1. Panggil OrderCloseAll() seluruh posisi    │
          │ 2. Panggil OrderCancelAll() pending orders   │
          │ 3. Set GlobalVariable: TRADING_HALTED = TRUE │
          │ 4. Kirim notifikasi darurat Telegram/SMS/API │
          │ 5. Bunyikan alert log di PostgreSQL DB       │
          └──────────────────────────────────────────────┘
```

---

## 🔐 4. Pemisahan Hak Akses Kunci API (API Key Hardening)

Pada integrasi broker institusi atau exchange kripto via REST/WebSocket/FIX:

1. **Prinsip Hak Akses Minimal (PoLP):**
   - Hak Akses yang Diizinkan: **Read Account Info**, **Order Create**, **Order Cancel**.
   - ❌ **HAK AKSES YANG DILARANG KERAS: WITHDRAWAL / PENARIKAN DANA.**
2. **IP Whitelisting Wajib:**
   - Kunci API wajib dikunci (*IP whitelisted*) hanya ke alamat IP statis server VPS trading resmi.
3. **Penyimpanan Kunci API:**
   - Dilarang menyimpan API secret dalam kode sumber. Wajib menggunakan environment variable yang diinjeksi via secret manager aman.

---

## 📰 5. Filter Berita Ekonomi Dampak Tinggi (High-Impact News Blackout)

Sistem wajib menghentikan pembukaan posisi baru selama jendela waktu kritis:
- **15 menit sebelum** rilis berita *High Impact* (NFP, CPI, Keputusan Suku Bunga FOMC/ECB).
- **15 menit setelah** rilis berita, hingga volatilitas spread kembali ke rentang normal.
- Posisi yang sudah berjalan wajib dipastikan memiliki Stop Loss yang valid sebelum jendela berita dimulai.

---

## 📝 6. Audit Logging & Rekonsiliasi Forensik

Setiap order yang dieksekusi wajib mencatat data ke database log:
- **Ticket ID & Client Order ID**
- **Waktu Eksekusi (Presisi Milidetik)**
- **Harga Request vs Harga Riil Eksekusi (Perhitungan Slippage)**
- **Nilai Spread saat Eksekusi**
- **Persentase Risiko & Nilai Stop Loss / Take Profit**
