"""Koneksi database MySQL/MariaDB (XAMPP lokal atau cloud seperti Aiven).

Konfigurasi lewat environment (lihat .env.example):
- Lokal XAMPP: DB_HOST=127.0.0.1, DB_USER=root, DB_PASSWORD=(kosong)
- Cloud (Aiven, wajib SSL): set DB_SSL_CA ke path file ca.pem ATAU isi
  sertifikatnya langsung (untuk env Vercel, dengan \n sebagai newline).
"""
import os
import ssl
import tempfile

import pymysql
from pymysql.cursors import DictCursor

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "kreativa")
DB_SSL_CA = os.environ.get("DB_SSL_CA", "")


class _DB:
    """Wrapper tipis agar pemakaian mirip sqlite3: db.execute() -> cursor."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cur = self._conn.cursor()
        cur.execute(sql, params or ())
        return cur

    def executemany(self, sql, seq):
        cur = self._conn.cursor()
        cur.executemany(sql, seq)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def _ssl_args():
    if not DB_SSL_CA:
        return {}
    if os.path.isfile(DB_SSL_CA):
        cafile = DB_SSL_CA
    else:
        # Isi PEM langsung (env Vercel): tulis ke file sementara
        fd, cafile = tempfile.mkstemp(suffix="-db-ca.pem")
        with os.fdopen(fd, "w") as f:
            f.write(DB_SSL_CA.replace("\\n", "\n"))
    ctx = ssl.create_default_context(cafile=cafile)
    return {"ssl": ctx}


def connect():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        **_ssl_args(),
    )
    return _DB(conn)
