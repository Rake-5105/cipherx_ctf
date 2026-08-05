"""
Vercel Serverless Function entry-point.
Everything is self-contained — no external templates or static files needed.
"""
from __future__ import annotations

import base64
import os
import shutil
import sqlite3
import tempfile
import traceback
from pathlib import Path

from flask import Flask, jsonify, request

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent          # project root

if os.access(BASE_DIR, os.W_OK):
    DB_PATH = BASE_DIR / "ctf_sqli.sqlite3"
else:
    DB_PATH = Path(tempfile.gettempdir()) / "ctf_sqli.sqlite3"

BACKUP_DB_PATH = BASE_DIR / "db_backup.sqlite"

# ---------------------------------------------------------------------------
# Flag
# ---------------------------------------------------------------------------
FLAG = "C1X{5angarn_0l1y1n_s3ya1}"
FLAG_HASH = base64.b64encode(FLAG.encode("utf-8")).decode("ascii")

FAKE_USERS = [
    ("alice",   "8f14e45fceea167a5a36dedd4bea2543", 0),
    ("bob",     "e99a18c428cb38d5f260853678922e03", 0),
    ("charlie", "098f6bcd4621d373cade4e832627b4f6", 0),
    ("diana",   "5f4dcc3b5aa765d61d8327deb882cf99", 0),
    ("eve",     "d8578edf8458ce06fbc5bb76a58c5ca4", 0),
    ("admin",   FLAG_HASH, 1),
]

# ---------------------------------------------------------------------------
# Flask app  (no template_folder / static_folder needed)
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config.update(DEBUG=False, TESTING=False, PROPAGATE_EXCEPTIONS=False)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def init_database() -> None:
    try:
        database_exists = DB_PATH.exists()
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

        if os.access(BASE_DIR, os.W_OK) and (not BACKUP_DB_PATH.exists() or not database_exists):
            shutil.copyfile(DB_PATH, BACKUP_DB_PATH)
    except Exception as e:
        print(f"Database initialization failed: {e}")
        traceback.print_exc()

init_database()

# ---------------------------------------------------------------------------
# Inline HTML  (eliminates all template / static-file issues on Vercel)
# ---------------------------------------------------------------------------
PAGE_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kuruttu Sathiyam - The Blind Truth</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Press+Start+2P&family=VT323&display=swap" rel="stylesheet">
  <style>
:root {
  --bg: #000000;
  --bg-soft: #0a0a0a;
  --panel: rgba(8, 8, 8, 0.9);
  --text: #ffffff;
  --muted: #8a8a8a;
  --dim: #5a5a5a;
  --accent: #ff5a1f;
  --accent-soft: #ff7a3d;
  --line: #1f1f1f;
  --border: #2a2a2a;
  --shadow: 0 0 0 transparent;
  --font-body: "JetBrains Mono", "Courier New", ui-monospace, monospace;
  --font-pixel: "Press Start 2P", "VT323", monospace;
  --font-crt: "VT323", "JetBrains Mono", ui-monospace, monospace;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; min-height: 100%; color: var(--text); background: var(--bg);
  font-family: var(--font-body); font-size: 14px; line-height: 1.6;
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
}
::selection { background: var(--accent); color: #000; }
body::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background: repeating-linear-gradient(to bottom, rgba(255,255,255,0.012) 0px,
    rgba(255,255,255,0.012) 1px, transparent 1px, transparent 3px);
}
.wrap { width: min(1600px, calc(100% - 16px)); margin: 0 auto; padding: 64px 0 48px; position: relative; z-index: 1; }
.hero { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 56px 0 80px; position: relative; }
.hero::after { content: ""; position: absolute; left: 50%; bottom: 32px; transform: translateX(-50%); width: 92%; max-width: 1080px; border-top: 1px dashed #1c1c1c; }
.dot-title { margin: 0; font-weight: 700; letter-spacing: 0.04em; line-height: 1; font-family: var(--font-pixel); font-size: clamp(48px, 8vw, 120px); white-space: nowrap; }
.subtitle { margin: 36px auto 0; max-width: 720px; color: var(--muted); font-size: 16px; line-height: 1.8; }
.features { padding: 48px 0 24px; }
.features-head { display: flex; align-items: center; gap: 18px; margin-bottom: 32px; }
.features-label { color: var(--accent); font-size: 13px; letter-spacing: 0.18em; font-weight: 700; white-space: nowrap; font-family: var(--font-pixel); }
.features-line { flex: 1; height: 1px; border-top: 1px dashed #1c1c1c; }
.features-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
.panel { position: relative; padding: 22px 20px; background: var(--panel); border: 1px solid var(--border); border-radius: 4px; }
.panel-icon { color: var(--accent); font-size: 22px; margin-bottom: 14px; line-height: 1; }
.panel h3 { margin: 0 0 10px; font-size: 13px; font-weight: 700; letter-spacing: 0.08em; color: var(--text); font-family: var(--font-pixel); line-height: 1.4; }
.panel p { margin: 0; font-size: 14.5px; line-height: 1.7; color: var(--muted); }
.panel code { font-family: var(--font-body); color: var(--accent-soft); font-size: 0.95em; }
.lookup-panel { margin-top: 8px; padding: 28px 28px 26px; }
.section-label { display: inline-flex; align-items: center; color: var(--accent); font-size: 13px; letter-spacing: 0.18em; margin-bottom: 16px; font-weight: 700; font-family: var(--font-pixel); }
.lookup-blurb { margin: 0 0 22px; color: var(--muted); font-size: 15px; line-height: 1.7; }
.lookup-blurb em { color: var(--accent); font-style: normal; }
.lookup-form { display: grid; grid-template-columns: auto minmax(0,1fr) auto; gap: 0; align-items: stretch; border: 1px solid var(--border); border-radius: 4px; background: #050505; overflow: hidden; padding: 4px; }
.prompt { padding: 0 14px; display: flex; align-items: center; color: var(--accent); font-size: 12px; background: #0a0a0a; border-right: 1px solid var(--border); font-family: var(--font-crt); letter-spacing: 0.04em; }
.lookup-form input { border: none; background: transparent; color: var(--text); padding: 18px 20px; outline: none; font-family: var(--font-body); font-size: 16px; min-width: 0; width: 100%; }
.lookup-form input::placeholder { color: var(--dim); }
.lookup-form input:focus { background: rgba(255,90,31,0.04); }
.lookup-form button { border: none; border-left: 1px solid var(--border); background: var(--accent); color: #000; font-family: var(--font-pixel); font-weight: 700; font-size: 9px; letter-spacing: 0.12em; padding: 10px 14px; cursor: pointer; transition: background 160ms ease; border-radius: 2px; align-self: center; }
.lookup-form button:hover { background: var(--accent-soft); }
.challenge-info { margin-top: 18px; padding: 14px 16px; border: 1px dashed var(--border); border-radius: 4px; color: var(--accent); font-family: var(--font-crt); font-size: 22px; letter-spacing: 0.04em; text-align: center; }
.result { margin-top: 22px; padding: 22px 26px; border-left: 4px solid var(--accent); background: rgba(255,90,31,0.06); color: var(--accent-soft); font-size: 32px; letter-spacing: 0.04em; font-family: var(--font-crt); text-align: center; font-weight: 700; }
.footer-note { margin-top: 56px; text-align: center; color: var(--dim); font-size: 14px; letter-spacing: 0.06em; }
.author-credit { position: fixed; right: 18px; bottom: 14px; color: #2a2a2a; font-family: var(--font-pixel); font-size: 9px; letter-spacing: 0.18em; opacity: 0.6; pointer-events: none; user-select: none; z-index: 2; }
@media (max-width: 980px) { .features-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .wrap { width: calc(100% - 32px); padding-top: 40px; } .hero { padding: 32px 0 56px; } .features-grid { grid-template-columns: 1fr; } .lookup-form { grid-template-columns: 1fr; } .prompt { border-right: none; border-bottom: 1px solid var(--border); padding: 10px 14px; } .lookup-form button { border-left: none; border-top: 1px solid var(--border); padding: 12px; } }
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <h1 class="dot-title dot-title-white">B1IND SQ1i</h1>
      <p class="subtitle">Challenge Your Mind. Break the Code.</p>
    </section>
    <section class="features" id="lookup">
      <div class="features-head">
        <span class="features-label">// CHALLENGE</span>
        <span class="features-line"></span>
      </div>
      <div class="features-grid">
        <article class="panel">
          <div class="panel-icon">&#9889;</div>
          <h3>BLIND SQLI</h3>
          <p>Extract data through boolean and timing oracles when no direct output is leaked.</p>
        </article>
        <article class="panel">
          <div class="panel-icon">&#8984;</div>
          <h3>SQLITE BACKEND</h3>
          <p>Lightweight file-based DB. Use <code>sqlite_master</code> and <code>pragma_table_info</code> to enumerate.</p>
        </article>
        <article class="panel">
          <div class="panel-icon">_</div>
          <h3>TIME-BASED ORACLE</h3>
          <p>No <code>SLEEP()</code> in SQLite &#8212; induce delay with <code>randomblob()</code> under a <code>CASE WHEN</code>.</p>
        </article>
        <article class="panel">
          <div class="panel-icon">&#9004;</div>
          <h3>BASE64 FLAG</h3>
          <p>Recover the admin row&#39;s <code>password_hash</code> character by character, then base64-decode the flag.</p>
        </article>
      </div>
      <article class="panel lookup-panel">
        <div class="section-label">// USER LOOKUP</div>
        <p class="lookup-blurb">
          Submit a username. The query is interpolated directly into SQLite.
          The page only reveals <em>found</em> or <em>not found</em>.
        </p>
        <form class="lookup-form" id="lookup-form" autocomplete="off">
          <span class="prompt">user@cipherx:~$</span>
          <input type="text" name="username" id="username-input"
                 placeholder="lookup --user=admin" aria-label="username" required />
          <button type="submit">EXECUTE</button>
        </form>
        <div class="result" id="lookup-result" style="display:none;"></div>
        <div class="challenge-info">&#2984;&#2985;&#3021;&#2993;&#3007; ! &#2997;&#2979;&#2965;&#3021;&#2965;&#2990;&#3021; !</div>
      </article>
      <div class="footer-note">&middot; Team CyberSec &middot;</div>
      <div class="author-credit">r4k3</div>
    </section>
  </main>
  <script>
    (function () {
      var form = document.getElementById('lookup-form');
      var input = document.getElementById('username-input');
      var resultEl = document.getElementById('lookup-result');
      if (!form) return;
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        var username = input.value;
        resultEl.textContent = '> querying...';
        resultEl.style.display = 'block';
        fetch('/lookup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'username=' + encodeURIComponent(username)
        })
        .then(function (r) { return r.json(); })
        .then(function (data) { resultEl.textContent = '> ' + data.result; })
        .catch(function () { resultEl.textContent = '> User not found'; });
      });
    })();
  </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_handler(_error):
    return "Not Found", 404

@app.errorhandler(500)
def internal_error_handler(_error):
    return "Internal Server Error", 500

@app.route("/", methods=["GET", "POST"])
def index():
    return PAGE_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

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
