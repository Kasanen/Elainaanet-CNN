# Neuroverkot

Eläinäänten tunnistus konvoluutioverkolla (ESC-50:n 10 eläinluokkaa). Neuroverkkokurssin loppuprojekti 4, ryhmä 2.

Tavoitteet ovat `PLAN.md`:ssä ja tehtävät `TASKS.md`:ssä.

## Näin työskentelemme

1. Aloita Claude-istunto komennolla `/jatka <nimi>` (esim. `/jatka Veijo`). Se hakee muutokset (`git pull`), kertoo mihin on jääty ja ehdottaa seuraavan tehtävän.
2. Varaa tehtävä komennolla `/varaa T07`. Se kirjoittaa varauksen `TASKS.md`:hen, pushaa sen mainiin ja luo haaran (esim. `T07-malli-a`).
3. Tee työ haarassa.
4. Kun työ on valmis, aja `/valmis`. Se merkitsee tehtävän valmiiksi `TASKS.md`:ään (`tila: valmis`, `[x]`), lisää rivin omaan AI-lokiisi (`logs/<nimi>.md`) ja avaa pull requestin. Yhdistä PR itse. Pyydä toista jäsentä katselmoimaan `src/data.py`- ja `src/augment.py`-muutokset.
5. Logiikka on `src/`:ssä. Notebookeihin tulee vain ajot ja kuvat. Dataa, malleja ja `.npy`-tiedostoja ei commitoida, vaan ne jaetaan Drivessa.

Ilman Claudea: `git pull`, lue `TASKS.md`, varaa tehtävä käsin (`ottaja` ja `tila: työn alla`, commit ja push mainiin) ja tee haara `T07-malli-a`.
