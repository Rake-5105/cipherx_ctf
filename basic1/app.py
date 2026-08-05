import os
from pathlib import Path
from flask import Flask, Response, render_template, send_from_directory, abort


BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "backup"

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/robots.txt")
def robots():
    robots_path = BASE_DIR / "robots.txt"
    return Response(robots_path.read_text(encoding="utf-8"), mimetype="text/plain")


@app.get("/admin/")
def admin():
    return Response("<h1>403 Forbidden</h1>", status=403, mimetype="text/html")


@app.get("/secret-login.php")
def secret_login():
    return Response(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Admin Login</title>
          <style>
            body { font-family: Arial, sans-serif; max-width: 420px; margin: 80px auto; padding: 0 16px; }
            .card { border: 1px solid #d7d7d7; border-radius: 10px; padding: 24px; }
            label { display: block; margin-top: 12px; font-weight: 600; }
            input, button { width: 100%; box-sizing: border-box; padding: 10px; margin-top: 6px; }
            button { margin-top: 18px; }
            p { color: #555; }
          </style>
        </head>
        <body>
          <div class="card">
            <h1>Admin Login</h1>
            <p>This page is only for internal staff.</p>
            <form>
              <label>Username<input type="text" name="username" autocomplete="off"></label>
              <label>Password<input type="password" name="password"></label>
              <button type="submit">Sign in</button>
            </form>
          </div>
        </body>
        </html>
        """,
        mimetype="text/html",
    )


@app.get("/backup/")
def backup_index():
    if not BACKUP_DIR.exists():
        abort(404)

    items = sorted(path.name for path in BACKUP_DIR.iterdir() if path.is_file())
    links = "".join(f'<li><a href="{name}">{name}</a></li>' for name in items)
    return Response(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Index of /backup/</title>
          <style>
            body {{ font-family: Arial, sans-serif; max-width: 720px; margin: 60px auto; padding: 0 16px; }}
            h1 {{ margin-bottom: 12px; }}
            ul {{ padding-left: 20px; }}
          </style>
        </head>
        <body>
          <h1>Index of /backup/</h1>
          <ul>{links}</ul>
        </body>
        </html>
        """,
        mimetype="text/html",
    )


@app.get("/backup/<path:filename>")
def backup_file(filename: str):
    return send_from_directory(BACKUP_DIR, filename, as_attachment=True)


if __name__ == "__main__":
  host = os.environ.get("HOST", "0.0.0.0")
  port = int(os.environ.get("PORT", "8000"))
  app.run(host=host, port=port, debug=True)