# Liite: Tekoälyn käyttö

Tämä liite on koottu ryhmän jäsenten AI-lokeista (`logs/*.md`) komennolla `python scripts/ai_appendix.py`. Rivit ovat lokien rivit sellaisinaan. Älä muokkaa tätä tiedostoa käsin: korjaa oma lokisi ja aja komento uudelleen.

## Yhteenveto

| Jäsen | Kirjauksia | Aikaväli |
| --- | --- | --- |
| Elias | 2 | 25.11.2026–25.11.2026 |
| Miska | 11 | 26.11.2026–27.11.2026 |
| Taif | 0 | – |
| Veijo | 7 | 24.11.2026–27.11.2026 |
| **Yhteensä** | **20** | |

**Työkalut (kuten lokeihin kirjattu):** Claude (Opus 5.5) (11), Claude Code (9)

**Tehtävät, joissa tekoälyä käytettiin:**

| Tehtävä | Jäsenet |
| --- | --- |
| T01 | Elias, Veijo |
| T02 | Miska |
| T06 | Miska |
| T09 | Miska |
| T22 | Miska |
| T25 | Miska |
| muu (ei T-numeroa) | Veijo |

## Elias

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 25.11.2026 | Elias | T01 (työnkulku ja varaus) | Claude Code | Selitä miten `/jatka`, `/varaa` ja `/valmis` toimivat ja ohjaa alkuun; varaa T01 komennolla `/varaa T01 elias` | Käytettiin selitystä työnkulusta. Claude varasi T01:n (`TASKS.md`, push mainiin) ja loi haaran `T01-repo` |
| 25.11.2026 | Elias | T01 | Claude Code | Tee T01 kokonaan | Claude loi `.gitignore`n, `requirements.txt`:n (alarajat, ei tarkkoja versioita), kansiot `src/` (tyhjät moduulipohjat), `notebooks/`, `results/`, `scripts/` ja README:n kansiorakenne-, asennus- ja Drive-osiot. Drive-kansio ja kirjoitusoikeudet tehdään käsin |

## Miska

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 26.11.2026 | Miska | T25 | Claude (Opus 5.5) | Ehdota `scripts/check_project.py`:n rakenne ja kirjoita koodi | Claude ehdotti rakenteen (tehtävät, tulostiedostot, tavoitteet, palautettavat). Miska päätti, että kynnykset luetaan `PLAN.md`:stä ja että raportti on kansiossa `report/` ja demo tiedostossa `demo/app.py`. Claude kirjoitti skriptin (vain standardikirjasto) ja testasi sen oikealla repolla ja keksityillä tulostiedostoilla: virheelliset tiedostot (rikki JSON, puuttuvat kentät, väärä siemen, puolikas foldi, käsin muutettu accuracy) tunnistetaan, makro-F1 vastaa scikit-learnia, ja tavoitteet arvioidaan vain, kun 5/5 foldia on olemassa. |
| 26.11.2026 | Miska | T25 | Claude (Opus 5.5) | Selitä `scripts/check_project.py` riveittäin ja `/valmis` | Claude selitti koko skriptin osio kerrallaan. Miska vahvisti, että tehtävä on valmis ja että hän osaa selittää koodin. Claude ajoi skriptin (paluukoodi 0, ei virheitä, 27 puuttuvaa tai avointa kohtaa, koska tuloksia ei vielä ole), päivitti `TASKS.md`:n (T25 `[x]`, `tila: valmis`) ja avasi PR:n. |
| 26.11.2026 | Miska | T06 | Claude (Opus 5.5) | Ehdota `src/train.py`:n rakenne ja kirjoita koodi | Claude ehdotti rakenteen (`set_seed`, `make_callbacks`, `train_model`, `evaluate`, `save_results`), ja Miska päätti, että callbackit seuraavat `val_loss`:ia ja CSV-lokit tallennetaan `results/history/`-kansioon. Claude kirjoitti koodin ja ajoi savutestin satunnaisdatalla (TF 2.22.0-rc1 / Keras 3.16 dev, ei Colabin versio): tiedostot syntyvät, JSON-kentät vastaavat `PLAN.md`:tä, one-hot-tunnisteet muuttuvat luokkanumeroiksi, ja parhaat painot palautuvat sekä aikaisessa pysähtymisessä että ilman sitä. |
| 26.11.2026 | Miska | T06 | Claude (Opus 5.5) | Selitä `src/train.py` riveittäin ja korjaa läpikäynnissä löytyneet kohdat | Claude selitti koko tiedoston ja korjasi kolme kohtaa: ModelCheckpoint tallentaa aina vakionimellä `models/{malli}_fold{k}.keras` (`stage` vaikuttaa vain CSV-lokin nimeen), `make_callbacks(save_files=False)` KerasTuneria (T11) varten ja `(x, y)`-pari kelpaa myös listana. Claude korjasi myös oman aiemman väärän väitteensä, että KerasTuner kutsuisi `train_model`:ia. Testattu satunnaisdatalla: C2:n kaksi vaihetta tuottavat yhden `.keras`-tiedoston ja kaksi CSV:tä, ja aiemmat savutestit menevät edelleen läpi. |
| 26.11.2026 | Miska | T06 | Claude (Opus 5.5) | `/valmis`: merkitse T06 valmiiksi ja avaa PR | Claude päivitti `TASKS.md`:n (T06 `[x]`, `tila: valmis`), lisäsi tämän rivin, commitoi ja avasi PR:n. Miska vahvisti, että tehtävä on valmis ja että hän osaa selittää koodin. |
| 26.11.2026 | Miska | T02 | Claude (Opus 5.5) | Tee T02: lataa ESC-50, suodata eläinluokat ja tarkista 400 leikettä | Claude kirjoitti `src/data.py`:hen funktiot `download_esc50`, `load_metadata` ja `check_dataset`, skriptin `scripts/download_esc50.py` ja README:n Data-osion. Testattu: 400 leikettä, 40 per luokka, 8 per luokka per foldi, kaikki 5 s / 44,1 kHz / mono; tarkistus huomaa puuttuvan rivin ja väärän foldin. |
| 27.11.2026 | Miska | T09 | Claude (Opus 5.5) | Ehdota T09:n rakenne ja kirjoita koodi | Claude ehdotti rakenteen, ja Miska hyväksyi: uusi moduuli `src/yamnet.py` (ei `src/data.py`:n konfliktia #18/#19:n kanssa), kehyskohtaiset upotukset ja notebook `notebooks/T09_yamnet.ipynb`. Claude kirjoitti `load_wave_16k`, `load_yamnet` (`hub.load`), `embed` ja `build_yamnet_cache`. Testattu oikealla ESC-50-datalla ja oikealla YAMNet-mallilla (ladattu `tf.saved_model.load`:lla, koska `tensorflow_hub` ei toimi tämän koneen TF 2.22-rc:n kanssa; `hub.load` testataan Colabissa): upotukset (400, 10, 1024), 16,4 Mt, ei NaN-arvoja, välimuisti luetaan uudelleen ja väärä järjestys kaatuu. Järkevyystesti: YAMNetin oma tunniste vastaa eläintä (esim. frog -> Frog, crow -> Crow, sheep -> Sheep, insects -> Insect); "Silence" on yleinen, koska leikkeissä on hiljaisuutta. Ei C1:n tulos. |
| 27.11.2026 | Miska | T09 | Claude (Opus 5.5) | `/valmis`: merkitse T09 valmiiksi ja avaa PR | Claude päivitti `TASKS.md`:n (T09 `[x]`, `tila: valmis`), lisäsi tämän rivin, ajoi `scripts/check_project.py`:n (ei virheitä) ja avasi PR:n. Miska vahvisti, että tehtävä on valmis ja että hän osaa selittää koodin. `hub.load` (Colab) on vielä ajamatta; kirjattu PR:ään. |
| 27.11.2026 | Miska | T09 | Claude (Opus 5.5) | Selitä `src/yamnet.py` riveittäin ja lisää `EMBED_DIM`-tarkistus | Claude selitti koko moduulin ja huomasi, ettei `EMBED_DIM`-vakiota käytetty. Miskan pyynnöstä `build_yamnet_cache` nostaa nyt `ValueError`in, jos upotuksen koko ei ole 1024, eikä silloin tallenna välimuistia. Testattu: valemalli (512) kaatuu, eikä välimuistia synny; oikea YAMNet (20 leikettä) antaa (20, 10, 1024). |
| 27.11.2026 | Miska | T09 | Claude (Opus 5.5) | Yhdistä PR #20, Colab-ajo tehty | Miska ajoi `notebooks/T09_yamnet.ipynb`:n Colabissa (`hub.load`) ja ilmoitti sen onnistuneen; Claude ei nähnyt ajon tulostetta. Claude lisäsi tämän rivin, kommentoi PR:ään ja yhdisti PR #20:n Miskan pyynnöstä. |
| 27.11.2026 | Miska | T22 | Claude (Opus 5.5) | Ehdota T22:n rakenne ja kirjoita koodi | Claude ehdotti rakenteen, ja Miska hyväksyi: koontiskripti `scripts/ai_appendix.py` (vain standardikirjasto, ei muokkaa lokeja), liite tiedostoon `report/liitteet/ai_kaytto.md` (alikansio, jotta `check_project.py` ei pidä liitettä raporttina), jäsenkohtaiset taulukot ja `--check`-tila T24:ää varten. Testattu keksityillä lokeilla: väärä nimi, väärä sarakemäärä, virheellinen päivämäärä, `\|` tekstissä, lopun ` \| ` puuttuu ja `--check` (0 ajan tasalla, 1 uuden rivin jälkeen). Ensimmäinen versio tulkitsi Veijon lokin rivin, josta puuttui lopun ` \| `, väärin; jäsennin korjattiin. Liite generoitu mainin lokeista (19 riviä). |

## Taif

Ei kirjauksia.

## Veijo

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 24.11.2026 | Veijo | Dokumentaation tarkistus | Claude Code | Vertaa CLAUDE.md, PLAN.md, TASKS.md ja INSTRUCTIONS-short.md tehtävänantoon ja korjaa 7 löydettyä puutetta | Käytettiin tarkistuksen tuloksia. Lisättiin validointifoldi, C1-poikkeus, T25, T17/T20/T21 muutokset ja raportin osiot. Ryhmän pitää tarkistaa muutokset |
| 24.11.2026 | Veijo | Yhteistyöpohja | Claude Code | Arvioi, toimiiko dokumentaatio neljän hengen työssä ja arvosanatavoitteessa 5 | Käytettiin ehdotuksia: git-työnkulku (varaus, haara, PR), istuntosäännöt, notebook-säännöt, arvosana 5 -tarkistuslista `PLAN.md`:ssä, README. Ryhmän pitää tarkistaa |
| 24.11.2026 | Veijo | Nykytilan jakaminen | Claude Code | Tee projektista sellainen, että muut jäsenet voivat jatkaa siitä mihin jäätiin | Siirrettiin tehtävänanto-tiedostot `temp/` -> `private/`, päivitettiin T01:n maininta ja avattiin PR. Tehtäviin ei koskettu |
| 25.11.2026 | Veijo | `/jatka`-komento | Claude Code | Tee komento, jolla Claude tarkistaa projektin ja varmistaa, missä tehtävässä edetään | Käytettiin `.claude/commands/jatka.md` sellaisenaan ja lisättiin maininta README:hen. Ryhmän pitää kokeilla komentoa |
| 25.11.2026 | Veijo | `/varaa`-komento | Claude Code | Automatisoi tehtävän varaus ja haaran luonti komennolla | Käytettiin `.claude/commands/varaa.md` ja lisättiin maininta README:hen. Ryhmän pitää kokeilla komentoa ennen kuin siihen luotetaan |
| 25.11.2026 | Veijo | `/valmis`-komento ja henkilökohtaiset lokit | Claude Code | Tee komento tehtävän valmiiksi merkitsemiseen ja anna jokaiselle jäsenelle oma loki `logs/`-kansioon | Käytettiin `.claude/commands/valmis.md` ja `logs/`-kansiota. AI-loki siirrettiin `TASKS.md`:stä henkilökohtaisiin tiedostoihin, ja `CLAUDE.md`, `README.md`, `/jatka` ja `/varaa` päivitettiin viittaamaan niihin. Ryhmän pitää hyväksyä muutos |
| 27.11.2026 | Veijo | Projektin tarkistus (PR-virheet, T01, tehtävänanto vs. PLAN.md) ja TASKS.md:n korjaus | Claude Code | Tarkista PR:t, vertaa tehtävänantoa PLAN.md:hen, tarkista T01, korjaa T01 ja tuplarivit ja kirjaa opettajan hyväksyntä PLAN.md:hen | Käytettiin löydöslistaa ja TASKS.md:n korjausta (PR #15). Opettajan hyväksynnän päivän ja sisällön antoi Veijo, Claude kirjasi sen PLAN.md:hen. Löydökset (mm. "kaksi foldia" -virhe) tarkistetaan ryhmässä |
