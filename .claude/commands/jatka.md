---
description: Tarkista projektin tila ja kerro, missä tehtävässä edetään ja mikä on seuraava askel
---

Aloita istunto: selvitä projektin tila ja ehdota seuraava askel. Tämä komento on vain lukeva: älä varaa tehtävää, muokkaa tiedostoja äläkä commitoi, ennen kuin käyttäjä vahvistaa.

1. Aja `git pull`, `git log -10 --oneline`, `git branch --show-current` ja `gh pr list`. Jos jokin epäonnistuu, kerro se äläkä arvaa.
2. Lue `CLAUDE.md`, `TASKS.md` ja `PLAN.md`.
3. Kysy käyttäjän nimi (Elias, Miska, Veijo tai Taif), ellei se ilmene. Git-käyttäjänimi ei kerro sitä.
4. Raportoi suomeksi tiiviisti:
   - Edistyminen: montako tehtävää `[x]` kaikista, nykyinen vaihe ja sen takaraja suhteessa tämän päivän päivämäärään.
   - `työn alla` -tehtävät ja niiden ottajat. Jos käyttäjällä on oma keskeneräinen tehtävä, kerro sen haara ja ehdota jatkamaan siitä.
   - Seuraava vapaa tehtävä: ylin rivi, jonka `tila` on `vapaa` ja jonka `vaatii`-tehtävät ovat kaikki `valmis`.
   - Myöhässä tai jumissa: `työn alla` -tehtävät, joiden takaraja on ohi, ja avoimet PR:t, jotka odottavat yhdistämistä.
5. Aja `python scripts/check_project.py`, jos tiedosto on olemassa. Jos sitä ei ole (tehtävä T25), sano se äläkä väitä tarkistusta tehdyksi.
6. Älä keksi tuloksia, lukuja tai lähteitä, äläkä väitä tavoitteen täyttyneen ilman skriptiä ja tulostiedostoja.
7. Kysy lopuksi, otetaanko ehdotettu tehtävä. Jos otetaan, noudata `CLAUDE.md`:n varausmenettelyä (kohta 4): ensin varaus mainiin omana pienenä commitina, sitten haara.
