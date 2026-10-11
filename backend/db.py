"""Koneksi database PostgreSQL (Supabase) — drop-in replacement untuk db.py.

Konfigurasi lewat environment:
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME (dari Settings > Database Supabase)
- DB_SSL_MODE = require (default Supabase)
"""
import os
import ssl
import tempfile

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_SSL_MODE = os.environ.get("DB_SSL_MODE", "require")

_pool: SimpleConnectionPool | None = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            1, 5,
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASSWORD,
            dbname=DB_NAME,
            sslmode=DB_SSL_MODE,
        )
    return _pool


class _PGWrapper:
    """Wrapper agar API mirip pymysql: conn.execute(sql, params) -> cursor."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        # psycopg2 pakai %s, bukan ? — konversi otomatis
        if params is not None:
            cur.execute(sql.replace("?", "%s"), params)
        else:
            cur.execute(sql)
        return cur

    def executemany(self, sql, seq):
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.executemany(sql.replace("?", "%s"), seq)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        _get_pool().putconn(self._conn)


def connect():
    pool = _get_pool()
    conn = pool.getconn()
    conn.autocommit = False
    return _PGWrapper(conn)