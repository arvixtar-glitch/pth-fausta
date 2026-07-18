# PTH Fausta - Pakeitimų istorija

## Nepaskelbta

### Pridėta

#### Customer Module

* Pataisyta Task 6.0C navigacijos regresija: sidebar darbo srities perėjimai
  nebenaudoja programos lygio `NavigationService`, todėl `AppController` ir
  `MainView` lieka aktyvūs pereinant tarp Pradžios ir Klientų puslapių.
* Užbaigta Task 6.0B – įgyvendintas pilnas klientų modulio vertikalus pjūvis.
* Pridėta `clients` ORM schema, `CustomerRepository`, `CustomerService` ir
  `CustomerController` su CRUD, validacija, dublikatų kontrole, momentine
  paieška, bendrais filtrais ir rūšiavimu.
* Įgyvendinti `CustomerListView` ir modalinis `CustomerDialog` pagal
  `CUSTOMER_MODULE_UI.md` v1.1: tabs, loading, empty, filtered-empty,
  dirty-state, klaviatūros ir šalinimo scenarijai.
* Klientų darbo sritis prijungta prie sidebar, `NavigationService`,
  Composition Root ir `ServiceContainer`.
* Išskirti bendri `DirtyStateTracker`, `GuardedDialog` ir `form_field`
  komponentai, naudojami kliento ir įmonės formose.
* Pridėti persistence, repository, service, controller, UI, navigacijos,
  paieškos, filtrų ir būsenų testai.

#### UI Foundation

* Užbaigta Task 5.3A UI bazė pagal privalomą `UI_GUIDELINES.md`.
* Pridėti centralizuoti dizaino žetonai ir bendra šviesios temos QSS sistema.
* Pagrindiniame lange įgyvendinta suskleidžiama sidebar navigacija, darbo
  sritis, pradinis puslapis ir DB bei versijos būsenos juosta.
* Įmonės rekvizitų langas suskirstytas į logines grupes, pridėta fiksuota
  veiksmų juosta, dirty būsena, atkūrimas, validacijos ir sąskaitų empty būsena.
* Pridėti MainView, HomeView, CompanyView, sidebar, navigacijos ir temos testai.

#### Company Profile

* Užbaigtas Task 5.3 – sukurtas pilnas įmonės profilio vertikalus pjūvis.
* Pridėti `companies` ir `company_bank_accounts` ORM modeliai bei jų ryšys.
* Sukurti `CompanyRepository`, `CompanyService` ir `CompanyController`.
* Įgyvendinta vienos numatytosios banko sąskaitos taisyklė.
* Pridėtas laikinas funkcinis „Įmonės nustatymų“ langas su dviem skirtukais.
* Modulis prijungtas prie Composition Root, `ServiceContainer` ir navigacijos.
* Pridėti ORM, CRUD, verslo taisyklių, kontrolerio ir integracijos testai.

#### Persistence Foundation

* Pradėtas 5 etapas – Persistence Foundation.
* Sukurtas `app.persistence` paketas ir nekintamas `DatabaseConfig` objektas.
* Apibrėžta numatytoji `data/` katalogų struktūra ir SQLite URL generavimas.
* Katalogai kuriami tik aiškiai iškvietus `ensure_directories()`; DB failas
  nekuriamas.
* Pridėti konfigūracijos validacijos, failų sistemos ir Windows kelių testai.
* Architektūrinė priklausomybių patikra išplėsta persistence sluoksniui.
* Sukurtas `DATABASE.md` su patvirtinta būsimos DB schemos kryptimi.
* SQLAlchemy priklausomybė apribota iki palaikomos 2.x versijos.
* Sukurtas `DatabaseEngine` su SQLite `check_same_thread=False`, kiekvieno
  ryšio `foreign_keys=ON` aktyvavimu ir aiškiu `dispose()` metodu.
* Sukurtas `SessionFactory`, grąžinantis naujas sesijas su `autoflush=False` ir
  `expire_on_commit=False`, bet automatiškai nevaldantis verslo transakcijų.
* Pridėti engine, sesijų ir visos persistence infrastruktūros grandinės testai.
* Papildyta SQLAlchemy ryšių, sesijų ir gijų naudojimo dokumentacija.

#### Business Layer Foundation

* Pradėtas 4 etapas – Business Layer Foundation.
* Sukurta minimali bazinė `BaseService` klasė būsimiems verslo servisams.
* `BaseService` eksportuota per `app.services` paketą.
* Pridėti bazinės servisų klasės architektūrinių ribų testai.
* Užbaigtas Task 4.2 – sukurtas minimalus `BaseRepository` pagrindas.
* `BaseRepository` sukurta be SQLite, SQLAlchemy ir kitų persistence technologijų.
* Bazinė klasė sąmoningai neturi bendrų CRUD metodų.
* Užbaigtas Task 4.3 – formalizuotos sluoksnių priklausomybių taisyklės.
* Pridėti rekursyviniai architektūriniai testai, automatiškai tikrinantys ir
  būsimus Repository, Service, Controller, Model bei View modulius.
* `NavigationService` priklausomybė nuo konkretaus kontrolerio pakeista į
  neutralią Core `ControllerPort` sąsają.
* Konkreti persistence infrastruktūra bus kuriama vėlesniame etape.

## v0.1.3 (2026-07-16)

### Pridėta

* Sukurtas `src/app/bootstrap.py` ir įgyvendintas Composition Root.
* Prijungtos vienintelė `QApplication` ir `QtEventLoop` instancijos.
* Sukurti, sujungti ir konteineryje registruoti pagrindiniai programos komponentai.
* `main.py` prijungtas prie Composition Root.
* Pridėti Composition Root testai.

### Patikrinimas

* Visas testų rinkinys praeina: 185 testai ir 8 subtestai.
* `ruff check .` ir `git diff --check` praeina be klaidų.

## v0.1.2 (2026-07-16)

### Pridėta

#### AppState

* Pridėtas `AppState` bendros programos būsenos valdymui.
* Pridėtas programos veikimo būsenos valdymas (`start()`, `stop()`).
* Pridėtas aktyvaus naudotojo būsenos valdymas (`set_current_user()`, `clear_current_user()`).
* Pridėtas aktyvaus dokumento būsenos valdymas (`set_active_document()`, `clear_active_document()`).
* Pridėtas neišsaugotų pakeitimų žymėjimas (`mark_unsaved_changes()`, `mark_changes_saved()`).
* Pridėta `reset()` metoda visai būsenai atkurti.
* Sukurti `AppState` vienetiniai testai (42 testai).
* Atnaujinti `app.core` paketų eksportai `AppState` įtraukimui.

#### Composition Root planas

* Pridėtas `COMPOSITION_ROOT.md` detalus komponentų sujungimo planas.
* Sukurtas ADR-001 su Composition Root vietos sprendimu.
* Aprašyta dabartinė programos paleidimo seka.
* Aprašyta planuojama komponentų kūrimo ir registravimo seka.
* Aprašyta programos paleidimo ir uždarymo seka su išimčių valdymu.
* Dokumentuotos leidžiamos ir draudžiamos priklausomybės.
* Sprendimas: Composition Root bus atskirame `src/app/bootstrap.py` modulyje (dar neįgyvendintas).
* Patikslinta: `bootstrap.py` vieta yra `src/app/`, ne `src/app/core/`, nes tai aukščiausio lygio programos surinkimas, ne Core infrastruktūra.

### Patikrinimas

* Patikrintas `AppState` elgesys naudojant `pytest` (179 testų iš viso).
* Projektas toliau veikia be pakeitimų.

## v0.1.1 (2026-07-15)

### Pridėta

#### MVC pagrindas

* Sukurtos bazinės MVC klasės: `BaseModel`, `BaseView` ir `BaseController`.
* Pridėti minimalūs paketų eksportai `app.models`, `app.views` ir `app.controllers`.
* Sukurti vienetiniai testai bazinėms MVC klasėms.

#### EventBus

* Pridėtas sinchroninis `EventBus` prenumeravimui, atsisakymui, publikavimui ir prenumeratų valymui.
* Sukurti `EventBus` vienetiniai testai.

#### AppController

* Pridėtas aukščiausio lygio `AppController` su idempotentišku `start()` ir `stop()` valdymu.
* Sukurti `AppController` vienetiniai testai.

#### NavigationService

* Pridėtas `NavigationService` aktyvaus kontrolerio perjungimui.
* Įdiegtas saugus kontrolerių paleidimo ir sustabdymo eiliškumas.
* Sukurti `NavigationService` vienetiniai testai.

#### ServiceContainer

* Pridėtas `ServiceContainer` servisų registravimui, gavimui, pakeitimui ir pašalinimui pagal tipą.
* Pridėta `ServiceNotRegisteredError` kaip aiškus klaidos tipas nerastam servisui.
* Sukurti `ServiceContainer` vienetiniai testai.

### Patikrinimas

* Patikrintas bazinių MVC klasių ir `EventBus` elgesys naudojant `pytest`.

## v0.1.0 (2026-07-14)

### Pridėta

#### Programos branduolys (Core)

* Sukurtas centralizuotas projekto katalogų valdymo modulis (`paths.py`).
* Sukurta centralizuota žurnalavimo (logging) sistema (`logger.py`).
* Sukurtas programos nustatymų valdymo modulis su atominiu JSON išsaugojimu (`settings.py`).
* Sukurtas centrinis branduolio konfigūracijos modulis (`config.py`).
* Sukurtas programos versijos valdymo modulis (`version.py`).
* Sukurta programos gyvavimo ciklo klasė (`app.py`).
* Sukurtas pagrindinis programos paleidimo taškas (`main.py`).

#### Testavimas

* Sukurti vienetiniai testai visiems Core moduliams.
* Sukurtas bendras Core testų rinkinys.
* Sėkmingai praeina visi **42** vienetiniai testai.

#### Architektūra

* Užbaigtas ir patvirtintas Programos branduolio (Core) architektūros etapas.
* Atlikta pilna branduolio architektūros peržiūra.
* Atliktas branduolio auditas.
* Patvirtinta programos paleidimo grandinė.

#### Dokumentacija

* Sukurtas dokumentas `CORE_ARCHITECTURE.md`.
* Papildyta projekto dokumentacija.
* Įvesta dokumentacijos atnaujinimo tvarka po kiekvieno užbaigto kūrimo etapo.

## v0.0.2 (2026-07-13)

### Pridėta
- Sutvarkyta projekto katalogų struktūra.
- Sukurtas docs katalogas.
- Sukurtas README.md.
- Sukurtas .gitignore.
- Sukurtas pyproject.toml.

---

## v0.0.1 (2026-07-13)

### Pridėta
- Sukurtas Python projekto karkasas.
- Sukurta virtuali aplinka (.venv).
- Sukurtas pagrindinis katalogų medis.
- Sukurtas main.py.
- Programa sėkmingai paleidžiama.
