import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, request, render_template, url_for
from jinja2 import ChoiceLoader, DictLoader, FileSystemLoader

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
        lines = [line.strip() for line in fallback.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]
        if lines:
            return lines[-1]

    raise RuntimeError(
        "FLAG is not configured. Set the FLAG environment variable or create "
        "flag.txt next to app.py."
    )


_OUTER_HALL_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ponni Kalanjiyam - Outer Hall</title>
  <style>
    :root {
      --ink: #2c1d12;
      --deep-ink: #1a1008;
      --sand: #f4e7c8;
      --parchment: #fbf3dd;
      --bronze: #8b5e34;
      --gold: #c7a24a;
      --clay: #b46a3c;
      --shadow: rgba(48, 28, 12, 0.24);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top, rgba(199, 162, 74, 0.22), transparent 32%),
        linear-gradient(180deg, #20130d 0%, #3a2314 16%, #f0dfb6 16%, #ead4a0 100%);
      padding: 32px 18px 40px;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(135deg, rgba(180, 106, 60, 0.08) 25%, transparent 25%, transparent 50%, rgba(180, 106, 60, 0.08) 50%, rgba(180, 106, 60, 0.08) 75%, transparent 75%, transparent);
      background-size: 42px 42px;
      opacity: 0.3;
      mix-blend-mode: multiply;
    }

    .container {
      position: relative;
      max-width: 860px;
      margin: 0 auto;
      padding: 34px 30px 30px;
      background: linear-gradient(180deg, rgba(251, 243, 221, 0.98), rgba(244, 231, 200, 0.98));
      border: 1px solid rgba(139, 94, 52, 0.35);
      border-radius: 22px;
      box-shadow: 0 24px 48px var(--shadow);
      overflow: hidden;
    }

    .container::before {
      content: "";
      position: absolute;
      inset: 12px;
      border: 1px solid rgba(139, 94, 52, 0.18);
      border-radius: 16px;
      pointer-events: none;
    }

    h1 {
      margin: 0 0 14px;
      color: var(--deep-ink);
      font-size: clamp(2rem, 4vw, 3.1rem);
      letter-spacing: 0.03em;
      line-height: 1.05;
    }

    .subtitle {
      margin: 0 0 24px;
      color: #634028;
      font-size: 1.05rem;
      line-height: 1.7;
    }

    .panel {
      position: relative;
      margin: 20px 0;
      padding: 18px 20px;
      background: rgba(255, 250, 236, 0.85);
      border-left: 6px solid var(--gold);
      border-radius: 14px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
    }

    .panel h2 {
      margin: 0 0 8px;
      font-size: 1rem;
      color: var(--bronze);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .hint {
      background: linear-gradient(180deg, rgba(199, 162, 74, 0.12), rgba(180, 106, 60, 0.08));
    }

    p {
      font-size: 1.04rem;
      line-height: 1.8;
      margin: 0 0 16px;
    }

    .divider {
      height: 1px;
      margin: 24px 0 18px;
      background: linear-gradient(90deg, transparent, rgba(139, 94, 52, 0.65), transparent);
    }

    .crest {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 18px;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(255, 250, 236, 0.75);
      color: var(--bronze);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 0.78rem;
      font-weight: 700;
    }

    .crest::before,
    .crest::after {
      content: "✦";
      color: var(--gold);
    }

    @media (max-width: 640px) {
      body { padding: 18px 12px 28px; }
      .container { padding: 24px 18px 18px; border-radius: 18px; }
      p { font-size: 1rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="crest">Ponni Kalanjiyam</div>
    <h1>Outer Hall of the Bronze Archives</h1>
    <p class="subtitle">Before the sacred vault, visitors enter a hall of carved stone, copper lamps, and archival seals. The outer chamber preserves the memory of the Chola waterworks, where every channel was measured like a hymn and every gate was built to resist the flood.</p>

    <div class="panel hint">
      <h2>Gatekeeper's note</h2>
      <p>
        The bronze gate remembers the <em>mark</em> of every wayfarer who passes, not their face. Palms that bear no seal are turned away at the threshold; palms that bear the <em>forged mark</em> are admitted without question, for the gate trusts what it is given.
      </p>
      <p>
        Those who walk the old courts know that the mark is something the wayfarer carries in their own hand, slipped quietly into the pouch at the threshold &mdash; never spoken aloud, never written into the ledger. Forge it well, and the bronze gate will yield.
      </p>
    </div>

    <p>
      Beyond the bronze threshold lies the chamber said to hold the king's hidden seal, copied from the river plans of Karikala and guarded by those who know the old names of power. Only the properly marked may enter.
    </p>
    <div class="divider"></div>
    <p>
      In the lore of this vault, the chamber answers only to a forged mark. Those who understand the old administration of the river granaries know that the seal is not steel, but belief made visible &mdash; and that the court, in its pride, never learned to question what it was handed.
    </p>
  </div>
</body>
</html>"""

_INNER_CHAMBER_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ponni Kalanjiyam - Inner Chamber</title>
  <style>
    :root {
      --ink: #26150a;
      --gold: #d2ab4a;
      --bronze: #8a5a2d;
      --seal: #1f160f;
      --jade: #2f7a5f;
      --shadow: rgba(31, 18, 10, 0.26);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top, rgba(210, 171, 74, 0.22), transparent 34%),
        linear-gradient(180deg, #19120d 0%, #352115 14%, #eadab0 14%, #f6e7bf 100%);
      padding: 32px 18px 40px;
      text-align: center;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        radial-gradient(circle at 20% 20%, rgba(138, 90, 45, 0.16) 0 2px, transparent 2px),
        radial-gradient(circle at 80% 30%, rgba(138, 90, 45, 0.16) 0 2px, transparent 2px),
        radial-gradient(circle at 30% 80%, rgba(138, 90, 45, 0.14) 0 2px, transparent 2px),
        radial-gradient(circle at 75% 75%, rgba(138, 90, 45, 0.14) 0 2px, transparent 2px);
      background-size: 140px 140px;
      opacity: 0.6;
    }

    .container {
      position: relative;
      max-width: 760px;
      margin: 0 auto;
      padding: 36px 28px 30px;
      background: linear-gradient(180deg, rgba(255, 249, 229, 0.98), rgba(241, 226, 185, 0.98));
      border: 1px solid rgba(138, 90, 45, 0.34);
      border-radius: 24px;
      box-shadow: 0 26px 52px var(--shadow);
      overflow: hidden;
    }

    .container::before {
      content: "";
      position: absolute;
      inset: 12px;
      border: 1px solid rgba(138, 90, 45, 0.16);
      border-radius: 18px;
      pointer-events: none;
    }

    .crest {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 14px;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(255, 248, 226, 0.9);
      color: var(--bronze);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 0.78rem;
      font-weight: 700;
    }

    .crest::before,
    .crest::after {
      content: "✦";
      color: var(--gold);
    }

    h1 {
      margin: 6px 0 16px;
      font-size: clamp(2rem, 4vw, 3.15rem);
      color: var(--seal);
      line-height: 1.05;
      letter-spacing: 0.03em;
    }

    .success {
      margin: 0 0 16px;
      color: var(--jade);
      font-size: 1.08rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .flag {
      margin: 26px auto 22px;
      max-width: 100%;
      padding: 22px 18px;
      background: linear-gradient(180deg, #1f160f, #2f2116);
      color: #f7e6bc;
      border: 1px solid rgba(210, 171, 74, 0.45);
      border-radius: 16px;
      font-family: "Consolas", "Courier New", monospace;
      letter-spacing: 0.14em;
      font-size: clamp(1rem, 2vw, 1.2rem);
      word-break: break-word;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .lore {
      margin: 0 auto;
      max-width: 640px;
      line-height: 1.85;
      font-size: 1.03rem;
    }

    .lore strong {
      color: var(--bronze);
    }

    .divider {
      width: 180px;
      height: 1px;
      margin: 22px auto 18px;
      background: linear-gradient(90deg, transparent, rgba(138, 90, 45, 0.72), transparent);
    }

    @media (max-width: 640px) {
      body { padding: 18px 12px 28px; }
      .container { padding: 24px 18px 20px; border-radius: 18px; }
      .lore { font-size: 1rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="crest">Inner Chamber</div>
    <h1>Vault of the Hidden Seal</h1>
    <p class="success">Access granted. The bronze gate has accepted your forged seal.</p>
    <div class="flag">{{ flag }}</div>
    <div class="divider"></div>
    <p class="lore">
      <strong>Flag lore:</strong> In the oldest record of Ponni Kalanjiyam, the king did not hide treasure, but a secret of legitimacy. The seal was forged from river mud, temple bronze, and the knowledge of those who measured the Kaveri's rise. The glyph inside the vault marks the one who could cross from public archive into sovereign memory. It is said the flag is not merely a prize, but the signature of Karikala's final decree, preserved for anyone clever enough to counterfeit the court's trust.
    </p>
  </div>
</body>
</html>"""

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.jinja_loader = ChoiceLoader([
    FileSystemLoader([
        str(BASE_DIR / "templates"),
        str(Path.cwd() / "templates"),
        "/var/task/templates",
        "/var/task/deploy/templates",
        str(BASE_DIR),
    ]),
    DictLoader({
        "outer_hall.html": _OUTER_HALL_HTML,
        "inner_chamber.html": _INNER_CHAMBER_HTML,
    }),
])

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
    if _is_authorized(request):
        return redirect(url_for("inner_chamber"))

    return render_template("outer_hall.html")


@app.route("/kalanjiyam/inner-chamber")
def inner_chamber():
    if not _is_authorized(request):
        return (
            "<h1>403 Forbidden</h1>"
            "<p>Access denied. You do not have permission to enter the inner chamber.</p>",
            403,
        )

    return render_template("inner_chamber.html", flag=FLAG)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    public_host = os.environ.get("PUBLIC_HOST", "localhost")
    print(f"Open http://{public_host}:{port}/")
    app.run(host=host, port=port, debug=False)
