-- Schema awal Platform Jasa Kreatif Digital (SQLite)
-- Sesuai ARCHITECTURE.md §5

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('customer','creator','admin')),
  avatar_url TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS creator_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT DEFAULT '',
  avatar_url TEXT DEFAULT '',
  availability_status TEXT NOT NULL DEFAULT 'open' CHECK (availability_status IN ('open','closed')),
  avg_rating REAL NOT NULL DEFAULT 0,
  total_reviews INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS service_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS services (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category_id INTEGER REFERENCES service_categories(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  thumbnail_url TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS service_packages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  price INTEGER NOT NULL CHECK (price >= 0),
  estimated_days INTEGER NOT NULL DEFAULT 3 CHECK (estimated_days >= 1),
  revision_count INTEGER NOT NULL DEFAULT 1 CHECK (revision_count >= 0),
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS portfolios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  creator_id INTEGER NOT NULL REFERENCES users(id),
  service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
  service_package_id INTEGER REFERENCES service_packages(id) ON DELETE SET NULL,
  need_desc TEXT NOT NULL,
  reference_link TEXT DEFAULT '',
  output_format TEXT DEFAULT '',
  deadline TEXT DEFAULT '',
  note TEXT DEFAULT '',
  price_snapshot INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','diterima','dikerjakan','revisi','dikirim','selesai','ditolak','dibatalkan')),
  payment_proof_url TEXT DEFAULT '',
  payment_status TEXT NOT NULL DEFAULT 'unpaid'
    CHECK (payment_status IN ('unpaid','verifying','paid','rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS revisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  requested_by INTEGER NOT NULL REFERENCES users(id),
  note TEXT NOT NULL,
  file_url TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
  customer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  creator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS booster_plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  duration_days INTEGER NOT NULL,
  price INTEGER NOT NULL,
  description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS booster_purchases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  booster_plan_id INTEGER NOT NULL REFERENCES booster_plans(id),
  service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  payment_proof_url TEXT NOT NULL DEFAULT '',
  payment_status TEXT NOT NULL DEFAULT 'verifying' CHECK (payment_status IN ('unpaid','verifying','paid','rejected'))
);

CREATE TABLE IF NOT EXISTS deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  creator_id INTEGER NOT NULL REFERENCES users(id),
  note TEXT DEFAULT '',
  file_url TEXT DEFAULT '',
  link_url TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payment_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  qris_image_url TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
