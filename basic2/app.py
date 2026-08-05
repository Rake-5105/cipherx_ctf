import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, request, render_template, url_for

# Load FLAG (and any other config) from a .env file kept outside the
# challenge source. The flag is never a literal in this file.
#
# Pin to the directory next to app.py so dotenv doesn't walk up to a parent
# .env file (which on a developer's machine might be a different challenge).
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _load_flag() -> str:
    """Resolve the flag from env, falling back to flag.txt at the repo root.

    The fallback exists only so local development works without leaking the
    real flag into the shipped source. Production deployments MUST set FLAG
    via the environment.
    """
    flag = os.environ.get("FLAG")
    if flag:
        return flag.strip()

    fallback = BASE_DIR / "flag.txt"
    if fallback.is_file():
        return fallback.read_text(encoding="utf-8").strip()

    raise RuntimeError(
        "FLAG is not configured. Set the FLAG environment variable or create "
        "flag.txt next to app.py."
    )


app = Flask(__name__)

# Resolved at import time. Never sent to the client unless the request
# passes the authorization check on /kalanjiyam/inner-chamber.
FLAG = _load_flag()


def _is_authorized(req: request) -> bool:
    role = req.cookies.get("role", "")
    mudirai = req.cookies.get("mudirai", "")
    return role == "4dm1n" or mudirai == "aracan_thondan"


@app.route("/")
@app.route("/kalanjiyam")
def outer_hall():
    # Solve the challenge by setting role=4dm1n or mudirai=aracan_thondan.
    # On success, redirect to the inner chamber, which is the ONLY route
    # that ever includes the flag in its response body.
    if _is_authorized(request):
        return redirect(url_for("inner_chamber"))

    # The outer hall never echoes the request's cookies back to the page --
    # the cookie is part of the player's craft, not part of the UI.
    return render_template("outer_hall.html")


@app.route("/kalanjiyam/inner-chamber")
def inner_chamber():
    if not _is_authorized(request):
        # Stay consistent with the previous behaviour: a polite 403 from the
        # challenge's own response only -- no flag in the body.
        return (
            "<h1>403 Forbidden</h1>"
            "<p>Access denied. You do not have permission to enter the inner "
            "chamber.</p>",
            403,
        )

    # Authorized: this is the one place the flag is rendered. Keep it on the
    # challenge site only -- do not embed {{ flag }} anywhere else.
    return render_template("inner_chamber.html", flag=FLAG)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    public_host = os.environ.get("PUBLIC_HOST", "localhost")
    print(f"Open http://{public_host}:{port}/")
    app.run(host=host, port=port, debug=False)
