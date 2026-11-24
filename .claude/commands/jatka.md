---
description: Kerro mihin projektissa on jääty ja anna konkreettiset ohjeet, miten jatketaan
---

Auta käyttäjää jatkamaan projektia siitä, mihin se jäi. Tämä komento on vain lukeva: älä varaa tehtävää, muokkaa tiedostoja äläkä commitoi, ennen kuin käyttäjä vahvistaa.

## 1. Selvitä tila
1. Aja `git pull`, `git log -10 --oneline`, `git branch --show-current`, `git branch -a` ja `gh pr list`. Jos jokin epäonnistuu, kerro se äläkä arvaa.
2. Lue `CLAUDE.md`, `TASKS.md` ja `PLAN.md`.
3. Kysy käyttäjän nimi (Elias, Miska, Veijo tai Taif), ellei se ilmene. Git-käyttäjänimi ei kerro sitä.

## 2. Kerro mihin on jääty
Raportoi suomeksi tiiviisti:
- **Edistyminen:** montako tehtävää `[x]` kaikista, nykyinen vaihe ja sen takaraja suhteessa tämän päivän päivämäärään.
- **Viimeisin työ:** mitä viimeiset commitit ja yhdistetyt PR:t tekivät, ja mikä tehtävä niistä valmistui.
- **Työn alla:** `työn alla` -tehtävät ja ottajat. Jos käyttäjällä on oma keskeneräinen tehtävä, kerro sen haara ja avoin PR, ja ehdota jatkamaan siitä.
- **Myöhässä tai jumissa:** `työn alla` -tehtävät, joiden takaraja on ohi, ja avoimet PR:t, jotka odottavat yhdistämistä.
- **Tarkistus:** aja `python scripts/check_project.py`, jos tiedosto on olemassa. Jos sitä ei ole (tehtävä T25), sano se äläkä väitä tarkistusta tehdyksi.

## 3. Ehdota seuraava tehtävä
Valitse ylin rivi, jonka `tila` on `vapaa` ja jonka `vaatii`-tehtävät ovat kaikki `valmis`. Jos käyttäjällä on jo keskeneräinen tehtävä, ehdota sitä ensin. Kerro tehtävän numero, kuvaus, takaraja ja mitä se avaa muille.

## 4. Anna ohjeet, miten jatketaan
Kirjoita valitulle tehtävälle valmis lista, jossa komennot on täytetty tehtävän numerolla ja lyhyellä nimellä (esim. `T02-data`):
1. Varaus: kirjoita nimesi `ottaja`-kenttään ja vaihda `tila: työn alla`. Commitoi ja pushaa tämä heti `mainiin` omana pienenä commitina.
2. Haara: `git switch -c T02-data`.
3. Työ: kerro, mitä tehtävä vaatii ja missä tiedostoissa se tehdään (`src/`, notebookit, `results/`).
4. Muistuta säännöt, jotka koskevat tätä tehtävää (ei datavuotoa, siemen 42, samat foldit, tulokset `results/{malli}_fold{k}.json`).
5. Valmis: PR mainiin, jossa `tila: valmis`, `[x]` ja AI-lokirivi. Kerro, tarvitseeko PR katselmoinnin (`src/data.py`, `src/augment.py`).

## 5. Lopuksi
Älä keksi tuloksia, lukuja tai lähteitä, äläkä väitä tavoitteen täyttyneen ilman skriptiä ja tulostiedostoja. Kysy, aloitetaanko ehdotettu tehtävä, ja noudata vasta vastauksen jälkeen varausmenettelyä (`CLAUDE.md` kohta 4).
