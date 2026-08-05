import sys
from pathlib import Path

# Add project root to path so we can import app.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app
