# AI-loki: Miska

Kirjaa tähän jokainen tekoälyn käyttökerta heti, kun käytät sitä. Kurssi vaatii tarkan kirjauksen. Tämän tiedoston muokkaa vain Miska, joten tiedosto ei aiheuta konflikteja muiden kanssa.

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 26.11.2026 | Miska | T02 | Claude (Opus 5.5) | Tee T02: lataa ESC-50, suodata eläinluokat ja tarkista 400 leikettä | Claude kirjoitti `src/data.py`:hen funktiot `download_esc50`, `load_metadata` ja `check_dataset`, skriptin `scripts/download_esc50.py` ja README:n Data-osion. Testattu: 400 leikettä, 40 per luokka, 8 per luokka per foldi, kaikki 5 s / 44,1 kHz / mono; tarkistus huomaa puuttuvan rivin ja väärän foldin. |
