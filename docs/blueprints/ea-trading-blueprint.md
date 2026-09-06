# Algorithmic & EA Trading System Architecture Blueprint

Dokumen ini adalah cetak biru teknis untuk merancang, membangun, menguji, dan mengoperasikan **Expert Advisor (EA) & Algorithmic Trading Systems** (MQL5/MQL4, Python ccxt, MetaAPI, atau FIX Protocol) dengan standar manajemen risiko institusional.

---

## 🏛️ 1. Arsitektur Komponen Sistem Trading Algoritmik

Sistem trading algoritmik memisahkan logika analisis pasar dengan eksekusi dan gerbang kontrol risiko:

```
[Market Data Ingestion Tier]
  ├── Real-time Tick Feed & Candlesticks (WebSocket / FIX Protocol / MQL OnTick)
  ├── News Calendar Filter (Economic High-Impact Event API)
  └── Market Depth & Spread Monitor
           │
           ▼
[Strategy & Quantitative Signal Engine]
  ├── Indikator Teknis & Price Action Logic
  ├── Filter Volatilitas (ATR / Bollinger Bandwidth)
  └── Sinyal Order: BUY / SELL / CLOSE / MODIFY
           │
           ▼
[Pre-Trade Risk Management Gate (KONTROL WAJIB)]
  ├── Daily Drawdown Validator (Cek apakah batas max DD tercapai)
  ├── Account Equity & Margin Check (Cek kecukupan free margin)
  ├── Dynamic Lot Calculator (Kalkulasi lot berdasarkan % risiko modal)
  ├── Spread & Slippage Filter (Batalkan jika spread melebar)
  └── Maximum Simultaneous Exposure Check (Batasi total lot/open trades)
           │
           ▼ (Hanya diteruskan jika lolos seluruh filter risiko)
[Order Execution Engine]
  ├── Broker / Exchange Bridge (MetaTrader Trade Library / CCXT / FIX API)
  ├── Order Timeout & Re-quote Handler
  └── State Machine: PENDING -> EXECUTED -> SL/TP_HIT -> CLOSED
           │
           ▼
[Post-Trade & Observability Tier]
  ├── Trade Audit Log (Tercatat ke PostgreSQL dengan ID transaksi unik)
  ├── Emergency Circuit Breaker Watchdog (Heartbeat & Health Monitor)
  └── Notifikasi Real-time (Telegram Bot / Discord Webhook / Push Notif)
```

---

## ⚖️ 2. Doktrin Proteksi Modal & Rumus Manajemen Risiko

### 2.1 Kalkulasi Lot Dinamis (Dynamic Position Sizing)
❌ **Dilarang Keras:** Menggunakan lot statis sembarangan (misal selalu 1.0 lot) atau strategi martingal pelipatgandaan tanpa batas.  
✅ **Rumus Resmi Kalkulasi Lot:**
Ukuran posisi harus dihitung dinamis berdasarkan persentase toleransi risiko dari ekuitas akun saat ini:

$$\text{Risk Amount (\$)} = \text{Account Equity} \times \text{Risk Percentage (misal 1\%)}$$

$$\text{Lot Size} = \frac{\text{Risk Amount (\textit{USD})}}{\text{Stop Loss Distance (Pips/Points)} \times \text{Tick Value per Lot}}$$

*Contoh Kasus:*
- Equity Akun = \$10,000
- Risk per Trade = 1% (\$100)
- Jarak Stop Loss = 50 pips
- Pip Value untuk EURUSD per 1.0 lot = \$10
- Maka Lot Size = $\$100 / (50 \times \$10) = 0.20\text{ lot}$.

### 2.2 Emergency Circuit Breaker (Max Daily Drawdown Kill-Switch)
Setiap EA atau bot trading wajib memiliki fungsi pemutus sirkuit darurat:
```text
Jika (Equity Saat Ini) <= (Equity Awal Hari * (1 - Max_Daily_Drawdown_Limit%)):
    1. Eksekusi CloseAllPositions() segera pada harga pasar terbaik.
    2. Batalkan seluruh pending orders (CancelAllPendingOrders()).
    3. Nonaktifkan flag izin trading (TradingEnabled = FALSE).
    4. Kirim sinyal alarm bahaya ke Telegram & Email operator.
    5. Kunci sistem hingga intervensi manual atau pergantian sesi hari berikutnya.
```

### 2.3 Higiene Hak Akses Kunci API (API Key Permission Segregation)
Saat menghubungkan bot trading ke bursa kripto (Binance, Bybit) atau broker institusi:
- **Izin yang Diizinkan:** `Read Info (Query)`, `Spot Trading`, `Futures Trading`.
- **IZIN YANG HARUS DINONAKTIFKAN (STRICTLY PROHIBITED):**  
  ❌ `Enable Withdrawals` (Penarikan Dana).  
  *Alasan:* Jika server EA diretas, penyerang tidak akan pernah bisa mencuri atau menarik modal trading keluar dari akun bursa!

---

## 🧪 3. Standard Operating Procedure (SOP) Pengujian & Anti-Overfitting

Algoritma trading dilarang dioperasikan pada dana riil sebelum melalui 5 gerbang validasi:

| Tahap Pengujian | Periode & Dataset | Kriteria Lolos (Acceptance Criteria) |
| :--- | :--- | :--- |
| **1. In-Sample Backtest** | 70% riwayat data historis (misal 2020-2023) | Profit Factor > 1.5, Max Drawdown < 15%, Sharpe Ratio > 1.2. |
| **2. Out-of-Sample Test** | 30% riwayat data yang belum pernah dilihat model | Kinerja tidak drop > 25% dibanding in-sample (bukti anti-curve fitting). |
| **3. Walk-Forward Analysis** | Uji jendela bergulir (*Rolling Window*) | Konsistensi profitabilitas di berbagai rezim pasar (trending vs sideways). |
| **4. Paper Trading / Demo** | Minimum 30 hari kalender pada live data | Eksekusi slippage dan latensi broker sesuai estimasi model. |
| **5. Incubation (Micro/Cent)** | Akun riil bernilai kecil (1-5% modal rencana) | Verifikasi eksekusi live order, spread nyata broker, dan stabilitas VPS. |

---

## 🖥️ 4. Infrastruktur VPS & Watchdog Heartbeat

1. **Hosting VPS Low-Latency:**
   - Ditempatkan di data center yang paling dekat dengan server broker (misal Equinix LD4 London untuk Forex, atau Tokyo/Virginia untuk Crypto).
   - Latensi ping eksekusi di bawah 5 ms.
2. **Watchdog Heartbeat:**
   - Script independen mengirim *ping heartbeat* setiap 60 detik.
   - Jika terminal MT5 atau proses Python macet (*freeze*), watchdog otomatis me-restart terminal dan mengirim alert darurat ke ponsel operator.

---

## 📋 5. Checklist Verifikasi Sebelum Live Trading

- [ ] Stop Loss otomatis selalu terpasang pada saat order dikirim (*never enter market without SL*).
- [ ] Batas *Max Daily Drawdown* teruji memutus sirkuit pada akun simulasi.
- [ ] Filter spread dan filter berita ekonomi (*Economic News Filter*) aktif.
- [ ] Hak akses *Withdrawal* pada API key exchange 100% dinonaktifkan.
- [ ] Database log mencatat setiap tiket order, waktu eksekusi, dan selisih slippage.
