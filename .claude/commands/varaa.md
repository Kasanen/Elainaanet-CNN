---
description: Varaa tehtävä (esim. /varaa T02) ja luo sille oma haara
argument-hint: "[tehtävän numero] [oma nimi], esim. T02 Veijo"
---

Varaa tehtävä käyttäjälle ja luo sille haara `CLAUDE.md`:n työnkulun kohdan 4 mukaisesti. Argumentit: `$ARGUMENTS`. Ne ovat tehtävän numero ja valinnaisesti oma nimi (esim. `T02 Veijo`). Sanojen järjestyksellä ei ole väliä: `Txx`-muotoinen sana on tehtävä ja Elias, Miska, Veijo tai Taif (kirjainkoolla ei väliä) on nimi.

Tämä on ainoa tilanne, jossa saa pushata suoraan `mainiin`: pelkkä varaus omana pienenä commitina. Kaikki muu työ tehdään haarassa ja viedään PR:llä.

## 1. Tarkistukset (älä jatka, jos jokin ei täyty)
1. Aja `git status --short`. Jos työpuussa on commitoimattomia muutoksia, pysähdy ja pyydä käyttäjää commitoimaan tai tallentamaan ne ensin (stash).
2. Aja `git switch main` ja `git pull`. Jos pull epäonnistuu, kerro virhe äläkä arvaa.
3. Lue `TASKS.md`. Jos argumentti puuttuu, ehdota ylintä vapaata tehtävää, jonka `vaatii`-tehtävät ovat kaikki `valmis`, ja kysy vahvistus ennen jatkamista.
4. Varmista, että tehtävä on olemassa, sen `tila` on `vapaa` ja kaikki sen `vaatii`-tehtävät ovat `valmis`. Jos ei, kerro syy (kuka on ottanut tai mikä vaatimus puuttuu) ja ehdota vaihtoehtoa. Älä muokkaa toisen `työn alla` -tehtävää.
5. Nimi: käytä argumentissa annettua nimeä. Jos sitä ei ole, käytä nimeä, jonka käyttäjä on jo kertonut tässä istunnossa (esim. `/jatka Veijo`). Kysy nimi (Elias, Miska, Veijo tai Taif) vain, jos se ei ilmene kummastakaan. Jos annettu nimi on muu kuin nämä neljä, kysy oikea nimi. Git-käyttäjänimi ei kerro sitä.

## 2. Varaus mainiin
1. Muokkaa `TASKS.md`:ssä vain valitun tehtävän riviä: `ottaja: –` -> `ottaja: <Nimi>` ja `tila: vapaa` -> `tila: työn alla`. Älä koske muihin riveihin, numerointiin tai ruutuun `[ ]`.
2. Commitoi vain `TASKS.md` viestillä `Varaa T02: <Nimi>` (numero ja nimi täytettynä) ja pushaa `mainiin` (`git push origin main`).
3. Jos push hylätään, koska joku ehti ensin: aja `git pull --rebase`, lue tehtävä uudelleen ja tarkista, onko se yhä `vapaa`. Jos joku muu otti sen, peru oma varaus (`git reset --hard origin/main`, vain oman varauscommitin osalta), kerro asia ja ehdota toista tehtävää.
4. Jos push epäonnistuu tunnistautumiseen (https-remote), kokeile `git -c credential.helper='!gh auth git-credential' push origin main`.

## 3. Haara
1. Muodosta haaran nimi: tehtävän numero + 1–3 sanan lyhyt nimi tehtävän kuvauksesta, pienillä kirjaimilla, ilman ääkkösiä ja välilyöntejä (esim. `T07-malli-a`, `T02-data`).
2. Aja `git switch -c <haaran-nimi>` ja `git push -u origin <haaran-nimi>`.

## 4. Raportoi ja ohjaa eteenpäin
Kerro lyhyesti suomeksi: mikä tehtävä varattiin, kenelle, mikä haara luotiin, mitä tehtävä vaatii ja mitä tiedostoja se koskee. Muistuta säännöt: ei datavuotoa, siemen 42, samat foldit, logiikka `src/`:ssä. Muistuta lopuksi, että työ päättyy PR:ään (`gh pr create --base main`), jossa `tila: valmis`, `[x]` ja rivi omaan AI-lokiin (`logs/<nimi>.md`), ja että tehtävä ei ole valmis ennen kuin PR on yhdistetty. Kerro, että `/valmis` tekee nämä ja avaa PR:n. Kirjaa tekoälyn käyttö omaan lokiin heti.

Älä keksi tuloksia tai lukuja. Älä aloita tehtävän varsinaista työtä ennen kuin käyttäjä pyytää.
