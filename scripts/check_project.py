"""Projektin tarkistus (T25): tehtävät, tulostiedostot, tavoitteet ja palautettavat.

Ajo repon juuresta:

    python scripts/check_project.py            # raportti, paluukoodi 1 vain jos tiedostoissa on virheitä
    python scripts/check_project.py --strict   # palautustarkistus (T24): myös puuttuvat -> paluukoodi 1

Skripti vain lukee tiedostoja (TASKS.md, PLAN.md, results/, notebooks/, README.md,
report/, demo/, logs/). Se ei koske dataan eikä malleihin ja käyttää vain Pythonin
standardikirjastoa, joten sen voi ajaa millä tahansa koneella.

Kynnysarvot luetaan PLAN.md:n tavoitetaulukosta. Tavoite on "OK" vain, jos mallilla on
kaikki viisi foldia. "OK" tarkoittaa vain, että tulostiedostojen luvut ylittävät
kynnyksen; ryhmän pitää silti todentaa tulokset.
"""

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import statistics
import sys

MODELS = ["A", "B", "C1", "C2"]
TRANSFER_MODELS = ["C1", "C2"]
FOLDS = [1, 2, 3, 4, 5]
N_CLASSES = 10
FOLD_SIZE = 80                    # testileikkeitä per foldi (10 luokkaa x 8)
SEED = 42
RESULT_FIELDS = ["model", "fold", "seed", "accuracy", "macro_f1", "params",
                 "train_seconds", "y_true", "y_pred"]
ABLATION_MIN_SETTINGS = 4         # T17: 4 augmentaatioasetusta x 5 foldia
PROJECT_YEAR = 2026               # TASKS.md:n takarajoissa ei ole vuotta
MEMBERS = ["elias", "miska", "veijo", "taif"]
REPORT_DIR = "report"
REPORT_EXTS = {".pdf", ".docx", ".md"}
DEMO_FILE = "demo/app.py"
ESC50_LINK = "github.com/karolpiczak/ESC-50"
TOL = 1e-4                        # sallittu ero tallennetun ja uudelleen lasketun metriikan välillä

# PLAN.md:n tavoitetaulukon rivien alut. Kynnys luetaan rivin toisesta sarakkeesta.
GOAL_ROWS = {
    "a_acc": "Malli A (baseline) tarkkuus",
    "best_acc": "Paras malli tarkkuus",
    "best_f1": "Paras malli makro-F1",
    "transfer": "Siirto-oppiminen",
}

RESULT_RE = re.compile(r"^(A|B|C1|C2)_fold([1-5])\.json$")
ABLATION_RE = re.compile(r"^ablation_(.+)_fold([1-5])\.json$")
TASK_RE = re.compile(r"^- \[( |x)\] \*\*(T\d+)\*\*")
META_RE = re.compile(r"takaraja: ([^·]*)·\s*ottaja: ([^·]*)·\s*tila: (.+)$")


class Report:
    """Tulostaa rivit ja laskee virheet ja puuttuvat kohdat paluukoodia varten."""

    PROBLEMS = {"PUUTTUU", "EI TÄYTY", "EI ARVIOITAVISSA", "MYÖHÄSSÄ", "AVOIN"}

    def __init__(self):
        self.errors = 0
        self.problems = 0

    def section(self, title):
        print(f"\n== {title} ==")

    def item(self, status, text):
        print(f"[{status}] {text}")
        if status == "VIRHE":
            self.errors += 1
        elif status in self.PROBLEMS:
            self.problems += 1

    def info(self, text):
        print(f"    {text}")


def pct(value):
    return f"{value * 100:.1f} %"


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


# --- 1. Tehtävät -----------------------------------------------------------------

def parse_date(text):
    """'to 26.11.' -> date(2026, 11, 26). Palauttaa None, jos päivämäärää ei ole."""
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.", text)
    return dt.date(PROJECT_YEAR, int(m.group(2)), int(m.group(1))) if m else None


def parse_tasks(text):
    """Lue TASKS.md:n tehtävärivit ja niiden alla olevat metatietorivit."""
    tasks = []
    lines = text.splitlines()
    for i, line in enumerate(lines[:-1]):
        m = TASK_RE.match(line)
        meta = META_RE.search(lines[i + 1]) if m else None
        if meta:
            tasks.append({
                "id": m.group(2),
                "checked": m.group(1) == "x",
                "deadline": parse_date(meta.group(1)),
                "owner": meta.group(2).strip(),
                "state": meta.group(3).strip(),
            })
    return tasks


def check_tasks(rep, root, today):
    rep.section("Tehtävät (TASKS.md)")
    text = read_text(root / "TASKS.md")
    if text is None:
        rep.item("PUUTTUU", "TASKS.md")
        return
    tasks = parse_tasks(text)
    if not tasks:
        rep.item("VIRHE", "TASKS.md:stä ei löytynyt yhtään tehtäväriviä")
        return

    done = sum(t["checked"] for t in tasks)
    rep.info(f"valmiina {done}/{len(tasks)} tehtävää")
    for t in tasks:
        if t["checked"] != (t["state"] == "valmis"):
            box = "[x]" if t["checked"] else "[ ]"
            rep.item("VIRHE", f"{t['id']}: ruutu {box}, mutta tila '{t['state']}'")
    for t in tasks:
        if t["state"] == "työn alla":
            rep.info(f"työn alla: {t['id']} ({t['owner']})")
    for t in tasks:
        if t["state"] != "valmis" and t["deadline"] and t["deadline"] < today:
            rep.item("MYÖHÄSSÄ", f"{t['id']} (takaraja {t['deadline']:%d.%m.}, "
                                 f"ottaja {t['owner']}, tila {t['state']})")


# --- 2. Tulostiedostot ------------------------------------------------------------

def macro_f1(y_true, y_pred):
    """Makro-F1 kuten scikit-learnin f1_score(average="macro"): luokat, jotka esiintyvät
    y_true- tai y_pred-listassa, ja F1 = 0, jos luokalla ei ole yhtään osumaa."""
    scores = []
    for c in sorted(set(y_true) | set(y_pred)):
        tp = sum(t == c and p == c for t, p in zip(y_true, y_pred))
        fp = sum(t != c and p == c for t, p in zip(y_true, y_pred))
        fn = sum(t == c and p != c for t, p in zip(y_true, y_pred))
        denom = 2 * tp + fp + fn
        scores.append(2 * tp / denom if denom else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def validate_result(data, name, fold):
    """Palauta lista virheistä (tyhjä, jos tiedosto on kunnossa)."""
    if not isinstance(data, dict):
        return ["tiedosto ei ole JSON-olio"]
    missing = [f for f in RESULT_FIELDS if f not in data]
    if missing:
        return [f"kentät puuttuvat: {', '.join(missing)}"]

    errs = []
    if data["model"] != name:
        errs.append(f"model on '{data['model']}', tiedostonimen mukaan '{name}'")
    if data["fold"] != fold:
        errs.append(f"fold on {data['fold']}, tiedostonimen mukaan {fold}")
    if data["seed"] != SEED:
        errs.append(f"seed on {data['seed']}, pitää olla {SEED}")
    if not all(isinstance(data[f], (int, float)) for f in ("accuracy", "macro_f1")):
        return errs + ["accuracy tai macro_f1 ei ole luku"]

    yt, yp = data["y_true"], data["y_pred"]
    if not isinstance(yt, list) or not isinstance(yp, list) or len(yt) != len(yp):
        return errs + ["y_true ja y_pred eivät ole yhtä pitkiä listoja"]
    if len(yt) != FOLD_SIZE:
        errs.append(f"{len(yt)} testileikettä, odotettiin {FOLD_SIZE} (yksi kokonainen foldi)")
    if not all(isinstance(v, int) and 0 <= v < N_CLASSES for v in yt + yp):
        return errs + [f"y_true/y_pred sisältää muuta kuin luokkia 0-{N_CLASSES - 1}"]
    if yt:
        acc = sum(t == p for t, p in zip(yt, yp)) / len(yt)
        if abs(acc - data["accuracy"]) > TOL:
            errs.append(f"accuracy {data['accuracy']:.4f}, mutta y_true/y_pred antaa {acc:.4f}")
        f1 = macro_f1(yt, yp)
        if abs(f1 - data["macro_f1"]) > TOL:
            errs.append(f"macro_f1 {data['macro_f1']:.4f}, mutta y_true/y_pred antaa {f1:.4f}")
    return errs


def load_result(rep, path, name, fold):
    """Lue ja tarkista yksi tulostiedosto. Palauttaa datan tai None, jos virheellinen."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        rep.item("VIRHE", f"{path.name}: ei luettavissa ({e})")
        return None
    errs = validate_result(data, name, fold)
    for err in errs:
        rep.item("VIRHE", f"{path.name}: {err}")
    return None if errs else data


def check_results(rep, root):
    """Palauttaa (results, ablation): {malli: {foldi: data}} ja {asetus: {foldi: data}},
    joissa on vain virheettömät tiedostot."""
    rep.section("Tulostiedostot (results/)")
    results = {m: {} for m in MODELS}
    ablation = {}
    bad = set()
    res_dir = root / "results"
    for path in sorted(res_dir.glob("*.json")) if res_dir.exists() else []:
        if m := RESULT_RE.match(path.name):
            name, fold = m.group(1), int(m.group(2))
            data = load_result(rep, path, name, fold)
            if data is None:
                bad.add((name, fold))
            else:
                results[name][fold] = data
        elif m := ABLATION_RE.match(path.name):
            setting, fold = m.group(1), int(m.group(2))
            data = load_result(rep, path, f"ablation_{setting}", fold)
            if data is not None:
                ablation.setdefault(setting, {})[fold] = data
        else:
            rep.info(f"tuntematon tiedosto ohitettiin: {path.name}")

    # Taulukko: OK = virheetön, !! = virheellinen, -- = puuttuu
    print("        " + "".join(f"f{k:<4}" for k in FOLDS))
    for name in MODELS:
        cells = ["OK" if k in results[name] else "!!" if (name, k) in bad else "--" for k in FOLDS]
        print(f"    {name:<4}" + "".join(f"{c:<5}" for c in cells))
    for name in MODELS:
        missing = [k for k in FOLDS if k not in results[name] and (name, k) not in bad]
        if missing:
            rep.item("PUUTTUU", f"{name}: foldit {', '.join(map(str, missing))}")

    # Oppimiskäyrät (CSVLogger, T06) tarvitaan T18:n kuvaajiin.
    hist_dir = root / "results" / "history"
    no_hist = [f"{name}_fold{k}" for name in MODELS for k in sorted(results[name])
               if not list(hist_dir.glob(f"{name}_fold{k}*.csv"))]
    if no_hist:
        rep.item("PUUTTUU", f"oppimiskäyrät (results/history/): {', '.join(no_hist)}")

    if ablation:
        rep.info("ablaatio: " + ", ".join(f"{s} {len(f)}/5" for s, f in sorted(ablation.items())))
    return results, ablation


# --- 3. Tavoitteet ----------------------------------------------------------------

def parse_goals(text):
    """Lue kynnykset PLAN.md:n tavoitetaulukosta: '≥ 70 %' -> 0.70, '≥ 0,85' -> 0.85,
    '+10 prosenttiyksikköä' -> 0.10."""
    goals = {}
    for key, label in GOAL_ROWS.items():
        m = re.search(rf"^\|\s*{re.escape(label)}[^|]*\|([^|]+)\|", text, re.M)
        num = re.search(r"(\d+(?:[.,]\d+)?)", m.group(1)) if m else None
        if num:
            value = float(num.group(1).replace(",", "."))
            if "%" in m.group(1) or "prosenttiyksik" in m.group(1):
                value /= 100
            goals[key] = value
    return goals


def summarize(folds):
    """Tarkkuuden ja makro-F1:n keskiarvo ja keskihajonta (otoskeskihajonta, n=5)."""
    accs = [folds[k]["accuracy"] for k in FOLDS]
    f1s = [folds[k]["macro_f1"] for k in FOLDS]
    return {"acc": statistics.mean(accs), "acc_sd": statistics.stdev(accs),
            "f1": statistics.mean(f1s), "f1_sd": statistics.stdev(f1s)}


def check_goals(rep, root, results, ablation):
    rep.section("Tavoitteet (PLAN.md)")
    text = read_text(root / "PLAN.md")
    if text is None:
        rep.item("PUUTTUU", "PLAN.md")
        return
    goals = parse_goals(text)
    for key, label in GOAL_ROWS.items():
        if key not in goals:
            rep.item("VIRHE", f"PLAN.md:n tavoiteriviä '{label}' ei löytynyt tai siinä ei ole lukua")

    complete = {m: summarize(results[m]) for m in MODELS if len(results[m]) == len(FOLDS)}
    for m in MODELS:
        if m in complete:
            s = complete[m]
            rep.info(f"{m}: tarkkuus {pct(s['acc'])} ± {s['acc_sd'] * 100:.1f}, "
                     f"makro-F1 {s['f1']:.3f} ± {s['f1_sd']:.3f}")
        else:
            rep.info(f"{m}: {len(results[m])}/5 foldia")

    def verdict(ok, text):
        rep.item("OK" if ok else "EI TÄYTY", text)

    if "a_acc" in goals:
        label = f"Malli A tarkkuus ≥ {pct(goals['a_acc'])}"
        if "A" in complete:
            verdict(complete["A"]["acc"] >= goals["a_acc"], f"{label}: {pct(complete['A']['acc'])}")
        else:
            rep.item("EI ARVIOITAVISSA", f"{label} (A: {len(results['A'])}/5 foldia)")

    if "best_acc" in goals or "best_f1" in goals:
        if len(complete) == len(MODELS):
            best = max(complete, key=lambda m: complete[m]["acc"])
            s = complete[best]
            if "best_acc" in goals:
                verdict(s["acc"] >= goals["best_acc"],
                        f"Paras malli ({best}) tarkkuus ≥ {pct(goals['best_acc'])}: {pct(s['acc'])}")
            if "best_f1" in goals:
                verdict(s["f1"] >= goals["best_f1"],
                        f"Paras malli ({best}) makro-F1 ≥ {goals['best_f1']:.2f}: {s['f1']:.3f}")
        else:
            missing = ", ".join(m for m in MODELS if m not in complete)
            rep.item("EI ARVIOITAVISSA", f"Paras malli (vaatii kaikki neljä mallia, kesken: {missing})")

    if "transfer" in goals:
        label = f"Siirto-oppiminen (C1 tai C2) vähintään +{goals['transfer'] * 100:.0f} %-yks. yli A:n"
        diffs = {m: complete[m]["acc"] - complete["A"]["acc"]
                 for m in TRANSFER_MODELS if m in complete and "A" in complete}
        shown = ", ".join(f"{m} {d * 100:+.1f}" for m, d in diffs.items())
        if any(d >= goals["transfer"] for d in diffs.values()):
            rep.item("OK", f"{label}: {shown}")
        elif "A" in complete and len(diffs) == len(TRANSFER_MODELS):
            rep.item("EI TÄYTY", f"{label}: {shown}")
        else:
            rep.item("EI ARVIOITAVISSA", f"{label} (A, C1 ja C2 tarvitsevat 5/5 foldia)")

    full = {s: summarize(f) for s, f in ablation.items() if len(f) == len(FOLDS)}
    for s, v in sorted(full.items()):
        rep.info(f"ablaatio {s}: tarkkuus {pct(v['acc'])} ± {v['acc_sd'] * 100:.1f}")
    if len(full) >= ABLATION_MIN_SETTINGS:
        rep.item("OK", f"Ablaatio: {len(full)} asetusta, kaikilla 5/5 foldia")
    else:
        rep.item("EI ARVIOITAVISSA",
                 f"Ablaatio: {len(full)}/{ABLATION_MIN_SETTINGS} asetusta valmiina (5/5 foldia)")


# --- 4. Palautettavat -------------------------------------------------------------

def plan_section(text, heading):
    """PLAN.md:n osion teksti otsikosta '## heading...' seuraavaan '## '-otsikkoon."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def check_deliverables(rep, root):
    rep.section("Palautettavat")

    notebooks = sorted((root / "notebooks").glob("*.ipynb"))
    if not notebooks:
        rep.item("PUUTTUU", "notebooks/: ei yhtään .ipynb-tiedostoa")
    else:
        no_html = [nb.name for nb in notebooks if not nb.with_suffix(".html").exists()]
        if no_html:
            rep.item("PUUTTUU", f".html-versio (T24): {', '.join(no_html)}")
        else:
            rep.item("OK", f"{len(notebooks)} notebookia, kaikilla .html-versio")

    readme = read_text(root / "README.md") or ""
    rep.item("OK" if ESC50_LINK.lower() in readme.lower() else "PUUTTUU",
             "README: linkki ESC-50-datasettiin")
    rep.item("OK" if "uudelleenkoulut" in readme.lower() else "PUUTTUU",
             "README: uudelleenkoulutusohje")

    reports = [p.name for p in (root / REPORT_DIR).glob("*") if p.suffix.lower() in REPORT_EXTS]
    rep.item("OK" if reports else "PUUTTUU",
             f"raportti {REPORT_DIR}/" + (f": {', '.join(reports)}" if reports else " (.pdf, .docx tai .md)"))
    rep.item("OK" if (root / DEMO_FILE).exists() else "PUUTTUU", f"demo {DEMO_FILE}")

    for member in MEMBERS:
        log = read_text(root / "logs" / f"{member}.md")
        rows = len(re.findall(r"^\|\s*\d{1,2}\.\d{1,2}\.\d{4}\s*\|", log or "", re.M))
        rep.item("OK" if rows else "PUUTTUU", f"AI-loki logs/{member}.md: {rows} riviä")

    plan = read_text(root / "PLAN.md") or ""
    dod = re.findall(r"^- \[( |x)\] (.+)$", plan_section(plan, "Valmiin määritelmä"), re.M)
    if dod:
        rep.info(f"PLAN.md valmiin määritelmä: {sum(c == 'x' for c, _ in dod)}/{len(dod)} merkitty")
    grade = re.findall(r"^\|\s*([^|]+?)\s*\|.*\|\s*\[( |x)\]\s*\|\s*$",
                       plan_section(plan, "Arvosana 5"), re.M)
    if grade:
        rep.info(f"PLAN.md arvosana 5 -lista: {sum(c == 'x' for _, c in grade)}/{len(grade)} merkitty")
        for item, checked in grade:
            if checked != "x":
                rep.item("AVOIN", f"arvosana 5: {item}")


# --- Pääohjelma -------------------------------------------------------------------

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # ääkköset Windowsin konsolissa
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true",
                        help="paluukoodi 1 myös, jos jotain puuttuu tai tavoite ei täyty (T24)")
    parser.add_argument("--root", help="repon juuri (oletus: tämän skriptin yläkansio)")
    parser.add_argument("--today", help="päivämäärä VVVV-KK-PP myöhästymisiä varten (oletus: tänään)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    rep = Report()
    print(f"Projektin tarkistus {today:%d.%m.%Y}")

    check_tasks(rep, root, today)
    results, ablation = check_results(rep, root)
    check_goals(rep, root, results, ablation)
    check_deliverables(rep, root)

    rep.section("Yhteenveto")
    print(f"virheitä {rep.errors}, puuttuvia tai avoimia kohtia {rep.problems}")
    if rep.errors:
        return 1
    return 1 if args.strict and rep.problems else 0


if __name__ == "__main__":
    sys.exit(main())
