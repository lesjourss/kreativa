import os
import sys

# Root project = satu level di atas folder "api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from app import app  # noqa: E402