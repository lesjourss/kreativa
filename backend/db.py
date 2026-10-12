"""Koneksi PostgreSQL (Supabase) untuk backend Flask.

Konfigurasi lewat environment (Vercel > Settings > Environment Variables):
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
  (pakai Session pooler dari tombol Connect di Supabase;
   DB_USER bentuknya postgres.<project-ref>)
- DB_SSL_MODE = require (default)
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_SSL_MODE = os.environ.get("DB_SSL_MODE", "require")

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        # Pool kecil: tiap instance serverless punya pool sendiri
        _pool = SimpleConnectionPool(
            1, 3,
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASSWORD,
            dbname=DB_NAME, sslmode=DB_SSL_MODE,
        )
    return _pool


class _Cursor:
    """Membungkus cursor agar punya .lastrowid seperti pymysql."""

    def __init__(self, cur, lastrowid=None):
        self._cur = cur
        self.lastrowid = lastrowid

    def __getattr__(self, name):
        return getattr(self._cur, name)


class _PGWrapper:
    """API mirip pymysql: db.execute(sql, params) -> cursor."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        # INSERT otomatis diberi RETURNING id supaya .lastrowid tersedia
        is_insert = (
            sql.lstrip()[:6].upper() == "INSERT"
            and "RETURNING" not in sql.upper()
        )
        if is_insert:
            sql = sql.rstrip().rstrip(";") + " RETURNING id"
        cur.execute(sql, params)
        lastrowid = None
        if is_insert:
            row = cur.fetchone()
            lastrowid = row["id"] if row else None
        return _Cursor(cur, lastrowid)

    def executemany(self, sql, seq):
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.executemany(sql, seq)
        return _Cursor(cur)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            # Bersihkan transaksi menggantung sebelum koneksi kembali ke pool
            self._conn.rollback()
        finally:
            _get_pool().putconn(self._conn)


def connect():
    conn = _get_pool().getconn()
    conn.autocommit = False
    return _PGWrapper(conn)