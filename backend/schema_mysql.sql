-- Skema MySQL/MariaDB — Platform Jasa Kreatif Digital (isi ARCHITECTURE.md §5)
-- Dipakai via XAMPP (phpMyAdmin). Database `kreativa`, charset utf8mb4.
-- Catatan: kolom TEXT tidak diberi DEFAULT (MariaDB tidak mengizinkan),
-- nilai default diisi eksplisit dari kode aplikasi.

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('customer','creator','admin')),
  avatar_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS creator_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  bio TEXT NULL,
  avatar_url VARCHAR(2000) NOT NULL DEFAULT '',
  availability_status VARCHAR(10) NOT NULL DEFAULT 'open' CHECK (availability_status IN ('open','closed')),
  avg_rating FLOAT NOT NULL DEFAULT 0,
  total_reviews INT NOT NULL DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS service_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  creator_id INT NOT NULL,
  category_id INT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT NULL,
  thumbnail_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (category_id) REFERENCES service_categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS service_packages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  service_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  price INT NOT NULL CHECK (price >= 0),
  estimated_days INT NOT NULL DEFAULT 3 CHECK (estimated_days >= 1),
  revision_count INT NOT NULL DEFAULT 1 CHECK (revision_count >= 0),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS portfolios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  creator_id INT NOT NULL,
  image_url VARCHAR(2000) NOT NULL,
  title VARCHAR(200) NOT NULL DEFAULT '',
  description TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  creator_id INT NOT NULL,
  service_id INT NULL,
  service_package_id INT NULL,
  need_desc TEXT NOT NULL,
  reference_link VARCHAR(2000) NOT NULL DEFAULT '',
  output_format VARCHAR(200) NOT NULL DEFAULT '',
  deadline VARCHAR(32) NOT NULL DEFAULT '',
  note TEXT NULL,
  price_snapshot INT NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','diterima','dikerjakan','revisi','dikirim','selesai','ditolak','dibatalkan')),
  payment_proof_url VARCHAR(2000) NOT NULL DEFAULT '',
  payment_status VARCHAR(20) NOT NULL DEFAULT 'unpaid'
    CHECK (payment_status IN ('unpaid','verifying','paid','rejected')),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users(id),
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL,
  FOREIGN KEY (service_package_id) REFERENCES service_packages(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS revisions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  requested_by INT NOT NULL,
  note TEXT NOT NULL,
  file_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (requested_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL UNIQUE,
  customer_id INT NOT NULL,
  creator_id INT NOT NULL,
  service_id INT NULL,
  rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS booster_plans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  duration_days INT NOT NULL,
  price INT NOT NULL,
  description VARCHAR(500) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS booster_purchases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  creator_id INT NOT NULL,
  booster_plan_id INT NOT NULL,
  service_id INT NULL,
  start_date DATETIME NOT NULL,
  end_date DATETIME NOT NULL,
  payment_status VARCHAR(20) NOT NULL DEFAULT 'paid' CHECK (payment_status IN ('pending','paid','failed')),
  FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (booster_plan_id) REFERENCES booster_plans(id),
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS deliveries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  creator_id INT NOT NULL,
  note TEXT NULL,
  file_url VARCHAR(2000) NOT NULL DEFAULT '',
  link_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS payment_settings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  qris_image_url VARCHAR(2000) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
