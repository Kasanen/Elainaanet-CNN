"""YAMNet-upotukset mallille C1 (T09).

C1 käyttää YAMNetin omaa esikäsittelyä (16 kHz:n mono-aaltomuoto), ei T04:n
log-meliä (PLAN.md:n poikkeus). YAMNet on jäädytetty esikoulutettu malli, joten
upotukset lasketaan kaikille 400 leikkeelle kerralla ilman datavuotoa: mitään ei
sovita dataan. Normalisointi ja luokitin opetetaan T10:ssä vain opetusfoldeista.

Keras 3:ssa `hub.KerasLayer` ei toimi, joten YAMNet ladataan `hub.load`-funktiolla
ja ajetaan mallin ulkopuolella.
"""

from pathlib import Path

import numpy as np

YAMNET_URL = "https://tfhub.dev/google/yamnet/1"
YAMNET_SR = 16000                     # YAMNet vaatii 16 kHz:n monon
CLIP_SECONDS = 5.0
N_SAMPLES_16K = int(YAMNET_SR * CLIP_SECONDS)   # 80 000 näytettä
EMBED_DIM = 1024
CACHE_NAME = f"yamnet_emb_sr{YAMNET_SR}"


def load_wave_16k(path):
    """Lue leike 16 kHz:n monona, float32 välillä -1…1, täsmälleen 5 s (80 000 näytettä).

    `librosa.load` näytteistää 44,1 kHz:stä 16 kHz:iin (oletusmenetelmä soxr_hq).
    Pituuden pienet poikkeamat korjataan nollilla täyttämällä tai leikkaamalla.
    """
    import librosa
    wave, _ = librosa.load(path, sr=YAMNET_SR, mono=True)
    wave = wave.astype(np.float32)
    if len(wave) < N_SAMPLES_16K:
        wave = np.pad(wave, (0, N_SAMPLES_16K - len(wave)))
    return wave[:N_SAMPLES_16K]


def load_yamnet(url=YAMNET_URL):
    """Lataa YAMNet TensorFlow Hubista (`hub.load`, ei `hub.KerasLayer`)."""
    import tensorflow_hub as hub
    return hub.load(url)


def embed(model, wave):
    """Kehyskohtaiset upotukset yhdelle leikkeelle, muoto (kehykset, 1024).

    YAMNet palauttaa (scores, embeddings, log_mel). Kehys on 0,96 s ja hyppy 0,48 s.
    """
    _, embeddings, _ = model(wave)
    return embeddings.numpy().astype(np.float32)


def build_yamnet_cache(df, cache_dir="data/cache", model=None):
    """Laske upotukset kaikille leikkeille kerran ja tallenna `.npy`-välimuistiin.

    Tiedostot: `{cache_dir}/{CACHE_NAME}.npy` (muoto (leikkeet, kehykset, 1024)) ja
    `{CACHE_NAME}_files.txt` (tiedostonimet samassa järjestyksessä). Jos välimuisti on
    olemassa, se luetaan; jos sen tiedostojärjestys ei vastaa `df`:ää, ValueError.
    Palauttaa taulukon, jonka rivi i vastaa `df`:n riviä i. `model` voidaan antaa
    valmiiksi ladattuna, muuten se ladataan `load_yamnet`-funktiolla.
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

    model = model or load_yamnet()
    x = np.stack([embed(model, load_wave_16k(p)) for p in df["path"]])
    if x.shape[-1] != EMBED_DIM:   # huomaa, jos malli on vaihtunut
        raise ValueError(f"upotuksen koko {x.shape[-1]}, odotettiin {EMBED_DIM}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    np.save(x_path, x)
    names_path.write_text("\n".join(names), encoding="utf-8")
    return x
