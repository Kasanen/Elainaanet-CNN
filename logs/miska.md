# AI-loki: Miska

Kirjaa tähän jokainen tekoälyn käyttökerta heti, kun käytät sitä. Kurssi vaatii tarkan kirjauksen. Tämän tiedoston muokkaa vain Miska, joten tiedosto ei aiheuta konflikteja muiden kanssa.

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 26.11.2026 | Miska | T06 | Claude (Opus 5.5) | Ehdota `src/train.py`:n rakenne ja kirjoita koodi | Claude ehdotti rakenteen (`set_seed`, `make_callbacks`, `train_model`, `evaluate`, `save_results`), ja Miska päätti, että callbackit seuraavat `val_loss`:ia ja CSV-lokit tallennetaan `results/history/`-kansioon. Claude kirjoitti koodin ja ajoi savutestin satunnaisdatalla (TF 2.22.0-rc1 / Keras 3.16 dev, ei Colabin versio): tiedostot syntyvät, JSON-kentät vastaavat `PLAN.md`:tä, one-hot-tunnisteet muuttuvat luokkanumeroiksi, ja parhaat painot palautuvat sekä aikaisessa pysähtymisessä että ilman sitä. |
