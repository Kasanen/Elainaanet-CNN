---
description: Merkitse tehtävä valmiiksi (tila, [x], AI-loki) ja avaa pull request
argument-hint: "[oma nimi], esim. Veijo"
---

Viimeistele käyttäjän nykyinen tehtävä `CLAUDE.md`:n kohtien 7–9 mukaisesti: päivitä `TASKS.md`, kirjaa tekoälyn käyttö omaan lokiin, commitoi, pushaa ja avaa PR. Argumentit: `$ARGUMENTS` (valinnaisesti oma nimi).

Älä yhdistä PR:ää. Käyttäjä yhdistää sen itse. Älä väitä tavoitteen täyttyneen tai tuloksia oikeiksi ilman skriptiä ja tulostiedostoja.

## 1. Tarkistukset (älä jatka, jos jokin ei täyty)
1. Aja `git branch --show-current`. Haaran nimen pitää alkaa tehtävän numerolla (`T07-malli-a`). Jos olet `main`issa tai haara ei ala `Txx-`, pysähdy ja kerro, että `/valmis` ajetaan tehtävähaarassa.
2. Nimi: käytä argumenttia (Elias, Miska, Veijo tai Taif, kirjainkoolla ei väliä), muuten samassa istunnossa jo kerrottua nimeä (esim. `/jatka Veijo`). Kysy vain, jos nimeä ei ole.
3. Lue `TASKS.md`. Tehtävän pitää olla `ottaja: <Nimi>` ja `tila: työn alla`. Jos ottaja on joku muu tai tila on jo `valmis`, pysähdy äläkä muokkaa toisen tehtävää.
4. Aja `git fetch` ja `git status --short`. Kerro, mitä haarassa on muuttunut `main`iin verrattuna (`git diff --stat origin/main...HEAD`). Jos työ on commitoimatta, kysy, commitoidaanko ne ensin samaan haaraan.
5. Kysy käyttäjältä vahvistus: "Onko `<Txx>` valmis ja pystytkö selittämään koodin?" Jatka vasta kun käyttäjä vahvistaa. Muistuta, että `src/data.py`- ja `src/augment.py`-muutokset tarvitsevat toisen jäsenen katselmoinnin.
6. Aja `python scripts/check_project.py`, jos tiedosto on olemassa. Jos se epäonnistuu, kerro tulos ja kysy, jatketaanko. Jos tiedostoa ei ole (T25), sano se äläkä väitä tarkistusta tehdyksi.

## 2. Päivitä tiedostot
1. `TASKS.md`: muokkaa vain tämän tehtävän riviä: `- [ ]` -> `- [x]` ja `tila: työn alla` -> `tila: valmis`. Älä koske muihin riveihin tai numerointiin.
2. Oma AI-loki `logs/<nimi pienillä kirjaimilla>.md` (esim. `logs/veijo.md`): lisää taulukon loppuun rivi sarakkeilla Päivä, Kuka, Tehtävä, Työkalu, Mitä pyydettiin ja Mitä käytettiin ja muutettiin. Jos tässä istunnossa on käytetty tekoälyä tehtävään, kirjaa se tosiasiallisesti: mitä pyydettiin ja mitä käytettiin tai muutettiin. Älä keksi mitään. Jos et tiedä, kysy käyttäjältä. Kirjaa vain käyttäjän omaan lokiin, ei toisen jäsenen lokiin.
3. `PLAN.md`: älä muuta. Jos tehtävä vaatii muutoslokirivin, ehdota sitä käyttäjälle ja kirjaa vasta kun ryhmä on päättänyt.

## 3. Commit, push ja PR
1. Aja `git merge origin/main`. Jos tulee konflikti, ratkaise vain `TASKS.md`:n osalta niin, että kaikkien muiden rivit säilyvät, ja kerro käyttäjälle. Jos et ole varma, pysähdy.
2. Lisää tiedostot nimeltä (ei `git add -A`): `TASKS.md`, oma loki ja tehtävän omat tiedostot, jos ne ovat vielä commitoimatta. Commit-viesti: `Valmis <Txx>: <lyhyt kuvaus>`, ja viimeiselle riville Co-Authored-By-attribuutio.
3. Pushaa: `git push -u origin <haara>`. Jos tunnistautuminen epäonnistuu (https-remote), käytä `git -c credential.helper='!gh auth git-credential' push -u origin <haara>`.
4. Avaa PR: `gh pr create --base main --head <haara>`. Otsikko: `<Txx>: <lyhyt kuvaus>`. Kuvaus: mitä tehtiin, kuka osaa selittää koodin (käyttäjän nimi), tarvitseeko katselmoinnin (`src/data.py`, `src/augment.py`) ja miten tulokset tarkistettiin. Viimeiselle riville `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

## 4. Lopuksi
Kerro lyhyesti suomeksi: PR:n osoite, mitä päivitettiin ja mitä puuttuu. Muistuta:
- Tehtävä ei ole valmis ennen kuin käyttäjä on yhdistänyt PR:n `mainiin`. Muut näkevät sen vasta sitten.
- Yhdistämisen jälkeen: `git switch main`, `git pull`, `git branch -d <haara>`. Sitten `/jatka` ehdottaa seuraavan tehtävän.
- Jos PR vaatii katselmointia, pyydä toista jäsentä (`gh pr create --reviewer` tai GitHubin PR-sivu).
