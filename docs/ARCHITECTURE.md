# ARCHITECTURE.md

**Projektas:** PTH Fausta
**Dokumentas:** ARCHITECTURE.md
**Versija:** 1.7
**Būsena:** Aktyvus
**Autorius:** Produkto savininkas ir DI komanda
**Sukūrimo data:** 2026-07-14
**Paskutinis atnaujinimas:** 2026-07-18

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

Pirmasis pilnas vertikalus pjūvis yra įmonės profilio modulis:

```text
CompanyView → CompanyController → CompanyService → CompanyRepository
            → SessionFactory → SQLAlchemy ORM → SQLite
```

`CompanyService` valdo įmonės profilio ir vienos numatytosios banko sąskaitos
verslo taisykles. `CompanyRepository` valdo tik CRUD ir transakcijų užbaigimą.
Modulis sujungiamas `bootstrap.py`, registruojamas `ServiceContainer`, o jo
langas pasiekiamas per `Nustatymai → Įmonė`.

Šis modelis taikomas visiems projekto moduliams.

Antrasis pilnas vertikalus pjūvis yra klientų modulis:

```text
CustomerListView / CustomerDialog → CustomerController → CustomerService
    → CustomerRepository → SessionFactory → SQLAlchemy ORM → SQLite
```

`CustomerService` yra vienintelė klientų validacijos, dublikatų kontrolės,
paieškos, filtravimo ir rūšiavimo verslo taisyklių vieta. Sąrašo View yra
įterpiamas į pagrindinio lango `QStackedWidget`, o kortelės redagavimas vyksta
modaliniame dialoge. Modulis sujungiamas `bootstrap.py`, registruojamas
`ServiceContainer` ir pasiekiamas per sidebar punktą „Klientai“.

Trečiasis pilnas vertikalus pjūvis yra prekių ir paslaugų modulis:

```text
ProductListView / ProductDialog → ProductController → ProductService
    → ProductRepository → SessionFactory → SQLAlchemy ORM → SQLite
```

`Product` yra vienas aggregate prekėms ir paslaugoms. Jis atominiu būdu valdo
kainodarą ir kelis barkodus, o kategorijos bei matavimo vienetai saugomi
kontroliuojamuose žodynuose. `CompanyService.is_vat_payer()` centralizuoja
laikiną įmonės PVM režimo nustatymą. Sąrašo View įterptas į gyvą pagrindinio
lango `QStackedWidget`; sidebar navigacija nestabdo `AppController` ir
neuždaro `MainView`.

---

# 10. Testavimo principai

Verslo logika projektuojama taip, kad ją būtų galima testuoti nepriklausomai nuo GUI.

Grafinė sąsaja neturi turėti verslo logikos.

Architektūriniai testai rekursyviai analizuoja visų Repository, Service,
Controller, Model, View ir Persistence modulių importus. Todėl tos pačios priklausomybių
taisyklės automatiškai taikomos ir ateityje sukurtiems šių sluoksnių moduliams.
Testai turi pateikti pažeidimą sukėlusį failą ir importą, kad sluoksnių ribų
pažeidimai būtų aptikti dar prieš integruojant pakeitimą.

Persistence konfigūracijos pagrindas yra `app.persistence` pakete. Jis aprašo
SQLite DB failo bei susijusių katalogų vietas. `DatabaseEngine` valdo vieno
SQLAlchemy engine sukūrimą ir pooled ryšių atlaisvinimą, o `SessionFactory`
kuria naujas, tarpusavyje nedalijamas sesijas. Vienos `Session` negalima dalyti
tarp gijų. Minimalus ORM pagrindas ir įmonės profilio lentelės jau sukurtos,
o persistence komponentai prijungti prie Composition Root. Migracijos ir
bendra transakcijų politika dar nesukurtos. Detalesnės taisyklės aprašytos
`DATABASE.md`.

## UI dizaino sistema

`UI_GUIDELINES.md` yra privalomas vizualinių ir UI elgsenos sprendimų šaltinis
visiems naujiems ekranams. Centralizuoti dizaino žetonai laikomi
`app.ui.theme`, o bendras QSS generuojamas `app.ui.styles`. View klasės gali
valdyti tik pateikimą, prieinamumą ir vizualines būsenas; verslo taisyklės
lieka Service sluoksnyje.

Kortelės tipo dialogai dalijasi `DirtyStateTracker`, kuris lygina dabartines
formos reikšmes su paskutine išsaugota kopija, ir `GuardedDialog`, kuris lango
uždarymą bei Esc nukreipia per vieną dirty-state patvirtinimo kelią. Vertikaliai
pažymėtiems laukams naudojamas bendras `form_field` komponentas. Šie
komponentai skirti ir būsimiems Product, Supplier, User bei kitiems moduliams.

Pakartotinai naudojami Qt komponentai laikomi `app.ui.shared` pakete.
`BaseListView` apibrėžia vienodą modulio sąrašo karkasą: antraštę, CRUD
veiksmus, momentinę paiešką, filtrus, lentelę, loading ir empty būsenas bei
įrašų skaičiaus juostą. `CustomerListView` ir `ProductListView` paveldi šį
karkasą ir pateikia tik domenui būdingus stulpelius, tekstus bei signalus.

`CrudToolbar`, `FilterBar`, `ActionTable`, `EmptyStateWidget`,
`LoadingStateWidget` ir `StatusBarWidget` naudojami per `BaseListView` arba
tiesiogiai, kai ekranas turi tą pačią elgseną. `CardDialogShell` suvienodina
Customer ir Product kortelių antraštę, skirtukus bei veiksmų juostą, bet
nekeičia `DirtyStateTracker` ir `GuardedDialog`. `form_field` yra vienintelis
Company, Customer ir Product vertikaliai pažymėtų laukų šaltinis.

Bendri komponentai kuriami tik tada, kai juos realiai naudoja bent du moduliai.
Domeno tekstai, lentelės duomenų atvaizdavimas ir validacijos lieka konkretaus
modulio View arba Service atsakomybėse; shared paketas neturi verslo logikos.

Pagrindinį langą sudaro viršutinė juosta, suskleidžiama sidebar navigacija,
`QStackedWidget` darbo sritis ir DB būsenos bei versijos juosta. Darbo srityje
aktyvūs pradinis puslapis, klientų ir prekių bei paslaugų sąrašai; įmonės
rekvizitai atidaromi kaip nustatymų langas.

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
| 1.7     | 2026-07-19 | Dokumentuota `app.ui.shared` biblioteka, `BaseListView` ir bendrų komponentų naudojimo taisyklės. |
| 1.6     | 2026-07-19 | Dokumentuotas Product vertikalus pjūvis, aggregate ir PVM režimo sąveika. |
| 1.5     | 2026-07-18 | Dokumentuotas klientų modulis ir bendri formų komponentai. |
| 1.3     | 2026-07-17 | Dokumentuoti SQLAlchemy engine ir sesijų komponentai. |
| 1.2     | 2026-07-17 | Dokumentuotas persistence konfigūracijos pagrindas.  |
| 1.1     | 2026-07-17 | Formalizuotos sluoksnių priklausomybės ir jų testai. |
| 1.0     | 2026-07-14 | Sukurtas pradinis sistemos architektūros dokumentas. |
