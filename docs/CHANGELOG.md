# PTH Fausta - Pakeitimų istorija

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
