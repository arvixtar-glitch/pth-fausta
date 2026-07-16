# ADR-001: Composition Root vieta

**Numeris:** ADR-001
**Data:** 2026-07-16
**Būsena:** Accepted (tik sprendimas, dar neįgyvendintas)
**Autorius:** AI komanda

---

## Santrauka

Komponentų kūrimas ir sujungimas (Composition Root) bus atliktas atskirame `bootstrap.py` modulyje, o ne esamame `Application` klasėje.

---

## Kontekstas

### Problema

Kada projektas augs, bus reikalinga sujungti kelis komponentus:

- `AppState` – programos būsena
- `EventBus` – įvykių sąsaja
- `ServiceContainer` – servisų valdymas
- `NavigationService` – kontrolerių perjungimas
- `MainView` – pagrindinė sąsaja (ateityje)
- `AppController` – pagrindinė valdymo logika (ateityje)

### Dabar

Šiuo metu `Application` klasė:

```python
class Application:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config: AppConfig = config if config is not None else AppConfig()
        self.logger = self.config.logger

    def run(self) -> int:
        self.logger.info(f"Starting...")
        return 0

    def shutdown(self) -> None:
        self.logger.info("Application shutdown completed.")

    def execute(self) -> int:
        try:
            return self.run()
        finally:
            self.shutdown()
```

`Application` valdo tik **gyvavimo ciklą** – paleidimą, veikimą, uždarymo logiką.

### Reikalavimas

Reikalinga vienintelė vieta, kurioje:

1. Sukuriami visi pagrindiniai komponentai
2. Registruojami servisų konteineryje
3. Kurie naudojami per visą programos veikimą

Ši vieta vadinama **Composition Root** arba **Bootstrapper**.

---

## Svarstyti variantai

### Variantas A: Composition Root Application klasėje (`app.py`)

#### Implementacija

```python
class Application:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config if config is not None else AppConfig()
        self.logger = self.config.logger
        
        # Komponentų kūrimas ir sujungimas
        self.container = ServiceContainer()
        self.app_state = AppState()
        self.event_bus = EventBus()
        self.navigation_service = NavigationService()
        
        # Registracija
        self.container.register(AppState, self.app_state)
        self.container.register(EventBus, self.event_bus)
        self.container.register(NavigationService, self.navigation_service)
        
        # MainView ir AppController (ateityje)
        # self.main_view = MainView(...)
        # self.app_controller = AppController(...)

    def run(self) -> int:
        self.logger.info("Starting...")
        # self.app_state.start()
        # self.app_controller.start()
        return 0

    def shutdown(self) -> None:
        # self.app_controller.stop()
        # self.app_state.stop()
        # self.container.clear()
        self.logger.info("Application shutdown completed.")
```

#### Privalumai

- Centralizuota vieta
- Vienkartinis sukūrimas programos pradžioje
- Paprasta supratimas (viša vienoje klasėje)

#### Trūkumai

- ❌ **SRP pažeidimas**: Viena klasė turi **dvi atsakomybes**:
  1. Programos gyvavimo ciklo valdymas
  2. Komponentų kūrimas ir sujungimas
- ❌ **Klasė tampa per didelė** (Fat Class Anti-pattern)
- ❌ **Sunkiau testuoti**: Application priklausotų nuo daugelio komponentų
- ❌ **Importų ciklai**: Gali sukelti `ImportError`
- ❌ **Sunkiau išplėsti**: Naujam komponentui pridėti reikia modifikuoti Application
- ❌ **Neaišku atsakomybių ribos**: Kas yra Application? Gyvavimo valdymas ar konfigūravimas?
- ❌ **Testų bėda**: Kiekvienas Application testas turėtų kurti visus komponentus

### Variantas B: Atskiras Bootstrap modulis (`bootstrap.py`) ✅ **PASIRINKTAS**

#### Implementacija

```python
# src/app/core/bootstrap.py

def create_components(config: AppConfig) -> dict[str, object]:
    """Create and register all application components."""
    
    container = ServiceContainer()
    app_state = AppState()
    event_bus = EventBus()
    navigation_service = NavigationService()
    
    # Registracija
    container.register(AppState, app_state)
    container.register(EventBus, event_bus)
    container.register(NavigationService, navigation_service)
    
    return {
        'container': container,
        'app_state': app_state,
        'event_bus': event_bus,
        'navigation_service': navigation_service,
    }

# src/app/main.py

def main() -> int:
    application = Application()
    
    # Sukuriami komponentai
    components = bootstrap.create_components(application.config)
    
    # Papildomas Application
    application.container = components['container']
    application.app_state = components['app_state']
    
    return application.execute()
```

#### Privalumai

- ✅ **SRP laikymasis**: Dvi skirtingos atsakomybės dvi skirtingose klasėse
  - `Application` – gyvavimo ciklo valdymas
  - `bootstrap` – komponentų kūrimas ir sujungimas
- ✅ **Aiškios atsakomybės**: Kiekvienas modulis žino tik savo darbą
- ✅ **Geriau testuoti**: `bootstrap` gali būti testuojamas atskirai
- ✅ **Geriau išplėsti**: Nauji komponentai pridedami tik `bootstrap.py` failui
- ✅ **Importų tvarka aiški**: `main` → `bootstrap` → `komponentai`
- ✅ **Mažiau klasės dydžio**: Application lieka paprastas (~30 linijų, o ne ~80)
- ✅ **Ateities lankstumo**: Galima turėti `bootstrap_test.py`, `bootstrap_dev.py` skirtingoms situacijoms

#### Trūkumai

- Papildomas failas
- Šiek tiek daugiau kodo
- Reikalingas mažesnis abstraktumas (bet tai yra **išvengiamas**, o ne tikras trūkumas)

---

## Sprendimas

### Pasirinktas variantas

**Variantas B: Atskiras `bootstrap.py` modulis.**

### Konkreti vieta

```
src/app/bootstrap.py
```

### Kodėl ne `src/app/core/bootstrap.py`?

`bootstrap.py` yra **aukščiausio lygio programos surinkimo modulis**, todėl priklauso `src/app` katalogui, o ne `src/app/core`.

Priežastis:
- `app.core` turi būti **nepriklausomas** nuo aukštesnių sluoksnių
- `bootstrap` importuos konkrečius programos komponentus: `AppController`, `MainView`, servisus
- Core moduliai **negrąžina** betokių atgalinių priklausomybių į bootstrap ar aukštesnius sluoksnius
- Tai garantuoja Core stabilumą ir nepriklausomybę

### Priežastys pasirinkti `bootstrap.py` (o ne kitą variantą)

1. **Single Responsibility Principle**
   - `Application` atsako tik už gyvavimo ciklą
   - `bootstrap` atsako tik už komponentų kūrimą
   - Viena atsakomybė → viena priežastis keisti klasę

2. **Testuojamumas**
   - Galima testuoti `bootstrap.create_components()` be Application
   - Galima testuoti Application be konkretaus bootstrap scenarijaus
   - Galima sukurti test-specific bootstrap

3. **Importų priklausomybių valdymas**
   - Aiški priklausomybės kryptis: `main` → `bootstrap` → `komponentai`
   - Atvirkštinės priklausomybės eliminuojamos
   - Importų ciklų rizika mažiau

4. **Plėtojamumas**
   - Nauji komponentai pridedami `bootstrap.py` failui
   - `Application` klasė lieka stabili
   - Ateityje lengvai gali būti `bootstrap_production.py`, `bootstrap_test.py`

5. **Kodo kokybė**
   - Mažesnės klasės dydžio
   - Aiškesnė atsakomybė
   - Lengviau suprasti kodos autoriai (ateityje)

---

## Pasekmės

### Iš karto

- ✅ Kuriant `MainView` ir `AppController` bus kuriamas `bootstrap.py`
- ✅ `Application.__init__()` liks nepakeista šiame etape
- ✅ `main.py` bus iš dalies modifikuota (tik kvietimas į `bootstrap`)

### Ateityje

- ℹ️ Gali būti skirtingi bootstrap failai skirtingoms scenarijoms
- ℹ️ Gali būti `BootstrapFactory` klasė, jei reikalingas dinaminis bootstrap
- ℹ️ Gali būti `bootstrap.py` testiniam aplinkai su mock'ais

### Nesprendžiami klausimai šiame ADR

- ❓ Ar bootstrap turėtų grąžinti tuple ar dict?
- ❓ Ar Application turėtų priimti `components` parametrą ar juos gauti kitu būdu?
- ❓ Kokia bendra konteineryje turėtų būti registruota?

Šie klausimai bus atsakyti, kai bus pradėta integruoti `MainView` ir `AppController`.

---

## Neįtraukta į šį sprendimą

### Šiame ADR nesprendžiamas

- Kaip konkretinai turi veikti `Application.run()` su komponentais
- Kaip `MainView` ir `AppController` bus kuriami ir registruojami
- Kaip klaidų valdymas konkrečiose komponentų uždaryme
- ServiceContainer self-registration tema (tai atskirai dokumentuojama COMPOSITION_ROOT.md)

### Kada bus sprendžiami

Šie klausimai bus sprendžiami **kito žingsnio metu**, kai bus:

1. Kuriamas `MainView`
2. Kuriamas `AppController`
3. Integruojami komponentai į `src/app/bootstrap.py`
4. Atnaujinama `Application.run()` ir `Application.shutdown()` logika

---

## Nuorodos

- 📄 `COMPOSITION_ROOT.md` – detalus planas
- 📄 `CORE_ARCHITECTURE.md` – Core sluoksnio principai
- 📄 `ARCHITECTURE.md` – bendra sistemos architektūra
- 📄 `DECISIONS.md` – architektūrinių sprendimų registras
