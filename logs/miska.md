# AI-loki: Miska

Kirjaa tähän jokainen tekoälyn käyttökerta heti, kun käytät sitä. Kurssi vaatii tarkan kirjauksen. Tämän tiedoston muokkaa vain Miska, joten tiedosto ei aiheuta konflikteja muiden kanssa.

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 26.11.2026 | Miska | T25 | Claude (Opus 5.5) | Ehdota `scripts/check_project.py`:n rakenne ja kirjoita koodi | Claude ehdotti rakenteen (tehtävät, tulostiedostot, tavoitteet, palautettavat). Miska päätti, että kynnykset luetaan `PLAN.md`:stä ja että raportti on kansiossa `report/` ja demo tiedostossa `demo/app.py`. Claude kirjoitti skriptin (vain standardikirjasto) ja testasi sen oikealla repolla ja keksityillä tulostiedostoilla: virheelliset tiedostot (rikki JSON, puuttuvat kentät, väärä siemen, puolikas foldi, käsin muutettu accuracy) tunnistetaan, makro-F1 vastaa scikit-learnia, ja tavoitteet arvioidaan vain, kun 5/5 foldia on olemassa. |
| 26.11.2026 | Miska | T25 | Claude (Opus 5.5) | Selitä `scripts/check_project.py` riveittäin ja `/valmis` | Claude selitti koko skriptin osio kerrallaan. Miska vahvisti, että tehtävä on valmis ja että hän osaa selittää koodin. Claude ajoi skriptin (paluukoodi 0, ei virheitä, 27 puuttuvaa tai avointa kohtaa, koska tuloksia ei vielä ole), päivitti `TASKS.md`:n (T25 `[x]`, `tila: valmis`) ja avasi PR:n. |
