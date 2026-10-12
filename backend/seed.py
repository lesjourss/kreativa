"""Seed data dummy untuk demo (Epic 8). Database PostgreSQL (Supabase) / MySQL (XAMPP)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash

import app as backend_app
from db import connect

backend_app.init_db()
db = connect()


def get_user(email):
    return db.execute("SELECT * FROM users WHERE email=%s", (email,)).fetchone()


def ensure_user(name, email, role, password="password123"):
    u = get_user(email)
    if u:
        return u["id"]
    # PostgreSQL: RETURNING id untuk dapatkan id
    cur = db.execute(
        "INSERT INTO users (name,email,password_hash,role) VALUES (%s,%s,%s,%s) RETURNING id",
        (name, email, generate_password_hash(password), role),
    )
    uid = cur.fetchone()["id"]
    if role == "creator":
        # PostgreSQL: ON CONFLICT DO NOTHING
        db.execute(
            "INSERT INTO creator_profiles (user_id, bio, availability_status) VALUES (%s, %s, 'open') ON CONFLICT (user_id) DO NOTHING",
            (uid, f"Halo! Saya {name}, freelancer kreatif."),
        )
    db.commit()
    return uid


def cat_id(name):
    r = db.execute("SELECT id FROM service_categories WHERE name=%s", (name,)).fetchone()
    return r["id"] if r else None


def ensure_service(creator_id, title, cat, desc, thumb, packages):
    r = db.execute("SELECT id FROM services WHERE creator_id=%s AND title=%s", (creator_id, title)).fetchone()
    if r:
        sid = r["id"]
    else:
        cur = db.execute(
            "INSERT INTO services (creator_id, category_id, title, description, thumbnail_url) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (creator_id, cat_id(cat), title, desc, thumb),
        )
        sid = cur.fetchone()["id"]
    for name, price, days, rev in packages:
        if not db.execute("SELECT id FROM service_packages WHERE service_id=%s AND name=%s", (sid, name)).fetchone():
            db.execute(
                "INSERT INTO service_packages (service_id, name, price, estimated_days, revision_count) VALUES (%s,%s,%s,%s,%s)",
                (sid, name, price, days, rev),
            )
    db.commit()
    return sid


# users demo
admin_user = ensure_user("Admin Kreativa", "admin@kreativa.id", "admin", "admin123")
c1 = ensure_user("Rina Desain", "rina@creator.id", "creator")
c2 = ensure_user("Bimo Visual", "bimo@creator.id", "creator")
cust = ensure_user("Tania UMKM", "tania@customer.id", "customer")

db.execute("UPDATE creator_profiles SET bio=%s, avatar_url=%s WHERE user_id=%s",
           ("Desainer grafis & ilustrator. Spesialis logo, poster, dan kemasan UMKM.",
            "https://i.pravatar.cc/150?img=47", c1))
db.execute("UPDATE creator_profiles SET bio=%s, avatar_url=%s WHERE user_id=%s",
           ("Videografer & video editor. Reels, TikTok, dan dokumentasi event.",
            "https://i.pravatar.cc/150?img=12", c2))

s1 = ensure_service(c1, "Logo Premium untuk UMKM", "Desain Grafis",
                    "Logo profesional + brand guideline mini. 3 konsep awal, file AI/PNG/SVG.",
                    "https://picsum.photos/seed/logo1/600/400",
                    [("Basic", 150000, 3, 1), ("Bisnis", 350000, 5, 3), ("Premium", 750000, 7, 5)])
s2 = ensure_service(c1, "Ilustrasi Chibi & Character", "Ilustrasi & Fan Art",
                    "Character design, chibi, fanart untuk merchandise & sosmed.",
                    "https://picsum.photos/seed/chibi/600/400",
                    [("1 Karakter", 120000, 3, 2), ("2 Karakter", 220000, 5, 3)])
s3 = ensure_service(c2, "Video Editing Reels/TikTok", "Video Editing",
                    "Editing reels/TikTok + caption + color grading. Revisi cepat.",
                    "https://picsum.photos/seed/reels/600/400",
                    [("1 Video", 100000, 2, 1), ("Paket 5 Video", 400000, 7, 2)])
s4 = ensure_service(c2, "Foto Produk UMKM", "Fotografi",
                    "Foto produk katalog + styling sederhana. 10 foto edited.",
                    "https://picsum.photos/seed/foto/600/400",
                    [("10 Foto", 250000, 4, 2)])

for sid, title in [(s1, "Logo coffeeshop"), (s1, "Kemasan snack"), (s3, "Reels fashion")]:
    owner = c1 if sid in (s1, s2) else c2
    if not db.execute("SELECT id FROM portfolios WHERE creator_id=%s AND title=%s", (owner, title)).fetchone():
        db.execute(
            "INSERT INTO portfolios (creator_id, image_url, title, description) VALUES (%s,%s,%s,%s)",
            (owner, f"https://picsum.photos/seed/{title.replace(' ', '')}/600/400", title, "Contoh hasil kerja.")
        )

# order + review contoh
pkg = db.execute("SELECT id, price FROM service_packages WHERE service_id=%s ORDER BY price LIMIT 1", (s1,)).fetchone()
if not db.execute("SELECT id FROM orders WHERE customer_id=%s AND service_package_id=%s", (cust, pkg["id"])).fetchone():
    cur = db.execute(
        """INSERT INTO orders (customer_id, creator_id, service_id, service_package_id, need_desc,
                               reference_link, output_format, deadline, note, price_snapshot, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'selesai') RETURNING id""",
        (cust, c1, s1, pkg["id"], "Butuh logo coffeeshop modern warna earth tone.",
         "https://pinterest.com/contoh", "AI + PNG", "2026-10-10", "Butuh cepat untuk launching.", pkg["price"]),
    )
    oid = cur.fetchone()["id"]
    db.execute(
        "INSERT INTO reviews (order_id, customer_id, creator_id, service_id, rating, comment) VALUES (%s,%s,%s,%s,%s,%s)",
        (oid, cust, c1, s1, 5, "Hasil cepat dan rapi! Sangat recommended."),
    )
    agg = db.execute("SELECT AVG(rating) AS a, COUNT(*) AS c FROM reviews WHERE creator_id=%s", (c1,)).fetchone()
    avg_r = float(agg["a"]) if agg["a"] is not None else 0
    db.execute("UPDATE creator_profiles SET avg_rating=%s, total_reviews=%s WHERE user_id=%s", (round(avg_r, 2), agg["c"], c1))

db.commit()
db.close()
print("Seed OK: rina@creator.id / bimo@creator.id / tania@customer.id (password: password123)")