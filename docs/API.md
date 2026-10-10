# API Docs — Kreativa MVP

Base URL: `http://127.0.0.1:5000/api`

Database: MySQL/MariaDB via XAMPP, database `kreativa` (lihat di phpMyAdmin
`http://localhost/phpmyadmin`). Skema: `backend/schema_mysql.sql`, koneksi:
`backend/db.py` (env `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`).

Auth: header `Authorization: Bearer <JWT>` kecuali endpoint publik.

## Auth (Epic 1)
- `POST /auth/register` {name, email, password, role: customer|creator}
- `POST /auth/login` {email, password} → {token, user}
- `GET /me` (auth)
- `PATCH /me` {name?, avatar_url?}

## Kategori & Listing (Epic 2-3)
- `GET /categories`
- `GET /services?category=&search=&sort=boosted|newest|rating|price_low` (publik, boosted dulu)
- `GET /services/:id` (detail + packages + reviews)
- `POST /services` (creator) {title≥4, description≥10, category_id?, thumbnail_url?}
- `PATCH /services/:id`, `DELETE /services/:id` (owner)
- `POST /services/:id/packages` {name, price≥0, estimated_days≥1, revision_count≥0}
- `PATCH /packages/:id`, `DELETE /packages/:id`

## Creative Shop (Epic 2)
- `GET /creators/:id/store` (publik)
- `GET /creator/profile` (creator: profil + ringkasan order & booster)
- `PATCH /creator/profile` {bio?, avatar_url?}
- `PATCH /creator/availability` {availability_status: open|closed}
- `GET /portfolios?creator_id=`
- `POST /portfolios` {image_url*, title?, description?}
- `DELETE /portfolios/:id`

## Upload gambar (Epic 2)
- `POST /api/upload` (auth, multipart field `file`: jpg/jpeg/png/webp/gif, maks 5MB,
  tersimpan lokal di `backend/uploads/`) → `{url: "/uploads/....jpg"}`
- `GET /uploads/<nama-file>` (publik)
- Dipakai untuk thumbnail jasa, portofolio, dan avatar (bisa juga tetap pakai URL)

## Order (Epic 4)
- `POST /orders` (customer) {service_package_id*, need_desc≥10, reference_link?, output_format?, deadline YYYY-MM-DD?, note?} → 400 bila creator Closed
- `GET /orders` (mine: customer→punya dia, creator→order masuk)
- `GET /orders/:id` (+revisions +review)
- `PATCH /orders/:id/status` {status} — transisi `pending→diterima→dikerjakan→revisi→selesai`, customer hanya boleh `dibatalkan` (revisi via endpoint revisi)
- `POST /orders/:id/revisions` {note*, file_url?} (kuota revisi paket dicek untuk customer)
- `GET /orders/:id/revisions`

## Review (Epic 5)
- `POST /orders/:id/review` (customer, hanya setelah selesai, 1x) {rating 1-5, comment?}
- `GET /creators/:id/reviews`

## Booster (Epic 6, mock paid)
- `GET /booster/plans`
- `POST /booster/purchase` (creator) {booster_plan_id*, service_id?} → selalu `paid`
- `GET /booster/active` (publik)
- `GET /booster/mine` (creator)
