# PRD.md

## Product Requirements Document — Platform Jasa Kreatif Digital

### 1. Latar Belakang

Kebutuhan jasa kreatif digital (desain grafis, ilustrasi, fotografi, video editing, UI/UX, motion graphic, 3D, audio, copywriting, konten sosmed) terus meningkat, mendorong makin banyak freelancer menawarkan jasa secara mandiri. Namun proses pemasaran & pemesanan masih tersebar di berbagai platform sosial (Instagram, TikTok, X, WhatsApp, Discord), sehingga informasi portofolio, harga, dan komunikasi sulit diakses dalam satu tempat, dan proses bisnis penyedia jasa jadi kurang terstruktur.

### 2. Tujuan Produk

Membangun platform web berbasis **marketplace + SaaS** yang:
- Memberi wadah bagi penyedia jasa kreatif untuk memajang portofolio & mengelola pesanan secara terstruktur.
- Memudahkan pelanggan mencari dan memesan jasa kreatif dari satu platform.
- Menghasilkan pendapatan platform lewat fitur monetisasi (Booster).

### 3. Target Pengguna

**A. Penyedia Jasa Kreatif (Creator)** — freelancer/individu dengan keahlian di bidang:

| Kategori | Contoh Jasa |
|---|---|
| Desain Grafis | Logo, poster, banner, kemasan |
| Ilustrasi & Fan Art | Fanart, chibi, character design |
| Fotografi | Foto produk, portrait, event |
| Videografi | Dokumentasi, video produk, event |
| Video Editing | Reels, TikTok, YouTube |
| UI/UX Design | UI website, aplikasi, prototype |
| Motion Graphic & Animasi | Motion graphic, intro, animasi 2D |
| 3D Design | 3D modeling, rendering, asset 3D |
| Audio & Musik | Mixing, mastering, sound design |
| Copywriting | Artikel, caption, script, deskripsi produk |
| Social Media Creative | Konten media sosial & template |

**B. Pelanggan (Customer)** — mahasiswa, UMKM, personal brand, komunitas, organisasi, event organizer.

### 4. Problem Statement

| # | Masalah |
|---|---|
| 1 | Informasi jasa (portofolio) & pemesanan dikelola mandiri di berbagai platform sosial. |
| 2 | Harga & paket jasa tidak terstruktur, pelanggan harus tanya langsung ke creator. |
| 3 | Pelanggan sulit tahu apakah creator sedang menerima pesanan. |
| 4 | Creator harus promosi mandiri agar jasa/portofolio ditemukan. |

### 5. Solusi Produk

| # | Solusi | Fitur Terkait |
|---|---|---|
| 1 | Halaman profil & portofolio dalam satu tempat | Creative Shop |
| 2 | Paket & harga jasa terstruktur (harga, estimasi, revisi) | Creative Shop |
| 3 | Status ketersediaan jasa (menerima/tidak menerima order) | Creative Shop |
| 4 | Formulir brief terstruktur saat pemesanan | Order Management |
| 5 | Fitur promosi berbayar untuk naikkan visibilitas | Booster (SaaS) |

### 6. MVP Scope

**Fitur Utama (Wajib ada di MVP):**
1. **Creative Shop** — profil, portofolio, kategori jasa, paket & harga, estimasi pengerjaan, status ketersediaan.
2. **Booster** — promosi berbayar untuk meningkatkan eksposur lapak/jasa dalam periode tertentu.

**Fitur Pendukung MVP:**
- Autentikasi & role (Customer, Creator)
- Pencarian & listing jasa/store
- Form brief pemesanan
- Status pengerjaan order (diterima → dikerjakan → revisi → selesai)
- Rating & review

**Di luar scope MVP (Future/Nice-to-have):**
- Live chat real-time
- Payment gateway production-ready (cukup simulasi/sandbox untuk tugas)
- Multi-bahasa / multi-currency
- Rekomendasi otomatis (AI matching creator-customer)

### 7. User Stories

| Sebagai | Saya ingin | Agar |
|---|---|---|
| Creator | membuat profil & upload portofolio | calon pelanggan bisa melihat keahlian saya |
| Creator | membuat paket jasa dengan harga & estimasi | pelanggan tahu biaya & waktu pengerjaan sebelum order |
| Creator | mengatur status ketersediaan | pelanggan tidak order saat saya sedang penuh |
| Creator | membeli booster | jasa saya lebih mudah ditemukan |
| Customer | mencari jasa berdasarkan kategori | menemukan creator yang sesuai kebutuhan |
| Customer | mengisi form brief saat order | kebutuhan saya tersampaikan dengan jelas & rapi |
| Customer | memantau status pesanan | tahu progres pengerjaan jasa saya |
| Customer | memberi rating & review | membantu creator lain menilai kredibilitas creator |

### 8. Success Metrics (Contoh untuk Tugas/Demo)

- Jumlah creator yang berhasil membuat store & minimal 1 paket jasa
- Jumlah order berhasil dibuat end-to-end (order → selesai)
- Jumlah review yang masuk
- Jumlah booster yang aktif terpasang (simulasi transaksi)

### 9. Model Monetisasi

- **Booster** — pembayaran sekali per periode promosi (per jasa/lapak)

### 10. Referensi

Disusun berdasarkan proposal "Ide Perancangan Sistem Web Sebagai Platform Jasa Kreatif Digital Berbasis Marketplace dan SaaS" (tugas mata kuliah Digital Entrepreneurship).
