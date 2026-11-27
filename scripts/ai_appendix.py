"""Kokoaa raportin liitteen tekoälyn käytöstä jäsenten AI-lokeista (T22).

Ajo repon juuresta:

    python scripts/ai_appendix.py           # kirjoittaa report/liitteet/ai_kaytto.md
    python scripts/ai_appendix.py --check   # paluukoodi 1, jos liite ei vastaa lokeja (T24)

Lukee tiedostot logs/{elias,miska,taif,veijo}.md eikä koskaan muokkaa niitä. Liitteen
rivit ovat täsmälleen lokien rivit; skripti ei kirjoita arvioivaa tekstiä. Puutteellisista
riveistä tulostetaan varoitus, ja korjauksen tekee lokin omistaja omaan lokiinsa.
Pelkkä Pythonin standardikirjasto.
"""

import argparse
from collections import Counter
import datetime as dt
from pathlib import Path
import re
import sys

MEMBERS = ["Elias", "Miska", "Taif", "Veijo"]
COLUMNS = ["Päivä", "Kuka", "Tehtävä", "Työkalu", "Mitä pyydettiin", "Mitä käytettiin ja muutettiin"]
OUTPUT = Path("report") / "liitteet" / "ai_kaytto.md"

ROW_RE = re.compile(r"^\|\s*\d{1,2}\.\d{1,2}\.\d{4}\s*\|")   # taulukkorivi alkaa päivämäärällä
CELL_SPLIT = re.compile(r"(?<!\\)\|")                       # jakaja: | ilman edeltävää \-merkkiä
TASK_RE = re.compile(r"\bT\d{2}\b")


def parse_log(path, owner, label):
    """Palauta (rivit, varoitukset). Rivi on sanakirja COLUMNS-avaimilla + järjestysnumero.

    `label` on varoituksissa näytettävä polku (esim. logs/veijo.md). Rivin lopun |-merkki
    on Markdownissa valinnainen, joten molemmat muodot hyväksytään.
    """
    rows, warnings = [], []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not ROW_RE.match(line):
            continue
        parts = CELL_SPLIT.split(line.strip())[1:]       # ensimmäinen osa on tyhjä (rivin alun |)
        if parts and not parts[-1].strip():
            parts = parts[:-1]                           # rivin lopun | (valinnainen)
        cells = [c.strip() for c in parts]
        where = f"{label}:{lineno}"
        if len(cells) != len(COLUMNS):
            warnings.append(f"{where}: {len(cells)} saraketta, odotettiin {len(COLUMNS)} "
                            "(tarkista |-merkit tekstissä)")
            if len(cells) > len(COLUMNS):          # ylimääräiset sarakkeet viimeiseen, ei hukata tekstiä
                cells = cells[:5] + [r" \| ".join(cells[5:])]   # \| ei riko taulukkoa
            cells += [""] * (len(COLUMNS) - len(cells))
        row = dict(zip(COLUMNS, cells))
        try:
            row["_date"] = dt.datetime.strptime(row["Päivä"], "%d.%m.%Y").date()
        except ValueError:
            warnings.append(f"{where}: päivämäärä '{row['Päivä']}' ei ole muotoa pp.kk.vvvv")
            row["_date"] = dt.date.max
        if row["Kuka"] != owner:
            warnings.append(f"{where}: Kuka on '{row['Kuka']}', lokin omistaja {owner}")
        for col in ("Mitä pyydettiin", "Mitä käytettiin ja muutettiin"):
            if not row[col]:
                warnings.append(f"{where}: sarake '{col}' on tyhjä")
        row["_order"] = lineno
        row["_owner"] = owner
        rows.append(row)
    return rows, warnings


def tasks_of(row):
    """T-numerot Tehtävä-sarakkeesta, esim. 'T02, T03' -> ['T02', 'T03']."""
    return TASK_RE.findall(row["Tehtävä"])


def table(rows):
    lines = ["| " + " | ".join(COLUMNS) + " |", "| " + " | ".join("---" for _ in COLUMNS) + " |"]
    lines += ["| " + " | ".join(r[c] for c in COLUMNS) + " |" for r in rows]
    return lines


def build_appendix(logs):
    """logs: {jäsen: rivit}. Palauttaa liitteen Markdown-tekstinä."""
    all_rows = [r for rows in logs.values() for r in rows]
    out = [
        "# Liite: Tekoälyn käyttö",
        "",
        "Tämä liite on koottu ryhmän jäsenten AI-lokeista (`logs/*.md`) komennolla "
        "`python scripts/ai_appendix.py`. Rivit ovat lokien rivit sellaisinaan. "
        "Älä muokkaa tätä tiedostoa käsin: korjaa oma lokisi ja aja komento uudelleen.",
        "",
        "## Yhteenveto",
        "",
        "| Jäsen | Kirjauksia | Aikaväli |",
        "| --- | --- | --- |",
    ]
    for member, rows in logs.items():
        dates = sorted(r["_date"] for r in rows if r["_date"] != dt.date.max)
        span = f"{dates[0]:%d.%m.%Y}–{dates[-1]:%d.%m.%Y}" if dates else "–"
        out.append(f"| {member} | {len(rows)} | {span} |")
    out.append(f"| **Yhteensä** | **{len(all_rows)}** | |")

    tools = Counter(r["Työkalu"] for r in all_rows)
    out += ["", "**Työkalut (kuten lokeihin kirjattu):** "
            + (", ".join(f"{t} ({n})" for t, n in sorted(tools.items())) if tools else "–")]

    per_task = {}
    for r in all_rows:
        for t in tasks_of(r) or ["muu"]:
            per_task.setdefault(t, set()).add(r["_owner"])   # lokin omistaja, ei Kuka-sarake
    if per_task:
        out += ["", "**Tehtävät, joissa tekoälyä käytettiin:**", "",
                "| Tehtävä | Jäsenet |", "| --- | --- |"]
        for t in sorted(per_task, key=lambda t: (t == "muu", t)):
            label = "muu (ei T-numeroa)" if t == "muu" else t
            out.append(f"| {label} | {', '.join(sorted(per_task[t]))} |")

    for member, rows in logs.items():
        out += ["", f"## {member}", ""]
        if rows:
            out += table(sorted(rows, key=lambda r: (r["_date"], r["_order"])))
        else:
            out.append("Ei kirjauksia.")
    return "\n".join(out) + "\n"


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="älä kirjoita; paluukoodi 1, jos liite puuttuu tai ei vastaa lokeja")
    parser.add_argument("--root", help="repon juuri (oletus: tämän skriptin yläkansio)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent

    logs, warnings = {}, []
    for member in MEMBERS:
        path = root / "logs" / f"{member.lower()}.md"
        if not path.exists():
            warnings.append(f"logs/{member.lower()}.md puuttuu")
            logs[member] = []
            continue
        logs[member], w = parse_log(path, member, f"logs/{member.lower()}.md")
        warnings += w
    for w in warnings:
        print(f"[VAROITUS] {w}")

    text = build_appendix(logs)
    out_path = root / OUTPUT
    if args.check:
        current = out_path.read_text(encoding="utf-8") if out_path.exists() else None
        if current != text:
            print(f"[EI AJAN TASALLA] {OUTPUT.as_posix()}: aja `python scripts/ai_appendix.py`")
            return 1
        print(f"[OK] {OUTPUT.as_posix()} vastaa lokeja")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8", newline="\n")
    counts = ", ".join(f"{m} {len(r)}" for m, r in logs.items())
    print(f"Kirjoitettu {OUTPUT.as_posix()}: {sum(len(r) for r in logs.values())} riviä ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
