"""YAMNet-upotukset (T09) ja niiden data ja vertailu mallille C1 (T10).

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


# --- T10: data ja vertailu mallille C1 ------------------------------------------

POOLINGS = ("mean", "max", "meanmax")


def pool_embeddings(emb, method="meanmax"):
    """Yhdistä kehykset leikkeen tasolle: (n, kehykset, 1024) -> (n, 1024) tai (n, 2048).

    `mean` = kehysten keskiarvo, `max` = kehysten maksimi (voimakkain kohta ohittaa
    hiljaiset kehykset), `meanmax` = molemmat peräkkäin.
    """
    if method == "mean":
        return emb.mean(axis=1)
    if method == "max":
        return emb.max(axis=1)
    if method == "meanmax":
        return np.concatenate([emb.mean(axis=1), emb.max(axis=1)], axis=1)
    raise ValueError(f"tuntematon pooling '{method}', vaihtoehdot {POOLINGS}")


def c1_fold_arrays(df, k, emb, pooling="meanmax"):
    """Ajon k data mallille C1: ((x_tr, y_tr), (x_va, y_va), (x_te, y_te)).

    Jako tulee `split(df, k)`-funktiosta, joten foldit ovat samat kuin muilla malleilla.
    Pooling -> standardointi ulottuvuuskohtaisesti vain opetusfoldien keskiarvolla ja
    keskihajonnalla. Ulottuvuudet, jotka ovat opetusdatassa vakioita (keskihajonta
    lähes 0), jaetaan ykkösellä, jotta validointi- ja testiarvot eivät räjähdä.
    `emb` on `build_yamnet_cache(df)`-funktion palauttama taulukko.
    """
    from src.data import split
    if len(emb) != len(df):
        raise ValueError(f"upotuksia {len(emb)} riviä, metadatassa {len(df)}")
    position = {name: i for i, name in enumerate(df["filename"])}
    parts = split(df, k)

    x_parts = [pool_embeddings(emb[[position[f] for f in part["filename"]]], pooling)
               for part in parts]
    mean = x_parts[0].mean(axis=0)                  # vain opetusdata
    std = x_parts[0].std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    return tuple((((x - mean) / std).astype(np.float32), part["target"].to_numpy())
                 for x, part in zip(x_parts, parts))


def compare_c1(df, emb, poolings=POOLINGS, hiddens=(0, 256), folds=(1, 2, 3, 4, 5),
               epochs=200, batch_size=32):
    """T10:n vertailu: pooling x piilokerros, jokainen viidellä ajolla.

    Käyttää vain opetus- ja validointifoldia; testifoldi heitetään pois (`_`) eikä sitä
    koskaan arvioida. Tiedostoja ei tallenneta (`save_files=False`). Palauttaa
    DataFramen, jossa rivi per (pooling, hidden, foldi): validointitarkkuus ja -häviö
    parhaan epookin painoilla (EarlyStopping palauttaa ne) sekä epookkien määrä.
    """
    import pandas as pd
    from src.models import build_c1
    from src.train import set_seed, train_model

    rows = []
    for pooling in poolings:
        for k in folds:
            (x_tr, y_tr), (x_va, y_va), _ = c1_fold_arrays(df, k, emb, pooling)
            for hidden in hiddens:
                set_seed()
                model = build_c1(x_tr.shape[1], hidden=hidden)
                history, secs = train_model(model, (x_tr, y_tr), (x_va, y_va), "C1", k,
                                            epochs=epochs, batch_size=batch_size,
                                            save_files=False, verbose=0)
                val_loss, val_acc = model.evaluate(x_va, y_va, verbose=0)
                rows.append({"pooling": pooling, "hidden": hidden, "fold": k,
                             "val_acc": float(val_acc), "val_loss": float(val_loss),
                             "epochs": len(history.history["loss"]), "seconds": round(secs, 1)})
    return pd.DataFrame(rows)
