# Kreativa — Platform Jasa Kreatif Digital (Marketplace + SaaS MVP)

## Menjalankan demo (Windows, XAMPP + Python 3.11)

1. Nyalakan MySQL di XAMPP (via `xampp-control.exe` → Start MySQL, atau `C:\xampp\mysql_start.bat`).
   Nyalakan juga Apache bila ingin buka phpMyAdmin.
2. Buat database (sekali saja): buka phpMyAdmin `http://localhost/phpmyadmin` → buat database
   `kreativa` (utf8mb4), atau via CLI:
   `C:\xampp\mysql\bin\mysql.exe -u root -e "CREATE DATABASE kreativa CHARACTER SET utf8mb4;"`
3. Install dependensi & siapkan data:
```powershell
python -m pip install -r backend/requirements.txt
python backend/seed.py
# Opsional, pindahan satu-kali dari SQLite lama (app.db) ke MySQL:
python backend/migrate_sqlite_to_mysql.py
```
4. Jalankan server:
```powershell
python backend/app.py
# buka http://127.0.0.1:5000
# database bisa dilihat di phpMyAdmin: http://localhost/phpmyadmin → database kreativa
```

Akun demo (password `password123`):
- Creator: `rina@creator.id`, `bimo@creator.id`
- Customer: `tania@customer.id`

## Struktur
- `frontend/` — HTML/CSS/JS vanilla (tanpa build step, sesuai UI_UX_BRIEF)
- `backend/` — Flask REST API + SQLite (`app.db`), validasi di backend
- `docs/API.md` — dokumentasi endpoint

## Alur end-to-end (Epic 8)
1. Customer buka `/` → cari/filter jasa → klik Lihat
2. Pilih paket → isi brief (`/order.html?package=`) → submit (status `pending`)
3. Creator login → `dashboard-creator.html` → Terima → Kerjakan → Selesai
4. Customer buka order → minta revisi (status `revisi`) atau beri rating setelah `selesai`
5. Creator aktifkan Booster (mock paid) → jasa naik ke atas listing + badge ⚡ Promoted
