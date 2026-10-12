-- Schema PostgreSQL (Supabase) — Platform Jasa Kreatif Digital
-- Jalankan di SQL Editor Supabase (Dashboard > SQL Editor > New query)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('customer','creator','admin')),
  avatar_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS creator_profiles (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  avatar_url VARCHAR(2000) NOT NULL DEFAULT '',
  availability_status VARCHAR(10) NOT NULL DEFAULT 'open' CHECK (availability_status IN ('open','closed')),
  avg_rating FLOAT NOT NULL DEFAULT 0,
  total_reviews INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS service_categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS services (
  id SERIAL PRIMARY KEY,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category_id INT REFERENCES service_categories(id) ON DELETE SET NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  thumbnail_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS service_packages (
  id SERIAL PRIMARY KEY,
  service_id INT NOT NULL REFERENCES services(id) ON DELETE CASCADE,
  name VARCHAR(120) NOT NULL,
  price INT NOT NULL CHECK (price >= 0),
  estimated_days INT NOT NULL DEFAULT 3 CHECK (estimated_days >= 1),
  revision_count INT NOT NULL DEFAULT 1 CHECK (revision_count >= 0),
  is_active SMALLINT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolios (
  id SERIAL PRIMARY KEY,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  image_url VARCHAR(2000) NOT NULL,
  title VARCHAR(200) NOT NULL DEFAULT '',
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  customer_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  creator_id INT NOT NULL REFERENCES users(id),
  service_id INT REFERENCES services(id) ON DELETE SET NULL,
  service_package_id INT REFERENCES service_packages(id) ON DELETE SET NULL,
  need_desc TEXT NOT NULL,
  reference_link VARCHAR(2000) NOT NULL DEFAULT '',
  output_format VARCHAR(200) NOT NULL DEFAULT '',
  deadline VARCHAR(32) NOT NULL DEFAULT '',
  note TEXT,
  price_snapshot INT NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','diterima','dikerjakan','revisi','dikirim','selesai','ditolak','dibatalkan')),
  payment_proof_url VARCHAR(2000) NOT NULL DEFAULT '',
  payment_status VARCHAR(20) NOT NULL DEFAULT 'unpaid'
    CHECK (payment_status IN ('unpaid','verifying','paid','rejected')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS revisions (
  id SERIAL PRIMARY KEY,
  order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  requested_by INT NOT NULL REFERENCES users(id),
  note TEXT NOT NULL,
  file_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
  id SERIAL PRIMARY KEY,
  order_id INT NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
  customer_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  service_id INT REFERENCES services(id) ON DELETE SET NULL,
  rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS booster_plans (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  duration_days INT NOT NULL,
  price INT NOT NULL,
  description VARCHAR(500) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS booster_purchases (
  id SERIAL PRIMARY KEY,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  booster_plan_id INT NOT NULL REFERENCES booster_plans(id),
  service_id INT REFERENCES services(id) ON DELETE CASCADE,
  start_date TIMESTAMPTZ NOT NULL,
  end_date TIMESTAMPTZ NOT NULL,
  payment_status VARCHAR(20) NOT NULL DEFAULT 'paid' CHECK (payment_status IN ('pending','paid','failed'))
);

CREATE TABLE IF NOT EXISTS deliveries (
  id SERIAL PRIMARY KEY,
  order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  creator_id INT NOT NULL REFERENCES users(id),
  note TEXT,
  file_url VARCHAR(2000) NOT NULL DEFAULT '',
  link_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_settings (
  id SERIAL PRIMARY KEY,
  qris_image_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscription_plans (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  price INT NOT NULL,
  max_portfolio INT NOT NULL,
  max_services INT NOT NULL,
  description VARCHAR(500) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id SERIAL PRIMARY KEY,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan_id INT NOT NULL REFERENCES subscription_plans(id),
  plan_type VARCHAR(120) NOT NULL DEFAULT '',
  start_date TIMESTAMPTZ NOT NULL,
  end_date TIMESTAMPTZ NOT NULL,
  payment_status VARCHAR(20) NOT NULL DEFAULT 'paid' CHECK (payment_status IN ('pending','paid','failed'))
);

-- Trigger untuk updated_at orders
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_orders_updated_at ON orders;
CREATE TRIGGER trg_orders_updated_at
BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();