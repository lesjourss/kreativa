"""Backend Flask — Platform Jasa Kreatif Digital (Marketplace + SaaS MVP).
Covers TASKS.md Epic 1-7. Database MySQL/MariaDB via XAMPP (lihat backend/db.py).
Validasi di backend.
"""
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

from db import connect as mysql_connect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-ganti-di-production")
JWT_EXP_HOURS = int(os.environ.get("JWT_EXP_HOURS", "72"))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

# Upload file lokal (sesuai AGENTS.md: storage boleh lokal untuk tugas)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ALLOWED_IMG_EXT = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = Flask(__name__)

VALID_ORDER_STATUS = ["pending", "diterima", "dikerjakan", "revisi", "selesai", "ditolak", "dibatalkan"]
# Transisi yang diizinkan (creator-driven, customer bisa minta revisi/batalkan)
ALLOWED_TRANSITIONS = {
    "pending": ["diterima", "ditolak", "dibatalkan"],
    "diterima": ["dikerjakan", "ditolak", "dibatalkan"],
    "dikerjakan": ["revisi", "selesai"],
    "revisi": ["dikerjakan", "selesai"],
    "selesai": [],
    "ditolak": [],
    "dibatalkan": [],
}


# ---------- DB helpers ----------
def get_db():
    if "db" not in g:
        g.db = mysql_connect()
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    # Supabase: schema dijalankan manual di SQL Editor (schema_supabase.sql).
    # Di sini cukup seed data master (kategori, booster plans).
    db = mysql_connect()
    try:
        # seed kategori + paket booster bila kosong
        if db.execute("SELECT COUNT(*) AS c FROM service_categories").fetchone()["c"] == 0:
            cats = ["Desain Grafis", "Ilustrasi & Fan Art", "Fotografi", "Videografi",
                    "Video Editing", "UI/UX Design", "Motion Graphic & Animasi",
                    "3D Design", "Audio & Musik", "Copywriting", "Social Media Creative"]
            db.executemany("INSERT INTO service_categories (name) VALUES (%s)", [(c,) for c in cats])
        if db.execute("SELECT COUNT(*) AS c FROM booster_plans").fetchone()["c"] == 0:
            db.executemany(
                "INSERT INTO booster_plans (name, duration_days, price, description) VALUES (%s,%s,%s,%s)",
                [("Booster 3 Hari", 3, 15000, "Naikkan visibilitas 1 jasa selama 3 hari"),
                 ("Booster 7 Hari", 7, 29000, "Naikkan visibilitas 1 jasa selama 7 hari"),
                 ("Booster 30 Hari", 30, 99000, "Eksposur maksimal 1 jasa selama 30 hari")],
            )
        db.commit()
    finally:
        db.close()


def _ser(v):
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return v


def row_to_dict(row):
    if row is None:
        return None
    return {k: _ser(v) for k, v in dict(row).items()}


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------- Auth helpers ----------
def make_token(user):
    payload = {
        "sub": str(user["id"]),
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXP_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Token tidak ditemukan"}), 401
        token = header.split(" ", 1)[1]
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token kedaluwarsa, login ulang"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token tidak valid"}), 401
        db = get_db()
        try:
            uid = int(data["sub"])
        except (TypeError, ValueError):
            return jsonify({"error": "Token tidak valid"}), 401
        user = db.execute("SELECT id, name, email, role, avatar_url FROM users WHERE id = %s", (uid,)).fetchone()
        if user is None:
            return jsonify({"error": "User tidak ditemukan"}), 401
        g.user = row_to_dict(user)
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if g.user["role"] not in roles and g.user["role"] != "admin":
                return jsonify({"error": "Akses ditolak untuk role ini"}), 403
            return f(*args, **kwargs)
        return wrapper
    return deco


def active_booster_service_ids(db):
    """Return set service_id yang sedang di-boost (mock payment paid + rentang tanggal aktif)."""
    rows = db.execute(
        """SELECT service_id FROM booster_purchases
           WHERE payment_status='paid' AND service_id IS NOT NULL
           AND NOW() BETWEEN start_date AND end_date"""
    ).fetchall()
    return {r["service_id"] for r in rows}


def active_booster_creator_ids(db):
    rows = db.execute(
        """SELECT creator_id FROM booster_purchases
           WHERE payment_status='paid'
           AND NOW() BETWEEN start_date AND end_date"""
    ).fetchall()
    return {r["creator_id"] for r in rows}


# ---------- Epic 1: Auth ----------
@app.post("/api/auth/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "customer").strip()
    if len(name) < 2:
        return jsonify({"error": "Nama minimal 2 karakter"}), 400
    if "@" not in email or "." not in email:
        return jsonify({"error": "Email tidak valid"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password minimal 6 karakter"}), 400
    if role not in ("customer", "creator"):
        return jsonify({"error": "Role harus customer atau creator"}), 400
    db = get_db()
    if db.execute("SELECT id FROM users WHERE email=%s", (email,)).fetchone():
        return jsonify({"error": "Email sudah terdaftar"}), 400
    pw_hash = generate_password_hash(password)
    cur = db.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s,%s,%s,%s)",
        (name, email, pw_hash, role),
    )
    user_id = cur.lastrowid
    if role == "creator":
        db.execute("INSERT INTO creator_profiles (user_id, bio) VALUES (%s, '')", (user_id,))
    db.commit()
    user = {"id": user_id, "role": role}
    return jsonify({"token": make_token(user), "user": {"id": user_id, "name": name, "email": email, "role": role}}), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email=%s", (email,)).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Email atau password salah"}), 401
    user = row_to_dict(row)
    return jsonify({
        "token": make_token(user),
        "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"], "avatar_url": user.get("avatar_url") or ""},
    })


@app.get("/api/me")
@auth_required
def me():
    return jsonify({"user": g.user})


@app.patch("/api/me")
@auth_required
def update_me():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    avatar_url = (data.get("avatar_url") or "").strip()
    if name and len(name) < 2:
        return jsonify({"error": "Nama minimal 2 karakter"}), 400
    db = get_db()
    if name:
        db.execute("UPDATE users SET name=%s WHERE id=%s", (name, g.user["id"]))
    if "avatar_url" in data:
        if len(avatar_url) > 2000:
            return jsonify({"error": "URL avatar terlalu panjang"}), 400
        db.execute("UPDATE users SET avatar_url=%s WHERE id=%s", (avatar_url, g.user["id"]))
    db.commit()
    return jsonify({"ok": True})


# ---------- Kategori ----------
@app.get("/api/categories")
def list_categories():
    db = get_db()
    rows = db.execute("SELECT id, name FROM service_categories ORDER BY name").fetchall()
    return jsonify([row_to_dict(r) for r in rows])


# ---------- Epic 2+3: Services / listing ----------
@app.get("/api/services")
def list_services():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "boosted").strip()
    db = get_db()
    boosted_ids = active_booster_service_ids(db)
    boosted_creators = active_booster_creator_ids(db)

    q = """SELECT s.id, s.title, s.description, s.thumbnail_url, s.created_at,
                  s.creator_id, u.name AS creator_name,
                  c.name AS category_name, c.id AS category_id,
                  cp.avg_rating, cp.availability_status,
                  (SELECT MIN(price) FROM service_packages WHERE service_id=s.id AND is_active=1) AS price_from
           FROM services s
           JOIN users u ON u.id = s.creator_id
           LEFT JOIN service_categories c ON c.id = s.category_id
           LEFT JOIN creator_profiles cp ON cp.user_id = s.creator_id
           WHERE 1=1"""
    params = []
    if category:
        q += " AND (c.name = %s OR CAST(c.id AS CHAR) = %s)"
        params += [category, category]
    if search:
        q += " AND (s.title LIKE %s OR s.description LIKE %s OR u.name LIKE %s)"
        like = f"%{search}%"
        params += [like, like, like]
    rows = db.execute(q, params).fetchall()
    out = []
    for r in rows:
        d = row_to_dict(r)
        d["is_boosted"] = (d["id"] in boosted_ids) or (d["creator_id"] in boosted_creators)
        out.append(d)
    if sort == "rating":
        out.sort(key=lambda x: (-(x.get("avg_rating") or 0), x["id"]))
    elif sort == "newest":
        out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    elif sort == "price_low":
        out.sort(key=lambda x: (x.get("price_from") is None, x.get("price_from") or 0))
    else:  # boosted first, then newest
        out.sort(key=lambda x: (not x["is_boosted"], x.get("created_at") or ""), reverse=False)
        # fix: boosted True harus di depan
        out.sort(key=lambda x: (0 if x["is_boosted"] else 1, x.get("created_at") or ""))
        out = sorted(out, key=lambda x: (0 if x["is_boosted"] else 1,))
    return jsonify(out)


@app.post("/api/services")
@auth_required
@role_required("creator")
def create_service():
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    category_id = data.get("category_id")
    thumbnail_url = (data.get("thumbnail_url") or "").strip()
    if len(title) < 4:
        return jsonify({"error": "Judul jasa minimal 4 karakter"}), 400
    if len(description) < 10:
        return jsonify({"error": "Deskripsi minimal 10 karakter"}), 400
    db = get_db()
    if category_id is not None:
        cat = db.execute("SELECT id FROM service_categories WHERE id=%s", (category_id,)).fetchone()
        if cat is None:
            return jsonify({"error": "Kategori tidak ditemukan"}), 400
    # creator closed tetap boleh tambah jasa, tapi tidak bisa diorder (dicek saat order)
    cur = db.execute(
        "INSERT INTO services (creator_id, category_id, title, description, thumbnail_url) VALUES (%s,%s,%s,%s,%s)",
        (g.user["id"], category_id, title, description, thumbnail_url),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid}), 201


@app.get("/api/services/<int:sid>")
def service_detail(sid):
    db = get_db()
    s = db.execute(
        """SELECT s.*, u.name AS creator_name, c.name AS category_name,
                  cp.bio, cp.avatar_url, cp.avg_rating, cp.total_reviews, cp.availability_status
           FROM services s JOIN users u ON u.id=s.creator_id
           LEFT JOIN service_categories c ON c.id=s.category_id
           LEFT JOIN creator_profiles cp ON cp.user_id=s.creator_id
           WHERE s.id=%s""",
        (sid,),
    ).fetchone()
    if s is None:
        return jsonify({"error": "Jasa tidak ditemukan"}), 404
    d = row_to_dict(s)
    pkgs = db.execute("SELECT * FROM service_packages WHERE service_id=%s ORDER BY price", (sid,)).fetchall()
    d["packages"] = [row_to_dict(p) for p in pkgs]
    d["is_boosted"] = sid in active_booster_service_ids(db)
    revs = db.execute(
        """SELECT r.*, u.name AS customer_name FROM reviews r
           JOIN users u ON u.id=r.customer_id WHERE r.service_id=%s ORDER BY r.created_at DESC LIMIT 20""",
        (sid,),
    ).fetchall()
    d["reviews"] = [row_to_dict(r) for r in revs]
    return jsonify(d)


@app.patch("/api/services/<int:sid>")
@auth_required
@role_required("creator")
def update_service(sid):
    db = get_db()
    s = db.execute("SELECT * FROM services WHERE id=%s", (sid,)).fetchone()
    if s is None:
        return jsonify({"error": "Jasa tidak ditemukan"}), 404
    if s["creator_id"] != g.user["id"] and g.user["role"] != "admin":
        return jsonify({"error": "Bukan jasa milikmu"}), 403
    data = request.get_json(force=True, silent=True) or {}
    fields, params = [], []
    for key in ("title", "description", "thumbnail_url"):
        if key in data and isinstance(data[key], str):
            fields.append(f"{key}=%s")
            params.append(data[key].strip())
    if "category_id" in data:
        if data["category_id"] is None:
            fields.append("category_id=NULL")
        else:
            cat = db.execute("SELECT id FROM service_categories WHERE id=%s", (data["category_id"],)).fetchone()
            if cat is None:
                return jsonify({"error": "Kategori tidak ditemukan"}), 400
            fields.append("category_id=%s")
            params.append(data["category_id"])
    if not fields:
        return jsonify({"error": "Tidak ada field yang diupdate"}), 400
    params.append(sid)
    db.execute(f"UPDATE services SET {', '.join(fields)} WHERE id=%s", params)
    db.commit()
    return jsonify({"ok": True})


@app.delete("/api/services/<int:sid>")
@auth_required
@role_required("creator")
def delete_service(sid):
    db = get_db()
    s = db.execute("SELECT * FROM services WHERE id=%s", (sid,)).fetchone()
    if s is None:
        return jsonify({"error": "Jasa tidak ditemukan"}), 404
    if s["creator_id"] != g.user["id"] and g.user["role"] != "admin":
        return jsonify({"error": "Bukan jasa milikmu"}), 403
    db.execute("DELETE FROM services WHERE id=%s", (sid,))
    db.commit()
    return jsonify({"ok": True})


# ---------- Paket jasa ----------
@app.post("/api/services/<int:sid>/packages")
@auth_required
@role_required("creator")
def create_package(sid):
    db = get_db()
    s = db.execute("SELECT * FROM services WHERE id=%s", (sid,)).fetchone()
    if s is None:
        return jsonify({"error": "Jasa tidak ditemukan"}), 404
    if s["creator_id"] != g.user["id"] and g.user["role"] != "admin":
        return jsonify({"error": "Bukan jasa milikmu"}), 403
    data = request.get_json(force=True, silent=True) or {}
    name = (str(data.get("name") or "")).strip()
    try:
        price = int(data.get("price", -1))
        estimated_days = int(data.get("estimated_days", 3))
        revision_count = int(data.get("revision_count", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "price/estimated_days/revision_count harus angka"}), 400
    if len(name) < 2:
        return jsonify({"error": "Nama paket minimal 2 karakter"}), 400
    if price < 0:
        return jsonify({"error": "Harga tidak boleh negatif"}), 400
    if estimated_days < 1:
        return jsonify({"error": "Estimasi minimal 1 hari"}), 400
    if revision_count < 0:
        return jsonify({"error": "Jumlah revisi tidak boleh negatif"}), 400
    cur = db.execute(
        "INSERT INTO service_packages (service_id, name, price, estimated_days, revision_count) VALUES (%s,%s,%s,%s,%s)",
        (sid, name, price, estimated_days, revision_count),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid}), 201


@app.patch("/api/packages/<int:pid>")
@auth_required
@role_required("creator")
def update_package(pid):
    db = get_db()
    p = db.execute(
        "SELECT sp.*, s.creator_id FROM service_packages sp JOIN services s ON s.id=sp.service_id WHERE sp.id=%s",
        (pid,),
    ).fetchone()
    if p is None:
        return jsonify({"error": "Paket tidak ditemukan"}), 404
    if p["creator_id"] != g.user["id"] and g.user["role"] != "admin":
        return jsonify({"error": "Bukan paket milikmu"}), 403
    data = request.get_json(force=True, silent=True) or {}
    fields, params = [], []
    if "name" in data:
        if len(str(data["name"]).strip()) < 2:
            return jsonify({"error": "Nama paket minimal 2 karakter"}), 400
        fields.append("name=%s")
        params.append(str(data["name"]).strip())
    for key in ("price", "estimated_days", "revision_count"):
        if key in data:
            try:
                v = int(data[key])
            except (TypeError, ValueError):
                return jsonify({"error": f"{key} harus angka"}), 400
            if key == "price" and v < 0:
                return jsonify({"error": "Harga tidak boleh negatif"}), 400
            if key == "estimated_days" and v < 1:
                return jsonify({"error": "Estimasi minimal 1 hari"}), 400
            if key == "revision_count" and v < 0:
                return jsonify({"error": "Revisi tidak boleh negatif"}), 400
            fields.append(f"{key}=%s")
            params.append(v)
    if "is_active" in data:
        fields.append("is_active=%s")
        params.append(1 if data["is_active"] else 0)
    if not fields:
        return jsonify({"error": "Tidak ada field yang diupdate"}), 400
    params.append(pid)
    db.execute(f"UPDATE service_packages SET {', '.join(fields)} WHERE id=%s", params)
    db.commit()
    return jsonify({"ok": True})


@app.delete("/api/packages/<int:pid>")
@auth_required
@role_required("creator")
def delete_package(pid):
    db = get_db()
    p = db.execute(
        "SELECT sp.*, s.creator_id FROM service_packages sp JOIN services s ON s.id=sp.service_id WHERE sp.id=%s",
        (pid,),
    ).fetchone()
    if p is None:
        return jsonify({"error": "Paket tidak ditemukan"}), 404
    if p["creator_id"] != g.user["id"] and g.user["role"] != "admin":
        return jsonify({"error": "Bukan paket milikmu"}), 403
    db.execute("DELETE FROM service_packages WHERE id=%s", (pid,))
    db.commit()
    return jsonify({"ok": True})


# ---------- Epic 2: Creator store & portfolio ----------
@app.get("/api/creators/<int:cid>/store")
def creator_store(cid):
    db = get_db()
    user = db.execute("SELECT id, name, avatar_url FROM users WHERE id=%s AND role='creator'", (cid,)).fetchone()
    if user is None:
        return jsonify({"error": "Creator tidak ditemukan"}), 404
    prof = db.execute("SELECT * FROM creator_profiles WHERE user_id=%s", (cid,)).fetchone()
    services = db.execute(
        """SELECT s.*, c.name AS category_name,
                  (SELECT MIN(price) FROM service_packages WHERE service_id=s.id AND is_active=1) AS price_from
           FROM services s LEFT JOIN service_categories c ON c.id=s.category_id
           WHERE s.creator_id=%s ORDER BY s.created_at DESC""",
        (cid,),
    ).fetchall()
    portfolios = db.execute("SELECT * FROM portfolios WHERE creator_id=%s ORDER BY created_at DESC", (cid,)).fetchall()
    reviews = db.execute(
        """SELECT r.*, u.name AS customer_name FROM reviews r
           JOIN users u ON u.id=r.customer_id WHERE r.creator_id=%s ORDER BY r.created_at DESC LIMIT 20""",
        (cid,),
    ).fetchall()
    boosted = active_booster_service_ids(db)
    svc_list = []
    for s in services:
        d = row_to_dict(s)
        pkgs = db.execute("SELECT * FROM service_packages WHERE service_id=%s AND is_active=1 ORDER BY price", (s["id"],)).fetchall()
        d["packages"] = [row_to_dict(p) for p in pkgs]
        d["is_boosted"] = s["id"] in boosted
        svc_list.append(d)
    return jsonify({
        "creator": row_to_dict(user),
        "profile": row_to_dict(prof),
        "services": svc_list,
        "portfolios": [row_to_dict(p) for p in portfolios],
        "reviews": [row_to_dict(r) for r in reviews],
    })


@app.get("/api/creator/profile")
@auth_required
@role_required("creator")
def my_creator_profile():
    db = get_db()
    prof = db.execute("SELECT * FROM creator_profiles WHERE user_id=%s", (g.user["id"],)).fetchone()
    orders_pending = db.execute("SELECT COUNT(*) AS c FROM orders WHERE creator_id=%s AND status='pending'", (g.user["id"],)).fetchone()["c"]
    booster_active = db.execute(
        """SELECT COUNT(*) AS c FROM booster_purchases WHERE creator_id=%s AND payment_status='paid'
           AND NOW() BETWEEN start_date AND end_date""",
        (g.user["id"],),
    ).fetchone()["c"]
    return jsonify({"profile": row_to_dict(prof),
                    "orders_pending": orders_pending, "booster_active": booster_active})


@app.patch("/api/creator/profile")
@auth_required
@role_required("creator")
def update_creator_profile():
    data = request.get_json(force=True, silent=True) or {}
    bio = (data.get("bio") or "").strip() if "bio" in data else None
    avatar_url = (data.get("avatar_url") or "").strip() if "avatar_url" in data else None
    if bio is not None and len(bio) > 2000:
        return jsonify({"error": "Bio maksimal 2000 karakter"}), 400
    db = get_db()
    if bio is not None:
        db.execute("UPDATE creator_profiles SET bio=%s WHERE user_id=%s", (bio, g.user["id"]))
    if avatar_url is not None:
        if len(avatar_url) > 2000:
            return jsonify({"error": "URL avatar terlalu panjang"}), 400
        db.execute("UPDATE creator_profiles SET avatar_url=%s WHERE user_id=%s", (avatar_url, g.user["id"]))
        db.execute("UPDATE users SET avatar_url=%s WHERE id=%s", (avatar_url, g.user["id"]))
    db.commit()
    return jsonify({"ok": True})


@app.patch("/api/creator/availability")
@auth_required
@role_required("creator")
def set_availability():
    data = request.get_json(force=True, silent=True) or {}
    status = (data.get("availability_status") or "").strip()
    if status not in ("open", "closed"):
        return jsonify({"error": "Status harus open atau closed"}), 400
    db = get_db()
    db.execute("UPDATE creator_profiles SET availability_status=%s WHERE user_id=%s", (status, g.user["id"]))
    db.commit()
    return jsonify({"ok": True, "availability_status": status})


@app.get("/api/portfolios")
def list_portfolios():
    creator_id = request.args.get("creator_id", "").strip()
    db = get_db()
    if creator_id:
        rows = db.execute("SELECT * FROM portfolios WHERE creator_id=%s ORDER BY created_at DESC", (creator_id,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM portfolios ORDER BY created_at DESC LIMIT 60").fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.post("/api/portfolios")
@auth_required
@role_required("creator")
def create_portfolio():
    data = request.get_json(force=True, silent=True) or {}
    image_url = (data.get("image_url") or "").strip()
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    if not image_url:
        return jsonify({"error": "image_url wajib diisi (URL atau path file)"}), 400
    if len(image_url) > 2000:
        return jsonify({"error": "URL gambar terlalu panjang"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO portfolios (creator_id, image_url, title, description) VALUES (%s,%s,%s,%s)",
        (g.user["id"], image_url, title, description),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid}), 201


@app.delete("/api/portfolios/<int:pid>")
@auth_required
@role_required("creator")
def delete_portfolio(pid):
    db = get_db()
    p = db.execute("SELECT * FROM portfolios WHERE id=%s", (pid,)).fetchone()
    if p is None:
        return jsonify({"error": "Portofolio tidak ditemukan"}), 404
    if p["creator_id"] != g.user["id"] and g.user["role"] != "admin":
        return jsonify({"error": "Bukan portofolio milikmu"}), 403
    db.execute("DELETE FROM portfolios WHERE id=%s", (pid,))
    db.commit()
    return jsonify({"ok": True})


# ---------- Epic 4: Orders ----------
@app.post("/api/orders")
@auth_required
@role_required("customer")
def create_order():
    data = request.get_json(force=True, silent=True) or {}
    try:
        package_id = int(data.get("service_package_id", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "service_package_id tidak valid"}), 400
    need_desc = (data.get("need_desc") or data.get("brief_text") or "").strip()
    reference_link = (data.get("reference_link") or "").strip()
    output_format = (data.get("output_format") or data.get("format") or "").strip()
    deadline = (data.get("deadline") or "").strip()
    note = (data.get("note") or data.get("catatan") or "").strip()
    if len(need_desc) < 10:
        return jsonify({"error": "Deskripsi kebutuhan minimal 10 karakter"}), 400
    if deadline:
        try:
            datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        except ValueError:
            # izinkan format YYYY-MM-DD
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Format deadline tidak valid (pakai YYYY-MM-DD)"}), 400
    db = get_db()
    pkg = db.execute(
        """SELECT sp.*, s.creator_id, s.id AS service_id FROM service_packages sp
           JOIN services s ON s.id=sp.service_id WHERE sp.id=%s""",
        (package_id,),
    ).fetchone()
    if pkg is None or not pkg["is_active"]:
        return jsonify({"error": "Paket jasa tidak ditemukan / tidak aktif"}), 404
    avail = db.execute("SELECT availability_status FROM creator_profiles WHERE user_id=%s", (pkg["creator_id"],)).fetchone()
    if avail and avail["availability_status"] == "closed":
        return jsonify({"error": "Creator sedang tidak menerima order (Closed)"}), 400
    cur = db.execute(
        """INSERT INTO orders (customer_id, creator_id, service_id, service_package_id, need_desc,
                               reference_link, output_format, deadline, note, price_snapshot, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'pending')""",
        (g.user["id"], pkg["creator_id"], pkg["service_id"], package_id, need_desc,
         reference_link, output_format, deadline, note, pkg["price"]),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "status": "pending"}), 201


@app.get("/api/orders")
@auth_required
def list_orders():
    db = get_db()
    if g.user["role"] == "creator":
        rows = db.execute(
            """SELECT o.*, u.name AS customer_name, s.title AS service_title, sp.name AS package_name
               FROM orders o JOIN users u ON u.id=o.customer_id
               LEFT JOIN services s ON s.id=o.service_id
               LEFT JOIN service_packages sp ON sp.id=o.service_package_id
               WHERE o.creator_id=%s ORDER BY o.created_at DESC""",
            (g.user["id"],),
        ).fetchall()
    elif g.user["role"] == "admin":
        rows = db.execute(
            """SELECT o.*, u.name AS customer_name FROM orders o
               JOIN users u ON u.id=o.customer_id ORDER BY o.created_at DESC LIMIT 200"""
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT o.*, u.name AS creator_name, s.title AS service_title, sp.name AS package_name
               FROM orders o JOIN users u ON u.id=o.creator_id
               LEFT JOIN services s ON s.id=o.service_id
               LEFT JOIN service_packages sp ON sp.id=o.service_package_id
               WHERE o.customer_id=%s ORDER BY o.created_at DESC""",
            (g.user["id"],),
        ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.get("/api/orders/<int:oid>")
@auth_required
def order_detail(oid):
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    if g.user["role"] != "admin" and g.user["id"] not in (o["customer_id"], o["creator_id"]):
        return jsonify({"error": "Bukan order milikmu"}), 403
    d = row_to_dict(o)
    revs = db.execute("SELECT * FROM revisions WHERE order_id=%s ORDER BY created_at", (oid,)).fetchall()
    d["revisions"] = [row_to_dict(r) for r in revs]
    rev = db.execute("SELECT * FROM reviews WHERE order_id=%s", (oid,)).fetchone()
    d["review"] = row_to_dict(rev)
    return jsonify(d)


@app.patch("/api/orders/<int:oid>/status")
@auth_required
def update_order_status(oid):
    data = request.get_json(force=True, silent=True) or {}
    new_status = (data.get("status") or "").strip()
    if new_status not in VALID_ORDER_STATUS:
        return jsonify({"error": f"Status tidak valid. Pilihan: {', '.join(VALID_ORDER_STATUS)}"}), 400
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    is_creator = g.user["id"] == o["creator_id"] or g.user["role"] == "admin"
    is_customer = g.user["id"] == o["customer_id"]
    if not (is_creator or is_customer):
        return jsonify({"error": "Bukan order milikmu"}), 403
    cur_status = o["status"]
    if new_status not in ALLOWED_TRANSITIONS.get(cur_status, []):
        return jsonify({"error": f"Tidak bisa pindah dari {cur_status} ke {new_status}"}), 400
    # Aturan peran:
    if is_customer and not is_creator:
        # customer hanya boleh batalkan saat pending/diterima, atau minta revisi (via endpoint revisi)
        if new_status not in ("dibatalkan",):
            return jsonify({"error": "Customer hanya bisa membatalkan order. Minta revisi lewat tombol Revisi."}), 403
    if is_creator and new_status == "dibatalkan":
        return jsonify({"error": "Creator tidak bisa membatalkan; gunakan status ditolak"}), 400
    db.execute("UPDATE orders SET status=%s, updated_at=%s WHERE id=%s", (new_status, now_str(), oid))
    db.commit()
    return jsonify({"ok": True, "status": new_status})


@app.post("/api/orders/<int:oid>/revisions")
@auth_required
def add_revision(oid):
    data = request.get_json(force=True, silent=True) or {}
    note = (data.get("note") or "").strip()
    file_url = (data.get("file_url") or "").strip()
    if len(note) < 3:
        return jsonify({"error": "Catatan revisi minimal 3 karakter"}), 400
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    if g.user["id"] not in (o["customer_id"], o["creator_id"]) and g.user["role"] != "admin":
        return jsonify({"error": "Bukan order milikmu"}), 403
    if o["status"] in ("selesai", "ditolak", "dibatalkan"):
        return jsonify({"error": "Order sudah final, tidak bisa revisi"}), 400
    # batasi jumlah revisi customer sesuai paket? cek jumlah revisi oleh customer
    if g.user["id"] == o["customer_id"]:
        pkg = db.execute("SELECT revision_count FROM service_packages WHERE id=%s", (o["service_package_id"],)).fetchone()
        used = db.execute("SELECT COUNT(*) AS c FROM revisions WHERE order_id=%s AND requested_by=%s",
                          (oid, o["customer_id"])).fetchone()["c"]
        if pkg and used >= (pkg["revision_count"] or 0):
            return jsonify({"error": f"Kuota revisi paket habis ({pkg['revision_count']}x)"}), 400
    cur = db.execute(
        "INSERT INTO revisions (order_id, requested_by, note, file_url) VALUES (%s,%s,%s,%s)",
        (oid, g.user["id"], note, file_url),
    )
    # setiap ada revisi, status jadi 'revisi' (kecuali masih pending)
    if o["status"] in ("diterima", "dikerjakan", "revisi"):
        db.execute("UPDATE orders SET status='revisi', updated_at=%s WHERE id=%s", (now_str(), oid))
    db.commit()
    return jsonify({"id": cur.lastrowid, "status": "revisi"}), 201


@app.get("/api/orders/<int:oid>/revisions")
@auth_required
def list_revisions(oid):
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    if g.user["id"] not in (o["customer_id"], o["creator_id"]) and g.user["role"] != "admin":
        return jsonify({"error": "Bukan order milikmu"}), 403
    rows = db.execute("SELECT * FROM revisions WHERE order_id=%s ORDER BY created_at", (oid,)).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


# ---------- Epic 5: Rating & Review ----------
@app.post("/api/orders/<int:oid>/review")
@auth_required
@role_required("customer")
def add_review(oid):
    data = request.get_json(force=True, silent=True) or {}
    try:
        rating = int(data.get("rating", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Rating harus angka 1-5"}), 400
    comment = (data.get("comment") or "").strip()
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating harus 1-5"}), 400
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    if o["customer_id"] != g.user["id"]:
        return jsonify({"error": "Hanya pemesan yang bisa memberi review"}), 403
    if o["status"] != "selesai":
        return jsonify({"error": "Review hanya bisa diberikan setelah order selesai"}), 400
    if db.execute("SELECT id FROM reviews WHERE order_id=%s", (oid,)).fetchone():
        return jsonify({"error": "Order ini sudah direview"}), 400
    cur = db.execute(
        "INSERT INTO reviews (order_id, customer_id, creator_id, service_id, rating, comment) VALUES (%s,%s,%s,%s,%s,%s)",
        (oid, g.user["id"], o["creator_id"], o["service_id"], rating, comment),
    )
    # update agregat creator
    agg = db.execute("SELECT AVG(rating) AS avg_r, COUNT(*) AS c FROM reviews WHERE creator_id=%s", (o["creator_id"],)).fetchone()
    avg_r = float(agg["avg_r"]) if agg["avg_r"] is not None else 0
    db.execute("UPDATE creator_profiles SET avg_rating=%s, total_reviews=%s WHERE user_id=%s",
               (round(avg_r, 2), agg["c"], o["creator_id"]))
    db.commit()
    return jsonify({"id": cur.lastrowid}), 201


@app.get("/api/creators/<int:cid>/reviews")
def creator_reviews(cid):
    db = get_db()
    rows = db.execute(
        """SELECT r.*, u.name AS customer_name FROM reviews r
           JOIN users u ON u.id=r.customer_id WHERE r.creator_id=%s ORDER BY r.created_at DESC""",
        (cid,),
    ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


# ---------- Epic 6: Booster ----------
@app.get("/api/booster/plans")
def booster_plans():
    db = get_db()
    rows = db.execute("SELECT * FROM booster_plans ORDER BY price").fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.post("/api/booster/purchase")
@auth_required
@role_required("creator")
def booster_purchase():
    data = request.get_json(force=True, silent=True) or {}
    try:
        plan_id = int(data.get("booster_plan_id", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "booster_plan_id tidak valid"}), 400
    service_id = data.get("service_id")
    if service_id is not None:
        try:
            service_id = int(service_id)
        except (TypeError, ValueError):
            return jsonify({"error": "service_id tidak valid"}), 400
    db = get_db()
    plan = db.execute("SELECT * FROM booster_plans WHERE id=%s", (plan_id,)).fetchone()
    if plan is None:
        return jsonify({"error": "Paket booster tidak ditemukan"}), 404
    if service_id is not None:
        s = db.execute("SELECT * FROM services WHERE id=%s", (service_id,)).fetchone()
        if s is None:
            return jsonify({"error": "Jasa tidak ditemukan"}), 404
        if s["creator_id"] != g.user["id"] and g.user["role"] != "admin":
            return jsonify({"error": "Bukan jasa milikmu"}), 403
    # simulasi pembayaran: selalu sukses (mock/sandbox untuk MVP)
    start = datetime.now()
    end = start + timedelta(days=int(plan["duration_days"]))
    start_s, end_s = start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")
    cur = db.execute(
        """INSERT INTO booster_purchases (creator_id, booster_plan_id, service_id, start_date, end_date, payment_status)
           VALUES (%s,%s,%s,%s,%s,'paid')""",
        (g.user["id"], plan_id, service_id, start_s, end_s),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "payment": "mock-paid",
                    "start_date": start.isoformat(), "end_date": end.isoformat()}), 201


@app.get("/api/booster/active")
def booster_active():
    db = get_db()
    rows = db.execute(
        """SELECT bp.*, pl.name AS plan_name, s.title AS service_title FROM booster_purchases bp
           JOIN booster_plans pl ON pl.id=bp.booster_plan_id
           LEFT JOIN services s ON s.id=bp.service_id
           WHERE bp.payment_status='paid' AND NOW() BETWEEN bp.start_date AND bp.end_date
           ORDER BY bp.end_date DESC"""
    ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.get("/api/booster/mine")
@auth_required
@role_required("creator")
def booster_mine():
    db = get_db()
    rows = db.execute(
        """SELECT bp.*, pl.name AS plan_name FROM booster_purchases bp
           JOIN booster_plans pl ON pl.id=bp.booster_plan_id
           WHERE bp.creator_id=%s ORDER BY bp.end_date DESC""",
        (g.user["id"],),
    ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


# ---------- Upload gambar (Epic 2: thumbnail jasa, portofolio, avatar) ----------
@app.post("/api/upload")
@auth_required
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file (pakai field 'file')"}), 400
    f = request.files["file"]
    if not f.filename or "." not in f.filename:
        return jsonify({"error": "Nama file tidak valid"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_IMG_EXT:
        return jsonify({"error": "Format harus jpg, jpeg, png, webp, atau gif"}), 400
    data = f.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        return jsonify({"error": "File kosong"}), 400
    if len(data) > MAX_UPLOAD_BYTES:
        return jsonify({"error": "Ukuran maksimal 5MB"}), 400
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    fname = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(UPLOAD_DIR, fname), "wb") as out:
        out.write(data)
    return jsonify({"url": f"/uploads/{fname}"}), 201


@app.get("/uploads/<path:fname>")
def serve_upload(fname):
    return send_from_directory(UPLOAD_DIR, fname)


# ---------- Serve frontend (static) ----------
@app.get("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def serve_static(filename):
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    full = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(full):
        return send_from_directory(FRONTEND_DIR, filename)
    # SPA fallback untuk halaman .html tanpa ekstensi? kembalikan index
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
