"""Datan lataus, fold-jako ja esikäsittely.

T02: ESC-50:n lataus, eläinluokkien suodatus ja tarkistus (`download_esc50`,
`load_metadata`, `check_dataset`).
Tähän tulevat vielä `split(df, k)` (T03) sekä `load_wave`, `log_mel`, välimuisti ja
normalisointi opetusdatan tilastoilla (T04). Muutokset katselmoi toinen jäsen.
"""

from pathlib import Path
import shutil
import urllib.request
import zipfile

import pandas as pd

# ESC-50: https://github.com/karolpiczak/ESC-50 (CC BY-NC 3.0, Piczak 2015)
ESC50_URL = "https://github.com/karolpiczak/ESC-50/archive/master.zip"

# Eläinluokat ovat ESC-50:n `target` 0-9. Indeksi listassa = `target`.
ANIMAL_CLASSES = [
    "dog", "rooster", "pig", "cow", "frog",
    "cat", "hen", "insects", "sheep", "crow",
]
N_CLASSES = len(ANIMAL_CLASSES)
N_FOLDS = 5
SAMPLE_RATE = 44100   # ESC-50:n alkuperäinen näytteenottotaajuus
CLIP_SECONDS = 5.0

# Odotetut määrät: 40 leikettä per luokka, 8 per luokka per foldi.
EXPECTED_CLIPS = 400
EXPECTED_PER_CLASS = 40
EXPECTED_PER_CLASS_FOLD = 8


def download_esc50(data_dir="data", url=ESC50_URL):
    """Lataa ESC-50 ja pura vain eläinluokkien 400 leikettä.

    Tuloksena `data_dir/ESC-50/meta/esc50.csv` (koko alkuperäinen metadata) ja
    `data_dir/ESC-50/audio/*.wav` (vain `target` < 10). Jos data on jo purettu,
    mitään ei ladata uudelleen. Palauttaa ESC-50-kansion polun.
    """
    root = Path(data_dir) / "ESC-50"
    meta_path = root / "meta" / "esc50.csv"
    audio_dir = root / "audio"
    if meta_path.exists() and audio_dir.exists() and len(list(audio_dir.glob("*.wav"))) >= EXPECTED_CLIPS:
        return root

    zip_path = Path(data_dir) / "ESC-50-master.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if not zip_path.exists():
        print(f"Ladataan {url} (useita satoja Mt)...")
        urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        # Zipin juurikansion nimi (yleensä "ESC-50-master/") päätellään metadatasta.
        meta_member = next(n for n in zf.namelist() if n.endswith("meta/esc50.csv"))
        prefix = meta_member[: -len("meta/esc50.csv")]

        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(meta_member) as src, open(meta_path, "wb") as dst:
            shutil.copyfileobj(src, dst)

        df = pd.read_csv(meta_path)
        audio_dir.mkdir(parents=True, exist_ok=True)
        for fname in df.loc[df["target"] < N_CLASSES, "filename"]:
            with zf.open(prefix + "audio/" + fname) as src, open(audio_dir / fname, "wb") as dst:
                shutil.copyfileobj(src, dst)

    zip_path.unlink()  # Zipiä ei enää tarvita, säästää tilaa Drivessa.
    return root


def load_metadata(data_dir="data"):
    """Palauta eläinluokkien metadata DataFramena (400 riviä, `target` 0-9).

    Lisää sarakkeen `path` (koko polku wav-tiedostoon).
    """
    root = Path(data_dir) / "ESC-50"
    df = pd.read_csv(root / "meta" / "esc50.csv")
    df = df[df["target"] < N_CLASSES].reset_index(drop=True)
    df["path"] = [str(root / "audio" / f) for f in df["filename"]]
    return df


def check_dataset(df, check_audio=True):
    """Tarkista, että eläindata on ehjä. Nostaa AssertionErrorin, jos ei ole.

    Tarkistaa: 400 leikettä, 40 per luokka, 8 per luokka per foldi, luokkien nimet
    vastaavat `ANIMAL_CLASSES`-listaa ja (valinnaisesti) jokainen tiedosto on olemassa,
    5 s pitkä, mono ja 44,1 kHz.
    """
    assert len(df) == EXPECTED_CLIPS, f"leikkeitä {len(df)}, odotettiin {EXPECTED_CLIPS}"
    assert df["filename"].is_unique, "sama tiedosto useammin kuin kerran"
    assert sorted(df["fold"].unique()) == list(range(1, N_FOLDS + 1)), "foldit eivät ole 1-5"

    per_class = df["target"].value_counts()
    assert (per_class == EXPECTED_PER_CLASS).all() and len(per_class) == N_CLASSES, \
        f"luokkajakauma väärin: {per_class.to_dict()}"

    per_class_fold = df.groupby(["fold", "target"]).size()
    assert (per_class_fold == EXPECTED_PER_CLASS_FOLD).all() and len(per_class_fold) == N_FOLDS * N_CLASSES, \
        "jokaisessa foldissa pitää olla 8 leikettä jokaisesta luokasta"

    names = df.drop_duplicates("target").set_index("target")["category"].sort_index()
    assert list(names) == ANIMAL_CLASSES, f"luokkien nimet eivät täsmää: {list(names)}"

    if check_audio:
        import soundfile as sf
        for path in df["path"]:
            info = sf.info(path)
            assert info.samplerate == SAMPLE_RATE, f"{path}: {info.samplerate} Hz"
            assert info.channels == 1, f"{path}: {info.channels} kanavaa"
            assert abs(info.duration - CLIP_SECONDS) < 0.01, f"{path}: {info.duration:.2f} s"
    return True
