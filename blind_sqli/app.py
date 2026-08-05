from __future__ import annotations

import base64
import shutil
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import os

import tempfile
import traceback

BASE_DIR = Path(__file__).resolve().parent

# Check if the deployment directory is writable (Vercel is read-only)
if os.access(BASE_DIR, os.W_OK):
    DB_PATH = BASE_DIR / "ctf_sqli.sqlite3"
else:
    DB_PATH = Path(tempfile.gettempdir()) / "ctf_sqli.sqlite3"

BACKUP_DB_PATH = BASE_DIR / "db_backup.sqlite"

FLAG = "C1X{5angarn_0l1y1n_s3ya1}"
FLAG_HASH = base64.b64encode(FLAG.encode("utf-8")).decode("ascii")

FAKE_USERS = [
    ("alice", "8f14e45fceea167a5a36dedd4bea2543", 0),
    ("bob", "e99a18c428cb38d5f260853678922e03", 0),
    ("charlie", "098f6bcd4621d373cade4e832627b4f6", 0),
    ("diana", "5f4dcc3b5aa765d61d8327deb882cf99", 0),
    ("eve", "d8578edf8458ce06fbc5bb76a58c5ca4", 0),
    ("admin", FLAG_HASH, 1),
]

app = Flask(__name__)
app.config.update(
    DEBUG=False,
    TESTING=False,
    PROPAGATE_EXCEPTIONS=False,
    TEMPLATES_AUTO_RELOAD=False,
)

def init_database() -> None:
    """Create the SQLite database and seed rows if needed."""
    try:
        database_exists = DB_PATH.exists()

        # If we are using a temp dir, try to restore from bundled backup first
        if not os.access(BASE_DIR, os.W_OK) and not database_exists and BACKUP_DB_PATH.exists():
            shutil.copyfile(BACKUP_DB_PATH, DB_PATH)
            database_exists = True

        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_admin INTEGER NOT NULL DEFAULT 0
                )
            """)

            count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if count == 0:
                connection.executemany(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                    FAKE_USERS,
                )
                connection.commit()

        # Save a backup locally if the directory is writable
        if os.access(BASE_DIR, os.W_OK) and (not BACKUP_DB_PATH.exists() or not database_exists):
            shutil.copyfile(DB_PATH, BACKUP_DB_PATH)
    except Exception as e:
        print(f"Database initialization failed: {e}")
        traceback.print_exc()

init_database()


@app.errorhandler(404)
def not_found_handler(_error):
    return render_template("index.html", result="User not found"), 404


@app.errorhandler(500)
def internal_error_handler(_error):
    return render_template("index.html", result="User not found"), 500


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/lookup", methods=["POST"])
def lookup():
    username = request.form.get("username", "")
    raw_sql = f"SELECT id, username, password_hash, is_admin FROM users WHERE username = '{username}' LIMIT 1"

    try:
        with sqlite3.connect(DB_PATH) as connection:
            row = connection.execute(raw_sql).fetchone()
        result = "User found" if row else "User not found"
    except Exception:
        result = "User not found"

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
