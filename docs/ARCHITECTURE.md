# ARCHITECTURE.md

**Projektas:** PTH Fausta
**Dokumentas:** ARCHITECTURE.md
**Versija:** 1.1
**Būsena:** Aktyvus
**Autorius:** Produkto savininkas ir DI komanda
**Sukūrimo data:** 2026-07-14
**Paskutinis atnaujinimas:** 2026-07-17

---

# PTH Fausta – Sistemos architektūra

---

# 1. Paskirtis

Šis dokumentas aprašo projekto techninę architektūrą.

Jo tikslas – apibrėžti sistemos struktūrą, modulių tarpusavio ryšius, sluoksnius ir pagrindinius architektūrinius principus.

Dokumentas aprašo ne planuojamą, o patvirtintą architektūrą.

---

# 2. Projekto tikslas

PTH Fausta yra profesionali darbalaukio programa, skirta dokumentų rengimui ir verslo procesų automatizavimui Lietuvos rinkoje.

Sistema projektuojama taip, kad būtų:

* lengvai plečiama;
* lengvai testuojama;
* aiškios architektūros;
* nepriklausoma nuo konkrečių UI sprendimų.

---

# 3. Architektūros principai

Projektas kuriamas vadovaujantis šiais principais:

* objektinis programavimas (OOP);
* viena atsakomybė kiekvienai klasei;
* sluoksninė architektūra;
* modulinė struktūra;
* mažos tarpusavio priklausomybės;
* dokumentacija vystoma kartu su architektūra.

---

# 4. Naudojamos technologijos

| Sritis                  | Technologija                               |
| ----------------------- | ------------------------------------------ |
| Programavimo kalba      | Python                                     |
| GUI                     | PySide6                                    |
| Duomenų bazė            | SQLite                                     |
| IDE                     | Visual Studio Code                         |
| Programavimo asistentas | Codeium                                    |
| Architektūra            | MVC (gali būti detalinama projekto eigoje) |

Jeigu ateityje bus keičiama technologija, pakeitimas registruojamas `DECISIONS.md`.

---

# 5. Projekto katalogų struktūra

```text
project_root/

├── docs/
├── src/
├── database/
├── resources/
├── tests/
├── README.md
├── pyproject.toml
└── .gitignore
```

Detalus katalogų aprašymas bus pildomas augant projektui.

---

# 6. Loginiai sluoksniai

Sistema skirstoma į loginius sluoksnius:

```text
Naudotojas
      │
      ▼
Grafinė sąsaja (GUI)
      │
      ▼
Valdymo sluoksnis
      │
      ▼
Verslo logika
      │
      ▼
Duomenų prieigos sluoksnis
      │
      ▼
Duomenų bazė
```

Kiekvienas sluoksnis atsako tik už savo funkcijas.

---

# 7. Priklausomybių taisyklės

Sluoksnių priklausomybės gali būti nukreiptos tik žemyn:

```text
View → Controller → Service → Repository → Persistence
```

Leidžiamos priklausomybės:

* Controller gali naudoti Service;
* Service gali naudoti Repository;
* Repository ateityje galės naudoti patvirtintą persistence infrastruktūrą;
* priklausomybės konkretiems komponentams perduodamos per konstruktorius;
* Composition Root gali importuoti ir sujungti visų sluoksnių konkrečius komponentus.

Draudžiamos priklausomybės:

* Repository negali importuoti Controller, Service, View, NavigationService ar Qt;
* Service negali importuoti Controller, View ar Qt;
* Controller negali tiesiogiai importuoti Repository;
* Model negali importuoti View ar Qt;
* View negali importuoti Repository;
* žemesnis sluoksnis negali importuoti aukštesnio sluoksnio.

Controller su duomenų prieiga dirba tik per Service sluoksnį. Verslo logika
priklauso Service, o ne Controller, View ar Repository sluoksniui. Qt ir PySide6
naudojami tik UI bei tam skirtoje infrastruktūroje.

---

# 8. Modulių organizavimo principai

Kiekvienas funkcionalumas kuriamas kaip atskiras modulis.

Modulis turi turėti:

* aiškią paskirtį;
* aiškias viešas sąsajas;
* kuo mažiau priklausomybių.

Modulių sąveika vyksta tik per aiškiai apibrėžtas sąsajas.

---

# 9. Duomenų srautas

Bendras duomenų judėjimo principas:

```text
Naudotojas

      │

      ▼

GUI

      │

      ▼

Controller

      │

      ▼

Business Service

      │

      ▼

Repository

      │

      ▼

SQLite
```

Šis modelis taikomas visiems projekto moduliams.

---

# 10. Testavimo principai

Verslo logika projektuojama taip, kad ją būtų galima testuoti nepriklausomai nuo GUI.

Grafinė sąsaja neturi turėti verslo logikos.

Architektūriniai testai rekursyviai analizuoja visų Repository, Service,
Controller, Model ir View modulių importus. Todėl tos pačios priklausomybių
taisyklės automatiškai taikomos ir ateityje sukurtiems šių sluoksnių moduliams.
Testai turi pateikti pažeidimą sukėlusį failą ir importą, kad sluoksnių ribų
pažeidimai būtų aptikti dar prieš integruojant pakeitimą.

---

# 11. Klaidų valdymas

Klaidos tvarkomos kuo arčiau jų atsiradimo vietos.

Naudotojui rodoma tik jam suprantama informacija.

Techninė informacija registruojama naudojant `logging`.

---

# 12. Logging

Projektas naudoja centralizuotą žurnalų registravimą.

Diagnostinė informacija nerašoma naudojant `print()`.

---

# 13. Architektūriniai apribojimai

Draudžiama:

* apeiti architektūros sluoksnius;
* dubliuoti verslo logiką;
* kurti tarpusavyje cikliškai priklausomus modulius;
* tiesiogiai pasiekti duomenų bazę iš GUI.

---

# 14. Dokumento vystymas

Šis dokumentas yra gyvas.

Jis papildomas tik tada, kai:

* atsiranda naujas modulis;
* pasikeičia architektūra;
* priimamas naujas ilgalaikis techninis sprendimas.

Kasdieniai programavimo darbai šiame dokumente nefiksuojami.

---

# 15. Versijų istorija

| Versija | Data       | Pakeitimai                                           |
| ------- | ---------- | ---------------------------------------------------- |
| 1.1     | 2026-07-17 | Formalizuotos sluoksnių priklausomybės ir jų testai. |
| 1.0     | 2026-07-14 | Sukurtas pradinis sistemos architektūros dokumentas. |
