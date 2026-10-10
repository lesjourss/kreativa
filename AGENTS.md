# AGENTS.md

## Development Guidelines — Platform Jasa Kreatif Digital

### 1. Project Context

Project ini adalah **Platform Jasa Kreatif Digital** berbasis **Marketplace** dan **SaaS**, yang menghubungkan penyedia jasa kreatif (freelancer/creator) dengan pelanggan yang membutuhkan jasa seperti desain grafis, ilustrasi, fotografi, videografi, video editing, UI/UX design, motion graphic, 3D design, audio, copywriting, dan konten media sosial.

Tujuan utama platform:
- Menyatukan portofolio, harga, paket layanan, dan komunikasi pemesanan dalam satu tempat (saat ini tersebar di IG, TikTok, X, WhatsApp, Discord, dll).
- Memberi struktur pada proses bisnis penyedia jasa (paket harga, estimasi pengerjaan, jumlah revisi, status ketersediaan).
- Menyediakan model pendapatan tambahan lewat fitur **Booster** (promosi berbayar/SaaS).

### 2. Target Users

| Role | Deskripsi |
|---|---|
| **Creator (Penyedia Jasa)** | Freelancer/individu kreatif yang membuka lapak jasa, mengelola portofolio, paket harga, dan pesanan. |
| **Customer (Pelanggan)** | Mahasiswa, UMKM, personal brand, komunitas, organisasi, event organizer yang mencari & memesan jasa kreatif. |

### 3. Core Features (MVP)

1. **Creative Shop** — Halaman toko/lapak milik creator: profil, portofolio, kategori jasa, paket & harga, estimasi pengerjaan, status ketersediaan (menerima/tidak menerima order).
2. **Booster** — Fitur berbayar untuk meningkatkan visibilitas/eksposur lapak atau jasa tertentu dalam periode waktu tertentu (sumber pendapatan platform / model SaaS).

### 4. Supporting Features

- Formulir **brief terstruktur** saat customer melakukan pemesanan (kebutuhan, referensi, format file, deadline, catatan tambahan).
- **Order tracking** / status pengerjaan (diterima → dikerjakan → revisi → selesai).
- **Rating & review** setelah order selesai.

### 5. Tech Stack (Rekomendasi Awal)

> Sesuaikan dengan kemampuan tim / requirement dosen.

- **Frontend:** React / Next.js (atau boleh diganti sesuai kebutuhan tugas)
- **Backend:** Node.js (Express/NestJS) atau Laravel — REST API
- **Database:** PostgreSQL atau MySQL
- **Auth:** JWT / session-based, role-based access (`customer`, `creator`, `admin`)
- **File storage:** untuk upload portofolio & lampiran brief (bisa lokal dulu untuk keperluan tugas, atau cloud storage bila deploy)
- **Payment (mock/sandbox):** untuk simulasi pembayaran Booster

### 6. Coding Conventions

- Gunakan struktur folder terpisah: `frontend/`, `backend/`, `docs/`.
- Penamaan tabel & entity dalam bahasa Inggris, konsisten (snake_case untuk DB, camelCase untuk kode JS).
- Setiap fitur besar (Creative Shop, Booster, Order, Review) dipisah per modul/service.
- Validasi input di sisi backend, jangan hanya mengandalkan validasi frontend.
- Setiap endpoint API didokumentasikan (bisa pakai Postman collection atau Swagger).

### 7. Development Priorities (Urutan Pengerjaan yang Disarankan)

1. Autentikasi & role (Customer / Creator)
2. Modul **Creative Shop**: profil creator, portofolio, kategori & paket jasa
3. Modul pencarian & tampilan store untuk customer
4. Modul **order & brief form**
5. Modul status pengerjaan & revisi
6. Modul **rating & review**
7. Modul **Booster** (SaaS/monetisasi)

### 8. Out of Scope (untuk versi MVP)

- Live chat real-time antara customer & creator (bisa pakai form/komentar dulu)
- Sistem pembayaran production-ready (cukup simulasi/sandbox)
- Multi-bahasa / multi-currency

### 9. Referensi

Dokumen ini disusun berdasarkan proposal "Ide Perancangan Sistem Web Sebagai Platform Jasa Kreatif Digital Berbasis Marketplace dan SaaS" (tugas mata kuliah Digital Entrepreneurship).
