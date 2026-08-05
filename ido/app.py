import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request

# Pin dotenv to this directory so the app is portable -- the deploy bundle
# can't accidentally pick up an unrelated .env from a parent folder.
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

LEDGER_DIR = BASE_DIR / "ledgers"

# Hostname and TCP port for the gateway view. Defaults match the basic2/
# convention so admin scripts can run both challenges side by side.
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8080))
PUBLIC_HOST = os.environ.get("PUBLIC_HOST", "localhost")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Ledger store
# ---------------------------------------------------------------------------
#
# Each ledger is a plain text file in LEDGER_DIR, named "<id>.txt". The
# contents are the scribe's transcription: merchant, cargo, broker, tariff,
# visibility. The royal ledger (116) holds the flag.
#
# In a "production" version this would be a database row with an owner
# column and an authorization check. Here there is no such column -- the
# gate trusts the number, not the merchant who stands at it. That is the
# IDOR.


def _load_ledgers() -> dict[int, list[str]]:
    """Read every ledger file in LEDGER_DIR into an in-memory dict.

    Lines are returned as a list so the template can render them
    verbatim. Missing or unreadable files are silently skipped -- the
    challenge keeps running even if a couple of ledgers go missing.
    """
    ledgers: dict[int, list[str]] = {}
    if not LEDGER_DIR.is_dir():
        return ledgers
    for path in sorted(LEDGER_DIR.glob("*.txt")):
        try:
            ledger_id = int(path.stem)
        except ValueError:
            continue
        try:
            content = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        ledgers[ledger_id] = content
    return ledgers


_LEDGERS = _load_ledgers()


def _summary_for_hall() -> list[dict]:
    """First-line-per-ledger summary used by /hall."""
    rows = []
    for ledger_id in sorted(_LEDGERS):
        lines = _LEDGERS[ledger_id]
        title = lines[0] if lines else "(empty ledger)"
        # Second line often carries cargo; we keep it for a richer list.
        cargo = lines[1] if len(lines) > 1 else ""
        rows.append({"id": ledger_id, "title": title, "cargo": cargo})
    return rows


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
@app.route("/kolunthu")
def gateway():
    """The dockyard landing page -- sets the scene, sends the player into
    the customs hall. No ledger IDs are revealed here.
    """
    return render_template("gateway.html")


@app.route("/records")
def hall():
    """List every merchant summary; ledger numbers are intentionally hidden."""
    return render_template("records.html", ledgers=_summary_for_hall())


@app.route("/manifest/<int:ledger_id>")
def manifest(ledger_id: int):
    """Intentionally vulnerable IDOR route for this CTF challenge."""
    lines = _LEDGERS.get(ledger_id)
    if lines is None:
        # 404, not 403 -- the gate doesn't know whose ledger it is, only
        # that there isn't one with that number. That phrasing matters.
        return render_template("not_found.html", ledger_id=ledger_id), 404

    visibility = "public"
    for line in lines:
        if line.lower().startswith("visibility:"):
            visibility = line.split(":", 1)[1].strip()
            break

    return render_template(
        "manifest.html",
        ledger_id=ledger_id,
        lines=lines,
        visibility=visibility,
    )


@app.route("/healthz")
def healthz():
    """Liveness probe for gunicorn / systemd."""
    return "ok", 200


if __name__ == "__main__":
    print(f"Open http://{PUBLIC_HOST}:{PORT}/kolunthu")
    app.run(host=HOST, port=PORT, debug=False)
