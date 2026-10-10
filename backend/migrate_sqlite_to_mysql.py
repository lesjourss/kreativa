"""Migrasi satu-kali: salin seluruh isi SQLite (backend/app.db) ke MySQL (kreativa).
ID dipertahankan. Aman dijalankan ulang (INSERT IGNORE / REPLACE hanya bila kosong).
"""
import os
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as backend_app
from db import connect

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")

TABLES = [
    "users",
    "service_categories",
    "creator_profiles",
    "services",
    "service_packages",
    "portfolios",
    "orders",
    "revisions",
    "reviews",
    "booster_plans",
    "booster_purchases",
]

DATETIME_COLS = {"created_at", "updated_at", "start_date", "end_date"}


def to_mysql_dt(v):
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    s = str(v).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
        try:
            if "%z" in fmt:
                dt = datetime.strptime(s, fmt)
                dt = dt.replace(tzinfo=None)
            else:
                dt = datetime.strptime(s.split("+")[0].split("Z")[0], fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(f"Format tanggal tak dikenal: {v!r}")


def main():
    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite tidak ditemukan: {SQLITE_PATH} — lewati migrasi.")
        return
    backend_app.init_db()
    lite = sqlite3.connect(SQLITE_PATH)
    lite.row_factory = sqlite3.Row
    db = connect()
    try:
        for table in TABLES:
            rows = [dict(r) for r in lite.execute(f"SELECT * FROM {table}")]
            if not rows:
                print(f"{table}: kosong, lewati")
                continue
            cols = list(rows[0].keys())
            placeholders = ",".join(["%s"] * len(cols))
            sql = f"INSERT IGNORE INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
            data = []
            for r in rows:
                data.append(tuple(
                    to_mysql_dt(v) if (c in DATETIME_COLS) else v
                    for c, v in ((c, r[c]) for c in cols)
                ))
            cur = db.execute("SELECT 1")
            cur.executemany(sql, data)
            print(f"{table}: {len(data)} baris disalin (duplikat id dilewati)")
        db.commit()
    finally:
        db.close()
        lite.close()
    print("Migrasi selesai.")


if __name__ == "__main__":
    main()
