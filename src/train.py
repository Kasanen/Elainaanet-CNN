"""Yhteinen koulutusfunktio, callbackit ja tulosten tallennus results/-kansioon (T06).

Kaikki mallit (A, B, C1, C2) käyttävät näitä funktioita, jotta koulutus ja
tulokset ovat vertailukelpoisia. Käyttö yhdellä foldilla:

    set_seed()
    model = ...rakenna ja käännä malli (src/models.py)...
    history, secs = train_model(model, train_data, val_data, "A", k)
    metrics = evaluate(model, x_test, y_test)      # vasta lopullisessa ajossa
    save_results("A", k, metrics, model.count_params(), secs)

`train_model` ei saa testidataa lainkaan: callbackit seuraavat vain
validointifoldia (`val_loss`). Testifoldi arvioidaan erikseen `evaluate`-funktiolla.
"""

import json
from pathlib import Path
import time

import keras
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

SEED = 42


def set_seed(seed=SEED):
    """Aseta Pythonin, NumPyn ja TensorFlow'n siemen. Kutsu ennen mallin rakentamista."""
    keras.utils.set_random_seed(seed)


def run_name(name, fold, stage=None):
    """Tiedostonimen runko, esim. `A_fold3` tai `C2_fold3_head`."""
    return f"{name}_fold{fold}" + (f"_{stage}" if stage else "")


def make_callbacks(name, fold, stage=None, models_dir="models",
                   history_dir="results/history", patience=15, lr_patience=5,
                   save_files=True):
    """Palauta yhteiset callbackit. Kaikki seuraavat validointihäviötä (`val_loss`).

    - EarlyStopping lopettaa, kun `val_loss` ei ole parantunut `patience` epookkiin,
      ja palauttaa parhaan epookin painot.
    - ReduceLROnPlateau puolittaa oppimisnopeuden, kun `val_loss` ei parane
      `lr_patience` epookkiin.
    - ModelCheckpoint tallentaa parhaan mallin: `models/{name}_fold{k}.keras`.
      Nimessä ei ole `stage`-osaa, joten C2:n hienosäätövaihe ylikirjoittaa
      pää-vaiheen tiedoston ja lopullinen malli on vakionimellä.
    - CSVLogger kirjaa jokaisen epookin häviöt ja tarkkuudet:
      `results/history/{name}_fold{k}[_{stage}].csv` (oppimiskuvaajat, T18).

    `save_files=False` jättää ModelCheckpointin ja CSVLoggerin pois. KerasTuner (T11)
    käyttää tätä, koska `tuner.search` kutsuu `fit`-funktiota itse jokaisella
    kokeilulla ja tiedostot muuten ylikirjoittuisivat.
    """
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience, restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=lr_patience, min_lr=1e-6, verbose=1),
    ]
    if save_files:
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        Path(history_dir).mkdir(parents=True, exist_ok=True)
        callbacks += [
            keras.callbacks.ModelCheckpoint(
                str(Path(models_dir) / f"{run_name(name, fold)}.keras"),
                monitor="val_loss", save_best_only=True),
            keras.callbacks.CSVLogger(
                str(Path(history_dir) / f"{run_name(name, fold, stage)}.csv")),
        ]
    return callbacks


def train_model(model, train_data, val_data, name, fold, epochs=100, batch_size=None,
                stage=None, extra_callbacks=None, **callback_kwargs):
    """Kouluta valmiiksi käännetty malli. Palauttaa (history, train_seconds).

    `train_data` ja `val_data` ovat joko `(x, y)`-pareja (monikko tai lista) tai
    `keras.utils.PyDataset`-olioita. Testidataa tälle funktiolle ei anneta. `stage`
    erottaa saman ajon vaiheiden CSV-lokit (C2: "head" ja "ft").
    `callback_kwargs` (esim. `patience=10`) välitetään `make_callbacks`-funktiolle.
    """
    callbacks = make_callbacks(name, fold, stage=stage, **callback_kwargs)
    callbacks += list(extra_callbacks or [])

    if isinstance(train_data, (tuple, list)):
        x, y = train_data
        fit_args = dict(x=x, y=y, batch_size=batch_size)
    else:
        fit_args = dict(x=train_data)   # PyDataset hoitaa erät itse
    if isinstance(val_data, list):
        val_data = tuple(val_data)      # fit odottaa validointiparin monikkona

    start = time.perf_counter()
    history = model.fit(**fit_args, validation_data=val_data, epochs=epochs,
                        callbacks=callbacks, verbose=2)
    train_seconds = time.perf_counter() - start
    return history, train_seconds


def evaluate(model, x_test, y_test):
    """Arvioi malli testifoldilla. Palauttaa accuracy, macro_f1, y_true ja y_pred.

    `y_test` voi olla luokkanumerot (0-9) tai one-hot-matriisi (esim. mixupin
    vuoksi), ja tulokset palautetaan aina luokkanumeroina.
    """
    y_true = np.asarray(y_test)
    if y_true.ndim == 2:
        y_true = y_true.argmax(axis=1)
    y_pred = model.predict(x_test, verbose=0).argmax(axis=1)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "y_true": [int(v) for v in y_true],
        "y_pred": [int(v) for v in y_pred],
    }


def save_results(name, fold, metrics, params, train_seconds, seed=SEED, results_dir="results"):
    """Tallenna ajon tulos `results/{name}_fold{k}.json` PLAN.md:n muodossa.

    `name` on `A`, `B`, `C1`, `C2` tai ablaatiossa `ablation_{asetus}`.
    `metrics` on `evaluate`-funktion palauttama sanakirja. Palauttaa tiedoston polun.
    """
    result = {
        "model": name,
        "fold": int(fold),
        "seed": int(seed),
        "accuracy": metrics["accuracy"],
        "macro_f1": metrics["macro_f1"],
        "params": int(params),
        "train_seconds": round(float(train_seconds), 1),
        "y_true": metrics["y_true"],
        "y_pred": metrics["y_pred"],
    }
    path = Path(results_dir) / f"{run_name(name, fold)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path
