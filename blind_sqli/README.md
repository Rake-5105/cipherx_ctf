# Cipherx CTF — Blind SQLi Challenge

A blind SQL injection CTF challenge. The page reveals only `User found` / `User not found` for a given username; the player has to extract the admin's password hash (which is the base64-encoded flag) via boolean and timing oracles.

- **Author:** Team CyberSec · `r4k3`
- **Stack:** Flask · SQLite · Vanilla CSS

## Flag

`C1X{sangam_oliyin_seyal}`

## Lore

In the age of the ancient Tamil courts, a sealed archive was said to hold the truth of a vanished inscription. The scribes of the Sangam era recorded the king's hidden seal in a pattern that could only be read through patience, rhythm, and inference rather than force.

The archive was guarded by a blind oracle. It never revealed the full record directly, only whether the seeker had found the correct name. Those who listened carefully to the pauses, the repeated replies, and the subtle delay between words could reconstruct the lost passage, decode the royal seal, and uncover the final truth buried beneath the script of the old land.

## File structure

```
.
├── app.py                  # Flask app, / endpoint + /lookup JSON API
├── ctf-sqli.service        # systemd unit for hosting
├── nginx-sqli.conf         # nginx reverse-proxy config
├── requirements.txt        # Python deps
├── reset_db.sh             # resets the SQLite DB from the seeded backup
├── solve.py                # reference exploit
├── ctf_sqli.sqlite3        # live database
├── db_backup.sqlite        # clean seed backup
├── solution.md             # walkthrough of the intended solve
├── static/
│   └── styles.css          # all UI styling
└── templates/
    └── index.html          # single page
```

## Hosting Bundle

When deploying the challenge, keep the runtime files together in a separate folder such as `deploy/`:

```text
deploy/
├── app.py                  # Flask application and challenge logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # single-page UI template
├── static/
│   └── styles.css          # frontend styling
├── ctf-sqli.service        # systemd unit for Linux hosting
└── nginx-sqli.conf         # reverse proxy configuration
```

## Local / Support Files

These files are useful for development, solving, or database reset, but they do not need to live inside the hosting bundle:

- `ctf_sqli.sqlite3` — live SQLite database
- `db_backup.sqlite` — clean backup used by the reset script
- `reset_db.sh` — database reseed helper
- `solve.py` — reference exploit
- `solution.md` — walkthrough for the intended solve

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app listens on `http://127.0.0.1:5000`. On first run it creates `ctf_sqli.sqlite3` and seeds six users (alice, bob, charlie, diana, eve, admin). The admin row's `password_hash` is the base64-encoded flag.

To wipe the DB and reseed from the backup:

```bash
./reset_db.sh                      # Linux/macOS
# Windows: copy /Y db_backup.sqlite ctf_sqli.sqlite3
```

## Vulnerability

The `username` form field is interpolated directly into a SQLite query, with no parameterization or escaping:

```python
raw_sql = f"SELECT id, username, password_hash, is_admin FROM users WHERE username = '{username}' LIMIT 1"
```

Any error or non-matching result is folded into a generic `User not found` response — no data ever leaks directly. The player has to use boolean-blind (does this user exist?) and time-blind (does this expression take longer?) techniques. See `solution.md` for the full walkthrough and `solve.py` for an automated exploit.

## Intended solve

1. Enumerate the schema with `sqlite_master` via UNION-based boolean probes.
2. Recover the admin's `password_hash` char-by-char using `substr(...) = 'X'` boolean tests (and confirm via `randomblob(...)`-induced timing delays under `CASE WHEN`).
3. Base64-decode the recovered hash to get the flag.

## Frontend notes

- The page is intentionally minimal: a single hero, a four-panel "challenge" grid, and the lookup form. No navbar.
- Form submission goes through a JSON endpoint (`/lookup`) so the page does not reload or scroll on submit — the result appears directly under the input.
- Result text is rendered in the CRT font at a large size for readability.
- A faint `r4k3` author mark sits in the bottom-right corner.

## Deployment

Two production configs are included:

- `ctf-sqli.service` — systemd unit. Drop into `/etc/systemd/system/`, then `systemctl enable --now ctf-sqli`.
- `nginx-sqli.conf` — reverse proxy in front of gunicorn/uwsgi. Adjust the `server_name` and TLS paths before use.

## UI updates (this session)

The following changes were applied to `templates/index.html` and `static/styles.css`:

- Hero simplified to a single line `B1IND SQ1i` (lowercase `i` for stylization), `CTF` line removed.
- Subtitle trimmed to `Challenge Your Mind. Break the Code.`.
- Footer fixed to `· Team CyberSec ·` (was `> Team CyberSec ·`).
- Lookup form: now submits via `fetch` to `/lookup` JSON endpoint, preventing page reload and scroll-to-top.
- Lookup result: font size increased from 13px to 32px, centered, thicker left border.
- Page layout: `max-width` widened from 1240px to 1600px, side gap reduced from 48px to 16px so the content fills the viewport.
- Bottom-right `r4k3` author mark added in a faint pixel font.
