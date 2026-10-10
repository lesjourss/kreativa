# TASKS.md

## Task Breakdown — Platform Jasa Kreatif Digital

Daftar task disusun per epic/fitur, mengikuti urutan prioritas pengerjaan di `AGENTS.md`. Tandai `[ ]` → `[x]` seiring progres.

---

### Epic 0 — Project Setup

- [x] Inisialisasi repo (frontend + backend)
- [x] Setup database (schema awal sesuai `ARCHITECTURE.md`)
- [x] Setup environment config (.env untuk DB, auth secret, dll)
- [x] Setup struktur folder (`frontend/`, `backend/`, `docs/`)

### Epic 1 — Auth & User Management

- [x] Register (Customer & Creator)
- [x] Login & logout (JWT/session)
- [x] Middleware role-based access (`customer`, `creator`, `admin`)
- [x] Edit profil dasar (nama, email, foto)

### Epic 2 — Creative Shop (Creator Store)

- [x] CRUD profil creator (bio, avatar)
- [x] CRUD portofolio (upload gambar/karya + judul + deskripsi)
- [x] CRUD kategori jasa (admin atau data seed awal)
- [x] CRUD jasa (title, deskripsi, kategori)
- [x] CRUD paket jasa (nama paket, harga, estimasi pengerjaan, jumlah revisi)
- [x] Toggle status ketersediaan (menerima/tidak menerima order)
- [x] Halaman publik store creator (dilihat customer)

### Epic 3 — Pencarian & Listing Jasa

- [x] Halaman listing semua jasa
- [x] Filter berdasarkan kategori
- [x] Search berdasarkan keyword (nama jasa/creator)
- [x] Sorting (mis. terbaru, rating tertinggi — opsional MVP)

### Epic 4 — Order Management

- [x] Form brief terstruktur (kebutuhan, referensi, format, deadline, catatan)
- [x] Submit order → tersimpan sebagai `pending`
- [x] Creator terima/tolak order
- [x] Update status order (`diterima → dikerjakan → revisi → selesai`)
- [x] Customer lihat status order real-time (polling/refresh)
- [x] Fitur revisi (customer request revisi + catatan/file)

### Epic 5 — Rating & Review

- [x] Form rating (bintang) + komentar setelah order selesai
- [x] Tampilkan review di halaman store creator
- [x] Hitung rata-rata rating creator

### Epic 6 — Booster (SaaS/Monetization)

- [x] Data paket booster (nama, durasi, harga)
- [x] Halaman pilih booster untuk creator
- [x] Simulasi pembayaran (sandbox/mock)
- [x] Aktivasi booster (set start_date, end_date)
- [x] Logic prioritas tampilan store yang di-boost di listing/search

### Epic 7 — Subscription (Creator) — DIHAPUS dari scope

Fitur subscription dihapus. Kuota creator menjadi unlimited, monetisasi hanya lewat Booster (Epic 6).

### Epic 8 — Polish & Demo Prep

- [x] Responsive check (mobile/desktop)
- [x] Seed data dummy (creator, jasa, order contoh) untuk demo
- [x] Testing alur end-to-end: Customer cari → order → creator kerjakan → selesai → review
- [ ] Siapkan slide/demo untuk presentasi tugas

---

### Prioritas Sprint (Saran Pembagian Waktu)

| Sprint | Fokus |
|---|---|
| Sprint 1 | Epic 0 + Epic 1 (setup & auth) |
| Sprint 2 | Epic 2 (Creative Shop) |
| Sprint 3 | Epic 3 + Epic 4 (listing & order) |
| Sprint 4 | Epic 5 + Epic 6 (review & booster) |
| Sprint 5 | Epic 8 (polish/demo) |

> Sesuaikan jumlah sprint dengan timeline tugas mata kuliah kamu (mis. per minggu).
