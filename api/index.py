import sys
from pathlib import Path

# Add backend directory to sys.path so app module can be imported
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

# Entrypoint for Vercel Serverless Function
handler = app
