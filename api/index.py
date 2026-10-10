import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app  # noqa: E402  (Vercel mencari variabel `app` di file ini)

# Catatan: init_db() TIDAK dijalankan di sini. Buat tabel di database cloud
# dengan menjalankan seed dari laptop: DB_HOST=... DB_USER=... python backend/seed.py
