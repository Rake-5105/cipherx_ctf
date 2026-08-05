# iDOR — `kolunthu_naadu` / கொழுந்து நாடு — *The Open Ledger*

A CTF challenge in the Cipherx CTF series. Theme: Muziris (Muciri), the
Chera-dynasty spice port, where every transaction was entered into a
*kolunthu* (account book) by a scribe whose job was to remember whose ledger
was whose. In the original port, that scribe's discipline kept the cargo
honest. In this challenge, the scribe has been replaced by a careless
record-keeper — and the door between ledgers is open.

## Event briefing

The customs house at Muciri is preparing for the season's busiest convoy.
Pepper ships, pearl traders, and foreign brokers have all left their cargo
records at the counter. You are a junior scribe asked to verify your first
assigned ledger, but the senior record-keeper has been replaced by a deputy
who trusts a numbered slip more than a merchant's seal.

The royal house keeps one manifest out of the public books: a sealed account
of undeclared cargo and midnight transfers. It was filed among ordinary
merchant records. Follow the ledger trail, discover what the gate fails to
protect, and recover the king's hidden note.

## Title

**`kolunthu_naadu`** (Tamil/Tanglish: *கொழுந்து நாடு*, "the land/domain of
the open account book").

The name borrows *kolunthu* (a young shoot, but in medieval merchant Tamil
also used for an entry in an account book — the "opening" of a new line in
a ledger) and pairs it with *naadu* (kingdom/domain/land). Together it
reads as **"the realm of the ledger that doesn't check who owns it."**

## Backstory (lore)

You are a junior scribe at the Chera customs house of **Muciri**, the
pepper-and-pearl port on the western coast. Yavana (Roman), Tamil, and
Arab merchants file their cargo manifests as numbered ledgers:
ledger **#101** belongs to Anjuvannam Itti Ravi's pepper ship, ledger
**#102** to a pearl trader from the Pandya coast, ledger **#103** to a
frankincense merchant from the north, and so on.

Each ledger has a single stamped page at the customs counter where any
scribe may look up the cargo, broker, and tariff owed. By long custom,
the ledger itself guards who may read it — a sealed edge bearing the
merchant's seal is meant to keep rival traders' eyes off another man's
cargo.

A new deputy has replaced the senior scribe. He checks neither the seal
nor the merchant's name. The ledger book only checks that **a ledger
number is given**; the gate trusts the number, not who stands at it.
Yavana gold leaves the port; pepper enters it; the records are kept — but
**anyone who knows a ledger's number can read it**.

Somewhere in the customs house is a sealed royal ledger — the king's own
record of what was smuggled, what was taxed, and what was never declared.
It carries a ledger number like any other. The deputy didn't even think
to look for it; he simply filed it in the regular sequence, between the
spice-merchant from Tyndis and the silk trader from the Gangetic plain.

## Player-facing description

> *At the Chera customs house of Muciri, each merchant's cargo is held in
> a numbered ledger. Your job as a customs scribe is to look up a ledger
> by its number and confirm its contents. Some ledgers are public; some
> are private. The door is open, the counter is unguarded, and the only
> thing the gate checks is the number on the slip.*
>
> *Find the royal ledger and read what the king wanted kept out of the
> port's books.*

## Vulnerability

Insecure Direct Object Reference (IDOR). The `/manifest/<id>` route reads
the integer from the URL and returns that ledger's record without any
ownership check. The intended exploitation is sequential enumeration:

- `/manifest/101` — your own ledger (a normal cargo record)
- `/manifest/102` — another trader's private ledger (an unexpected peek)
- `/manifest/103` ... `/manifest/<n>` — keep walking through the sequence
- somewhere in that sequence, the royal ledger — flag inside

The mechanics the player will hit:

1. Notice the URL pattern `/manifest/<number>` on their own ledger.
2. Change the number and submit; the server returns the new ledger's
   contents without complaint.
3. Enumerate forward / backward through the integer space to find ledgers
   they shouldn't have access to.
4. Find the royal ledger; the flag is rendered in the response body.

## Routes (file/URL layout)

```
/                       landing — gateway / dockyard narrative
/manifest/<int:id>      public ledger viewer (the vulnerable route)
/hall                   records room — list of merchants + a hint about
                        the royal ledger living somewhere in the sequence
/healthz                liveness probe for gunicorn/systemd
```

Recommended file layout (mirrors the basic2/ convention but with new
theming):

```
iDOR/
├── app.py
├── requirements.txt
├── .gitignore
├── .env.example
├── flag.txt                  # fallback flag file (placeholder)
├── deploy/                   # runnable bundle for the sysadmin
│   ├── app.py
│   ├── requirements.txt
│   ├── README.md
│   ├── .env.example
│   ├── flag.txt
│   └── templates/
│       ├── gateway.html
│       ├── manifest.html
│       └── hall.html
├── ledgers/                  # static seed data, one file per ledger id
│   ├── 101.txt               # player's own ledger
│   ├── 102.txt
│   ├── 103.txt
│   ├── ...
│   └── <royal>.txt           # flag lives here
└── templates/
    ├── gateway.html
    ├── manifest.html
    └── hall.html
```

The URL pattern `/manifest/<id>` keeps the integer exploitable while the
Tamil route name (*kolunthu*, *vaniga-p-pattayam*, *pattayam-kaappu*) is
left for a richer template rebrand later.

## Flag options (pick one)

All three fit `C1X{...}` format and the Chera/Muziris theme:

1. **`C1X{muc1r1_k0lunthu_kaapu_kandaan}`**
   *Translation:* "The one who found the open ledger at Muziris."
   `muc1r1` (Muziris), `k0lunthu` (ledger), `kaapu` (guard/seal),
   `kandaan` (one who saw). Reads cleanly; refers directly to the bug.

2. **`C1X{pepper_g0ld_ar1sen_pat1yam}`**
   *Translation:* "The pepper-gold ledger of Arsinoe" — an inside nod
   to the *Periplus of the Erythraean Sea* and *Akananuru 149*, which
   describe Roman gold arriving and pepper leaving. Poetic and
   historically accurate.

3. **`C1X{kaanom_k0lunthu_p0la_v1thiyum}`**
   *Translation:* "What the gate lets through, the ledger sees" — a
   construction echoing Tamil verb pattern (*kaan + om* "it sees",
   *pola* "like", *vithiyum* "is sold/recorded"). Most thematic; reads
   almost like a Sangam line.

**Recommendation:** option **1** — it names the city, the artefact, and
the act, all in three leetspeak chunks. Easy to recognise on a CTF score
board, hard to false-positive.

## In-page hint (Tamil proverb / Sangam-style line)

A single line on the **/hall** (records room) page, beneath the merchant
list, in italics:

> *எண்ணைக் கேட்டால் பதிலளிக்கும் வாயில், உரிமையைக் கேட்பதில்லை.*
>
> *"The gate answers to a number. It never asks whose name is on the
> ledger behind it."*

This is intentionally a modern Tamil construction, not a quoted Sangam
verse — keeping it accurate to the genre without fabricating ancient
authorship. It nudges the player toward enumeration without saying the
word.

A *secondary*, optional line on `/manifest/<id>` when a private (non-public)
ledger is opened (so the player gets a quiet dopamine hit when they
realise they've crossed out of their own):

> *"யாருடையது என்று அறியேன்; என் கண்ணுக்குத் தெரிந்தது எண்ணளவாய்
> இருந்தது."*
>
> *"I do not know whose it is; my eyes were given only a number."*

## Implementation sketch (for your reference, not yet written)

```python
@app.route("/manifest/<int:ledger_id>")
def manifest(ledger_id: int):
    # IDOR: no ownership / authorization check. Any integer is valid.
    record = ledger_store.get(ledger_id)
    if not record:
        return "No ledger with that number.", 404
    return render_template("manifest.html", record=record, ledger_id=ledger_id)
```

Seed data should include:
- 1 "player's own" ledger (#101)
- ~10-15 normal merchant ledgers (102..115 or so) — some flagged as
  private, just to teach the player that **all** are reachable
- 1 royal ledger with the flag, embedded inside the otherwise-cargo
  content (so the player has to read the response body, not just see
  the page load)

## Deployment (Ubuntu, gunicorn + systemd + nginx)

A production deployment will need:

- `gunicorn --bind 127.0.0.1:8080 --workers 3 app:app` behind nginx
- systemd unit pointing at a venv-installed gunicorn
- nginx reverse-proxy on `:80` / `:443` with `proxy_pass
  http://127.0.0.1:8080`
- `flag.txt` provisioned at deploy time by the sysadmin (one of the
  three flag options, no other place holds it)

The `deploy/` folder pattern from `basic2/` is recommended — admin gets
an operator README, the source gets the lore + design doc you are
reading now.
