# Neuroverkot

Eläinäänten tunnistus konvoluutioverkolla (ESC-50:n 10 eläinluokkaa). Neuroverkkokurssin loppuprojekti 4, ryhmä 2.

Tavoitteet ovat `PLAN.md`:ssä ja tehtävät `TASKS.md`:ssä.

## Näin työskentelemme

0. Aloita Claude-istunto komennolla `/jatka`. Se tarkistaa projektin tilan ja ehdottaa seuraavan tehtävän.
1. `git pull`, lue `TASKS.md` ja valitse vapaa tehtävä, jonka `vaatii`-tehtävät ovat valmiit.
2. Varaa tehtävä: kirjoita nimesi `ottaja`-kenttään, vaihda `tila: työn alla`, commitoi ja pushaa heti mainiin.
3. Tee haara `T07-malli-a` (tehtävän numero + lyhyt nimi) ja tee työ siinä.
4. Tee pull request ja yhdistä se itse. Pyydä toista jäsentä katselmoimaan `src/data.py`- ja `src/augment.py`-muutokset. Samassa PR:ssä päivitetään `TASKS.md` ja AI-loki.
5. Logiikka on `src/`:ssä. Notebookeihin tulee vain ajot ja kuvat. Dataa, malleja ja `.npy`-tiedostoja ei commitoida, vaan ne jaetaan Drivessa.
