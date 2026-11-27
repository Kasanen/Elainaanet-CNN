"""Datan lataus, fold-jako ja esikäsittely.

T02: ESC-50:n lataus, eläinluokkien suodatus ja tarkistus (`download_esc50`,
`load_metadata`, `check_dataset`).
T03: fold-jako (`split_folds`, `split`).
T04: esikäsittely (`load_wave`, `log_mel`), `.npy`-välimuisti (`build_cache`) ja
normalisointi opetusdatan tilastoilla (`fit_normalizer`, `normalize`, `fold_arrays`).
Muutokset katselmoi toinen jäsen.
"""

from pathlib import Path
import shutil
import urllib.request
import zipfile

import numpy as np
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


# --- T03: fold-jako -------------------------------------------------------------

def split_folds(k):
    """Palauta ajon k foldit: (opetusfoldit, validointifoldi, testifoldi).

    Testifoldi on k. Validointifoldi on seuraava foldi kiertäen (k=5 -> 1), joten
    jokainen foldi on täsmälleen kerran testinä ja kerran validointina. Loput kolme
    foldia ovat opetusta. Jako on kiinteä eikä riipu satunnaisuudesta.
    """
    if k not in range(1, N_FOLDS + 1):
        raise ValueError(f"k:n pitää olla 1-{N_FOLDS}, saatiin {k}")
    test_fold = k
    val_fold = k % N_FOLDS + 1
    train_folds = [f for f in range(1, N_FOLDS + 1) if f not in (test_fold, val_fold)]
    return train_folds, val_fold, test_fold


def split(df, k):
    """Jaa data ajolle k viralliseen foldiin perustuen: (train_df, val_df, test_df).

    Kaikki mallit (A, B, C1, C2) käyttävät tätä samaa jakoa. Validointi on yksi
    kokonainen foldi, ei satunnaista osuutta, koska ESC-50:ssä samasta
    lähdeäänitteestä leikatut pätkät ovat samassa foldissa. Satunnainen jako
    vuotaisi samaa äänitettä opetukseen ja validointiin.
    Testifoldiin (`test_df`) ei kosketa viritysvaiheessa.
    """
    train_folds, val_fold, test_fold = split_folds(k)
    train_df = df[df["fold"].isin(train_folds)].reset_index(drop=True)
    val_df = df[df["fold"] == val_fold].reset_index(drop=True)
    test_df = df[df["fold"] == test_fold].reset_index(drop=True)

    # Varmistus: jokainen leike on täsmälleen yhdessä osassa.
    assert len(train_df) + len(val_df) + len(test_df) == len(df)
    parts = [set(train_df["filename"]), set(val_df["filename"]), set(test_df["filename"])]
    assert not (parts[0] & parts[1] or parts[0] & parts[2] or parts[1] & parts[2])
    return train_df, val_df, test_df


# --- T04: esikäsittely, välimuisti ja normalisointi ----------------------------
# Mallit A, B ja C2 käyttävät tätä log-meliä. C1 käyttää YAMNetin omaa
# esikäsittelyä (16 kHz), ks. PLAN.md.

N_SAMPLES = int(SAMPLE_RATE * CLIP_SECONDS)   # 220 500 näytettä
N_FFT = 2048          # ikkuna 46 ms (44,1 kHz)
HOP_LENGTH = 512      # hyppy 11,6 ms -> 431 aikakehystä
N_MELS = 128
CACHE_NAME = f"logmel_sr{SAMPLE_RATE}_m{N_MELS}_h{HOP_LENGTH}"


def load_wave(path):
    """Lue leike float32-aaltomuodoksi, jonka pituus on täsmälleen 5 s (220 500 näytettä).

    Ei uudelleennäytteistystä: tiedoston pitää olla 44,1 kHz ja mono, muuten ValueError.
    Pituuden pienet poikkeamat korjataan nollilla täyttämällä tai leikkaamalla, jotta
    kaikista leikkeistä tulee samankokoinen spektrogrammi.
    """
    import soundfile as sf
    wave, sr = sf.read(path, dtype="float32")
    if sr != SAMPLE_RATE:
        raise ValueError(f"{path}: {sr} Hz, odotettiin {SAMPLE_RATE} Hz")
    if wave.ndim != 1:
        raise ValueError(f"{path}: ei mono ({wave.shape[1]} kanavaa)")
    if len(wave) < N_SAMPLES:
        wave = np.pad(wave, (0, N_SAMPLES - len(wave)))
    return wave[:N_SAMPLES]


def log_mel(wave, sr=SAMPLE_RATE, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=N_MELS):
    """Log-mel-spektrogrammi desibeleinä, muoto (n_mels, aikakehykset) = (128, 431).

    `ref=1.0` pitää desibelit absoluuttisina (ei leikekohtaista maksimia), joten
    voimakkuuserot leikkeiden välillä säilyvät. `top_db=None`: ei leikekohtaista
    leikkausta; hiljaisuuden alaraja on librosan `amin`-arvosta -100 dB.
    """
    import librosa
    S = librosa.feature.melspectrogram(y=wave, sr=sr, n_fft=n_fft,
                                       hop_length=hop_length, n_mels=n_mels)
    return librosa.power_to_db(S, ref=1.0, top_db=None).astype(np.float32)


def build_cache(df, cache_dir="data/cache"):
    """Laske log-mel kaikille leikkeille kerran ja tallenna `.npy`-välimuistiin.

    Tiedostot: `{cache_dir}/{CACHE_NAME}.npy` (muoto (400, 128, 431)) ja
    `{CACHE_NAME}_files.txt` (tiedostonimet samassa järjestyksessä). Parametrit ovat
    nimessä, joten muutetut parametrit eivät käytä vanhaa välimuistia. Jos välimuisti
    on olemassa, se luetaan; jos sen tiedostojärjestys ei vastaa `df`:ää, ValueError.
    Palauttaa taulukon, jonka rivi i vastaa `df`:n riviä i.
    """
    cache_dir = Path(cache_dir)
    x_path = cache_dir / f"{CACHE_NAME}.npy"
    names_path = cache_dir / f"{CACHE_NAME}_files.txt"
    names = list(df["filename"])

    if x_path.exists() and names_path.exists():
        if names_path.read_text(encoding="utf-8").split() != names:
            raise ValueError(f"välimuistin tiedostojärjestys ei vastaa metadataa: "
                             f"poista {x_path} ja {names_path.name} ja laske uudelleen")
        return np.load(x_path)

    x = np.stack([log_mel(load_wave(p)) for p in df["path"]])
    cache_dir.mkdir(parents=True, exist_ok=True)
    np.save(x_path, x)
    names_path.write_text("\n".join(names), encoding="utf-8")
    return x


def fit_normalizer(x_train):
    """Mel-kaistakohtainen keskiarvo ja keskihajonta, kumpikin muotoa (n_mels, 1).

    Anna tälle vain opetusdata (ei validointia eikä testiä), muuten syntyy datavuoto.
    """
    mean = x_train.mean(axis=(0, 2))[:, np.newaxis]
    std = x_train.std(axis=(0, 2))[:, np.newaxis]
    return mean.astype(np.float32), np.maximum(std, 1e-6).astype(np.float32)


def normalize(x, mean, std):
    """Normalisoi `fit_normalizer`-funktion tilastoilla: (x - mean) / std."""
    return ((x - mean) / std).astype(np.float32)


def fold_arrays(df, k, cache):
    """Ajon k data malleille A, B ja C2: ((x_tr, y_tr), (x_va, y_va), (x_te, y_te)).

    Jako tulee `split(df, k)`-funktiosta. Normalisoinnin tilastot lasketaan vain
    opetusfoldeista, ja samoilla luvuilla normalisoidaan validointi- ja testifoldi.
    x:n muoto on (leikkeet, 128, 431, 1) (kanava-akseli Kerasin Conv2D:tä varten),
    y on luokkanumerot 0-9. `cache` on `build_cache(df)`-funktion palauttama taulukko.
    """
    if len(cache) != len(df):
        raise ValueError(f"välimuistissa {len(cache)} riviä, metadatassa {len(df)}")
    position = {name: i for i, name in enumerate(df["filename"])}
    parts = split(df, k)

    x_parts = [cache[[position[f] for f in part["filename"]]] for part in parts]
    mean, std = fit_normalizer(x_parts[0])          # vain opetusdata
    return tuple((normalize(x, mean, std)[..., np.newaxis], part["target"].to_numpy())
                 for x, part in zip(x_parts, parts))
