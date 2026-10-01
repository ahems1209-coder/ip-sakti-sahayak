import sys
from pathlib import Path

# Make backend/ available for imports
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

handler = app
