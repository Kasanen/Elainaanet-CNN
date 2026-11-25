# AI-loki: Veijo

Kirjaa tähän jokainen tekoälyn käyttökerta heti, kun käytät sitä. Kurssi vaatii tarkan kirjauksen. Tämän tiedoston muokkaa vain Veijo, joten tiedosto ei aiheuta konflikteja muiden kanssa.

| Päivä | Kuka | Tehtävä | Työkalu | Mitä pyydettiin | Mitä käytettiin ja muutettiin |
| --- | --- | --- | --- | --- | --- |
| 24.11.2026 | Veijo | Dokumentaation tarkistus | Claude Code | Vertaa CLAUDE.md, PLAN.md, TASKS.md ja INSTRUCTIONS-short.md tehtävänantoon ja korjaa 7 löydettyä puutetta | Käytettiin tarkistuksen tuloksia. Lisättiin validointifoldi, C1-poikkeus, T25, T17/T20/T21 muutokset ja raportin osiot. Ryhmän pitää tarkistaa muutokset |
| 24.11.2026 | Veijo | Yhteistyöpohja | Claude Code | Arvioi, toimiiko dokumentaatio neljän hengen työssä ja arvosanatavoitteessa 5 | Käytettiin ehdotuksia: git-työnkulku (varaus, haara, PR), istuntosäännöt, notebook-säännöt, arvosana 5 -tarkistuslista `PLAN.md`:ssä, README. Ryhmän pitää tarkistaa |
| 24.11.2026 | Veijo | Nykytilan jakaminen | Claude Code | Tee projektista sellainen, että muut jäsenet voivat jatkaa siitä mihin jäätiin | Siirrettiin tehtävänanto-tiedostot `temp/` -> `private/`, päivitettiin T01:n maininta ja avattiin PR. Tehtäviin ei koskettu |
| 25.11.2026 | Veijo | `/jatka`-komento | Claude Code | Tee komento, jolla Claude tarkistaa projektin ja varmistaa, missä tehtävässä edetään | Käytettiin `.claude/commands/jatka.md` sellaisenaan ja lisättiin maininta README:hen. Ryhmän pitää kokeilla komentoa |
| 25.11.2026 | Veijo | `/varaa`-komento | Claude Code | Automatisoi tehtävän varaus ja haaran luonti komennolla | Käytettiin `.claude/commands/varaa.md` ja lisättiin maininta README:hen. Ryhmän pitää kokeilla komentoa ennen kuin siihen luotetaan |
| 25.11.2026 | Veijo | `/valmis`-komento ja henkilökohtaiset lokit | Claude Code | Tee komento tehtävän valmiiksi merkitsemiseen ja anna jokaiselle jäsenelle oma loki `logs/`-kansioon | Käytettiin `.claude/commands/valmis.md` ja `logs/`-kansiota. AI-loki siirrettiin `TASKS.md`:stä henkilökohtaisiin tiedostoihin, ja `CLAUDE.md`, `README.md`, `/jatka` ja `/varaa` päivitettiin viittaamaan niihin. Ryhmän pitää hyväksyä muutos |
