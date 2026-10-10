# UI_UX_BRIEF.md

## UI/UX Brief — Platform Jasa Kreatif Digital

### 1. Brand Feel / Mood

Platform ini menyasar kalangan kreatif digital (desainer, ilustrator, videografer, dll), jadi tampilan sebaiknya:
- **Modern, bersih, dan sedikit playful** — mencerminkan industri kreatif, bukan platform korporat kaku.
- **Portofolio-first** — visual karya (gambar/video) jadi elemen utama, bukan teks panjang.
- **Terpercaya & terstruktur** — meski playful, informasi harga/paket/status harus jelas dan mudah dibaca (menjawab masalah "harga tidak terstruktur" di PRD).

### 2. Warna & Tipografi (Saran Awal)

- **Warna utama:** 1 warna aksen berani (mis. ungu/indigo atau oranye) + netral (putih/abu gelap) untuk background, agar portofolio (gambar/video) tetap jadi fokus.
- **Tipografi:** sans-serif modern (Inter, Poppins, atau Manrope) — mudah dibaca di layar, terasa "digital-native".
- Gunakan skema warna berbeda tipis untuk membedakan role (opsional): dashboard Creator vs tampilan publik Customer.

### 3. Halaman Utama (Core Screens)

Berdasarkan flow di `ARCHITECTURE.md`, berikut layar-layar utama yang perlu didesain:

#### A. Untuk Customer
1. **Landing Page / Homepage** — hero section, kategori jasa unggulan, creator/booster yang sedang di-highlight.
2. **Halaman Pencarian/Listing Jasa** — filter kategori, search bar, kartu jasa (thumbnail, nama creator, harga mulai dari, rating, status ketersediaan).
3. **Halaman Store/Profil Creator** — bio, portofolio (grid galeri), daftar paket jasa (harga, estimasi, revisi), badge status (Open/Closed for order).
4. **Halaman Detail Paket & Form Order (Brief)** — detail paket + form brief terstruktur (kebutuhan, referensi, format file, deadline, catatan).
5. **Halaman Status Order** — timeline status (Pending → Diterima → Dikerjakan → Revisi → Selesai), tombol request revisi.
6. **Halaman Rating & Review** — form bintang + komentar setelah order selesai.

#### B. Untuk Creator
1. **Dashboard Creator** — ringkasan order masuk dan status booster aktif.
2. **Halaman Kelola Profil & Portofolio** — upload/edit karya, edit bio.
3. **Halaman Kelola Jasa & Paket** — CRUD kategori jasa, nama paket, harga, estimasi, revisi; toggle status ketersediaan.
4. **Halaman Kelola Order Masuk** — list order, terima/tolak, update status pengerjaan, upload hasil revisi.
5. **Halaman Booster** — pilih paket booster, simulasi pembayaran, lihat masa aktif booster.

### 4. Komponen UI Kunci

| Komponen | Catatan Desain |
|---|---|
| Kartu Jasa (Service Card) | Thumbnail besar, nama creator, kategori, harga mulai dari, badge status (Open/Closed) |
| Badge Status Ketersediaan | Warna hijau = menerima order, abu/merah = tidak menerima |
| Timeline Status Order | Stepper horizontal/vertikal, jelas menunjukkan tahap saat ini |
| Form Brief | Multi-field terstruktur (bukan textarea kosong) — kebutuhan, referensi (upload/link), format output, deadline, catatan |
| Galeri Portofolio | Grid responsif, bisa preview besar saat diklik |
| Badge Booster | Label kecil "Promoted"/"Diboost" pada kartu jasa yang sedang di-boost, agar transparan ke customer |

### 5. Prinsip UX

- **Kurangi friksi order**: form brief harus terasa cepat diisi meski terstruktur (gunakan step-by-step jika field banyak).
- **Transparansi harga & waktu**: harga, estimasi pengerjaan, dan jumlah revisi harus terlihat *sebelum* customer klik order — ini inti solusi dari masalah utama di PRD.
- **Kejelasan status**: baik customer maupun creator harus selalu tahu "sekarang di tahap apa" tanpa perlu chat manual.
- **Responsive-first**: banyak customer (mahasiswa/UMKM) kemungkinan akses lewat HP — prioritaskan tampilan mobile untuk listing jasa & status order.

### 6. Referensi Visual (Inspirasi, bukan untuk ditiru identik)

Untuk gambaran mood, bisa cek platform sejenis seperti Fiverr, Sribulancer, atau Project.co — khususnya dari sisi tata letak kartu jasa dan halaman profil freelancer, lalu disesuaikan dengan identitas kampus/tugas kamu sendiri.

### 7. Referensi

Disusun berdasarkan proposal "Ide Perancangan Sistem Web Sebagai Platform Jasa Kreatif Digital Berbasis Marketplace dan SaaS" dan alur sistem pada `ARCHITECTURE.md`.
