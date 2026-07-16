# Composition Root

**Dokumentas:** COMPOSITION_ROOT.md
**Versija:** 1.0
**Būsena:** Projektavimas
**Data:** 2026-07-16

---

## Paskirtis

Šis dokumentas aprašo Composition Root – vienintelę vieta, kurioje kuriami ir sujungiami pagrindiniai programos komponentai.

Composition Root atsakingas tik už:

- komponentų sukūrimą;
- jų sujungimą;
- registravimą servisų konteineryje.

Composition Root **neatsakingas** už:

- komponentų vidinę logiką;
- gyvavimo ciklo valdymą (tai Application atsakomybė);
- verslo logikos vykdymą.

---

## Dabartinė programos paleidimo seka

Šiuo metu programos paleidimas vyksta šia seka:

```
1. python -m app.main
      ↓
2. main() funkcija iš src/app/main.py
      ↓
3. Application() sukūrimas
      ↓
4. Application.__init__()
      - Sukuria arba priima AppConfig
      - AppConfig inicijuoja:
        - ProjectPaths
        - SettingsManager
        - Loggerio konfigūracija
        - Logger instancija
      ↓
5. Application.execute()
      - Iškviečia run() (try bloke)
      - Iškviečia shutdown() (finally bloke)
      ↓
6. Application.run()
      - Užrašo "Starting..." žinutę
      - Grąžina 0
      ↓
7. Application.shutdown()
      - Užrašo "Application shutdown completed." žinutę
```

**Diagrama:**

```
main.py
  │
  ├─→ Application()
  │     │
  │     ├─→ AppConfig()
  │     │     │
  │     │     ├─→ ProjectPaths
  │     │     ├─→ SettingsManager
  │     │     ├─→ configure_logging()
  │     │     └─→ get_logger()
  │     │
  │     └─→ execute()
  │           │
  │           ├─→ run()
  │           │    └─→ logger.info("Starting...")
  │           │
  │           └─→ shutdown()
  │                └─→ logger.info("Application shutdown completed.")
  │
  └─→ sys.exit()
```

### Šiuo metu kuriami komponentai

- ✅ `ProjectPaths` – projekto katalogų valdymas
- ✅ `Logger` – žurnalavimo sistema
- ✅ `SettingsManager` – nustatymų valdymas
- ✅ `AppConfig` – konfigūracija

### Komponentai, kurie dar nėra sujungti

- ❌ `AppState` – programos būsena (sukurtas, bet nėra naudojamas)
- ❌ `EventBus` – įvykių sąsaja (sukurta, bet nėra naudojama)
- ❌ `ServiceContainer` – servisų valdymas (sukurtas, bet nėra naudojamas)
- ❌ `NavigationService` – kontrolerių perjungimas (sukurtas, bet nėra naudojamas)
- ❌ `MainView` – pagrindinė sąsaja (ateityje)
- ❌ `AppController` – pagrindinė valdymo logika (ateityje)

---

## Pasirinkta Composition Root vieta

### Sprendimas

**Composition Root bus pradiniame `src/app/bootstrap.py` modulyje.**

### Pagrindimas

`bootstrap.py` turi būti **aukščiausio lygio programos surinkimo modulis**, ne žemo lygio Core infrastruktūros komponentas. Jo paskirtis – importuoti ir sujungti konkrečius programos komponentus:

- `Application` (Core)
- `AppState`, `EventBus`, `ServiceContainer`, `NavigationService` (Core)
- `AppController` (verslo logika)
- `MainView` (GUI)
- kitus verslo modulius

Todėl `bootstrap.py` priklauso `app` katalogui, o ne `app/core`, kuris turi likti skirtas bendriesiems, nuo aukštesnių sluoksnių **nepriklausantiems** komponentams.

**Leistina priklausomybių kryptis:**
```
main.py
   ↓
bootstrap.py (aukščiausio lygio programa)
   ↓
Application, AppController, MainView, Services (verslo logika)
   ↓
Core komponentai (Logger, Paths, Settings, etc.)
```

`app.core` **neturi** importuoti konkrečių kontrolerių, View ar programos surinkimo logikos. Tai garantuoja Core nepriklausomybę.

#### Option A: app.py (atmestas)

**Privalumai:**
- Centralizuota vieta

**Trūkumai:**
- `Application` klasė tampa per didelė (fat class)
- Sumaišoma atsakomybė: `Application` **valdo gyvavimo ciklą** ir **kuria komponentus**
- Sunkiau testuoti (`Application` priklausotų nuo per daug komponentų)
- Importų tarpusavio priklausomybių rizika
- Sunkiau išplėsti (kiekvienai naujai funkcionalumui reikalingi pakeitimai `Application`)

**Kodėl atmesta:**
Viena klasė turėtų turėti vieną atsakomybę (SRP). Application jau atsako už gyvavimo ciklo valdymą. Konfigūravimo seka turi būti atskira.

#### Option B: bootstrap.py (pasirinkta) ✅

**Privalumai:**
- ✅ **SRP**: Atskirtos dvi atsakomybės:
  - `Application` valdo gyvavimo ciklą
  - `bootstrap` kuria ir sujungia komponentus
- ✅ **Testuojamumas**: Galima patikrinti bootstrap atskirai nuo Application
- ✅ **Aiškumas**: Vienoje vietoje matoma visų komponentų sujungimo seka
- ✅ **Plėtojamumas**: Naujų komponentų pridėjimas neturi įtakos Application
- ✅ **Importų eilės tvarka**: Aiški hierarchija: main → bootstrap → konkretūs komponentai
- ✅ **Testuojama struktūra**: bootstrap gali būti visiškai atskiras, t.y., testai gali kurti komponentus be Application
- ✅ **Ateityje**: Galima turėti skirtingus bootstrap scenarijai (production, testing, development)

### Priklausomybių kryptis (pasirinktu sprendimu)

```
main.py
  │
  ├─→ bootstrap.bootstrap() arba bootstrap.create_app()
  │     │
  │     ├─→ Application
  │     │     │
  │     │     └─→ AppConfig
  │     │
  │     ├─→ AppState
  │     ├─→ EventBus
  │     ├─→ ServiceContainer
  │     ├─→ NavigationService
  │     ├─→ (MainView – ateityje)
  │     └─→ (AppController – ateityje)
  │
  └─→ Application.execute()
```

---

## Komponentų kūrimo seka

### Planuojama objektų kūrimo tvarka

Composition Root turi kurti komponentus šia tvarka:

```
1. AppConfig (pasilik Application.__init__())
   - ProjectPaths
   - SettingsManager  
   - Logger konfigūracija
   - Logger instancija

2. ServiceContainer()
   - Tuščia instancija, neturi priklausomybių

3. AppState()
   - Neturi priklausomybių, priklauso nuo AppState vidinio stavo

4. EventBus()
   - Neturi priklausomybių

5. NavigationService()
   - Gali priklausyti nuo EventBus (jei ateityje bus įvykių publikavimas)

6. MainView (ateityje)
   - Gali priklausyti nuo AppState, EventBus
   - Gali priklausyti nuo logger

7. AppController (ateityje)
   - Gali priklausyti nuo AppState, ServiceContainer, EventBus
   - Turi valdyti NavigationService
```

### Planuojama registravimo tvarka

```python
container = ServiceContainer()

# Registruojami pagrindiniai komponentai
container.register(AppState, app_state)
container.register(EventBus, event_bus)
container.register(NavigationService, navigation_service)

# MainView ir AppController registruojasi atskirai, 
# jei tą daro patys (pvz., per factory metodą)
```

### Sprendimas dėl ServiceContainer registravimo

**SPRENDIMAS: `ServiceContainer` **NEREGISTRUOJAMAS** savyje pačiame.**

**Priežastys:**

1. **Apibrėžtumas**: Kontaineris jau yra žinomas bootstrap kode, kuris jį kūrė.

2. **Išvengiamos tarpinės priklausomybės**: Jei `ServiceContainer` būtų registruojamas savyje, kitos klasės galėtų:
   - Prašyti `ServiceContainer` iš container
   - Tai sukurtų neperspektyvą (container priklauso nuo kontainerio)

3. **SRP**: `ServiceContainer` atsakingas tik už **servisų saugojimą ir grąžinimą**, ne **savęs registravimą**.

4. **IoC principas**: Šaltinį valdymo (Inversion of Control) principas sako, kad kontainerį turėtų valdyti **bootstrap**, o **ne** pats kontaineris.

5. **Ateities plėtimas**: Jei vėliau reikalingas kitoks kontainerio valdymas, šis sprendimas nėra svarbus.

**Išimtis**: Jei konkreti klasė **aiškiai žino**, kad jai reikalingas kontaineris (pvz., `MainWindow` turi dėl dinaminio servisų paieškos), tada ji gali **prašyti** kontainerio iš bootstrap aplinko. Bet tai turėtų būti labai retas atvejis.

---

## Programos paleidimo seka

### Planuojama paleidimo eilutė (pseudo-kodas)

```python
# src/app/main.py

def main() -> int:
    application = Application()
    
    # Čia būtu iškviečiamas bootstrap
    # app_state, event_bus, services = bootstrap.create_components(application.config)
    
    return application.execute()

# src/app/bootstrap.py

def create_components(config: AppConfig) -> tuple[AppState, EventBus, ServiceContainer]:
    """Create and configure all application components."""
    
    # 1. Sukuriam servisų konteinerį
    container = ServiceContainer()
    
    # 2. Sukuriam AppState
    app_state = AppState()
    
    # 3. Sukuriam EventBus
    event_bus = EventBus()
    
    # 4. Sukuriam NavigationService
    navigation_service = NavigationService()
    
    # 5. Registruojame pagrindnius komponentus
    container.register(AppState, app_state)
    container.register(EventBus, event_bus)
    container.register(NavigationService, navigation_service)
    
    # 6. Sukuriam MainView (ateityje)
    # main_view = MainView()
    # container.register(MainView, main_view)
    
    # 7. Sukuriam AppController (ateityje)
    # app_controller = AppController(container, app_state, event_bus)
    # container.register(AppController, app_controller)
    
    return app_state, event_bus, container
```

### Pilna paleidimo eilutė su gyvavimo ciklu

```
Pradžia (main.py)
  │
  ├─→ Application() sukūrimas
  │     └─→ AppConfig.__init__()
  │           ├─→ ProjectPaths
  │           ├─→ SettingsManager
  │           └─→ Logger
  │
  ├─→ bootstrap.create_components(config)
  │     ├─→ ServiceContainer()
  │     ├─→ AppState()
  │     ├─→ EventBus()
  │     ├─→ NavigationService()
  │     ├─→ Registracija: AppState, EventBus, NavigationService
  │     ├─→ MainView() [ateityje]
  │     └─→ AppController() [ateityje]
  │
  ├─→ Application.execute()
  │     │
  │     ├─→ try: Application.run()
  │     │         ├─→ logger.info("Starting...")
  │     │         ├─→ [Čia būtų pradėtas AppController]
  │     │         └─→ return 0
  │     │
  │     └─→ finally: Application.shutdown()
  │              └─→ logger.info("Application shutdown completed.")
  │
  └─→ sys.exit(0)
```

---

## Programos uždarymo seka

### Planuojama uždarymo eilutė (pseudo-kodas)

```python
# src/app/core/app.py

def shutdown(self) -> None:
    """Perform application shutdown tasks and log the completion."""
    
    try:
        # 1. Sustabdomas aktyvus kontroleris (jei jis yra)
        # if hasattr(self, 'app_controller') and self.app_controller:
        #     try:
        #         self.app_controller.stop()
        #     except Exception as e:
        #         self.logger.error(f"Error stopping AppController: {e}")
        
        # 2. Uždarytas MainView (jei ji yra)
        # if hasattr(self, 'main_view') and self.main_view:
        #     try:
        #         self.main_view.close()
        #     except Exception as e:
        #         self.logger.error(f"Error closing MainView: {e}")
        
        # 3. Sustabdoma AppState
        # if hasattr(self, 'app_state') and self.app_state:
        #     try:
        #         self.app_state.stop()
        #     except Exception as e:
        #         self.logger.error(f"Error stopping AppState: {e}")
        
        # 4. Išvalomos registracijos (jei yra kontaineris)
        # if hasattr(self, 'container') and self.container:
        #     try:
        #         self.container.clear()
        #     except Exception as e:
        #         self.logger.error(f"Error clearing container: {e}")
        
        self.logger.info("Application shutdown completed.")
        
    except Exception as e:
        self.logger.error(f"Unexpected error during shutdown: {e}")
        raise
```

### Pilna uždarymo eilutė

```
Application.shutdown()
  │
  ├─→ AppController.stop() [ateityje]
  │     └─→ Sustabdo visus aktyvius kontrolerius
  │
  ├─→ MainView.close() [ateityje]
  │     └─→ Uždaro sąsają
  │
  ├─→ AppState.stop()
  │     └─→ Sustabdo programos būsenos valdymą
  │
  ├─→ ServiceContainer.clear()
  │     └─→ Išvalo visas registracijas
  │
  └─→ logger.info("Application shutdown completed.")
```

---

## Išimčių valdymas

### Principas

Programos paleidimo metu **pirmoji išimtis turi būti išsaugota ir iškelta**, o **uždarymo klaidos negali maskuoti** originalios klaidos.

### Scenarijus

#### Scenarijus 1: Paleidimas nepavyksta

```python
try:
    result = application.run()
    # ✓ Sėkmės atveju grąžinama 0
except Exception as original_error:
    # ✗ Grąžinama klaida iš run()
    # finally bloke shutdown() būtinai iškviečiamos
    
finally:
    try:
        application.shutdown()
    except Exception as shutdown_error:
        # Uždarymo klaida negrąžina shutdown_error,
        # Vietoje to:
        # - Užregistruojama shutdown_error
        # - Iškelta originali original_error
        pass
```

#### Scenarijus 2: Paleidimas sėkminga, bet uždarymas nepavyksta

```
Application.execute():
  │
  ├─→ try: run() ✓ grąžina 0
  │
  └─→ finally: shutdown() ✗ išmeta Exception
         - Išimtis užregistruojama
         - Išimtis NEgrąžinama (nes run() buvo sėkminga)
         - Grąžinama 0 (klaidos negrąžiname, kai paleidimas buvo sėkminga)
```

#### Scenarijus 3: Abu nepavyks

```
Application.execute():
  │
  ├─→ try: run() ✗ išmeta ValueError
  │
  └─→ finally: shutdown() ✗ išmeta RuntimeError
         - shutdown() klaida NEPERRAŠO run() klaidą
         - ValueError išsaugojusi ir iškelta
         - RuntimeError užregistruojama kaip secondary error
```

### Kodas

```python
def execute(self) -> int:
    """Execute the application lifecycle and always run shutdown."""
    try:
        return self.run()
    finally:
        try:
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
            # Neperrrašom exception'o iš run(), tik registruojam shutdown klaidą
```

**Rezultatas**: Pirminė `run()` klaida **negali būti** maskuota `shutdown()` klaida.

---

## Priklausomybių kryptys

### Leidžiama priklausomybių seka

```
main.py
  ↓
bootstrap.py
  ↓
Application + AppConfig
  ↓
AppState, EventBus, ServiceContainer, NavigationService
  ↓
Core komponentai (Logger, Paths, Settings)
  ↓
Python Standard Library
```

### Aiškios taisyklės

✅ **LEIDŽIAMA:**
- `main.py` → `bootstrap.py`
- `bootstrap.py` → konkretūs komponentai (AppState, EventBus, etc.)
- `AppController` → `AppState`, `EventBus`, `ServiceContainer`
- Kontroleriai → Core komponentai

❌ **DRAUDŽIAMA:**

| Draudžiama | Priežastis |
|-----------|-----------|
| `BaseView` → `AppController` | GUI neturi žinoti apie valdymą |
| `BaseModel` → GUI | Modelis nepriklausomas nuo sąsajos |
| `EventBus` → konkretūs kontroleriai | Sujungimas per konkretius tipus |
| `ServiceContainer` → konkretūs servisai | Kontaineris generiškas |
| `AppState` → `EventBus` arba GUI | Būsena neturi žinoti apie įvykius |
| Bet kas → `bootstrap.py` | Bootstrap tik main pradžioje |
| Core komponentai → MVC | Core nepriklausomas nuo verslo logikos |

---

## Sprendimai, kurie dar neįgyvendinami

### ⏳ Būsimo diegimo etape

Šiame dokumente **aprašytas planas**, bet **nekurtas** produkcinis kodas:

- ❌ `src/app/bootstrap.py` dar **nekuriamas**
- ❌ `Application` dar **nemodifikuojama**
- ❌ Komponentai **neintegruojami**
- ❌ `MainView` dar **nekuriama**
- ❌ `AppController` dar **nesujungiama** su likusia sistema

### ✅ Kas jau priimta šiame etape

- ✅ Sprendimas dėl bootstrap.py vietos
- ✅ Komponentų kūrimo seka
- ✅ Registravimo planas
- ✅ Gyvavimo ciklo aprašymas
- ✅ Išimčių valdymo principas
- ✅ Priklausomybių kryptys

### 🔄 Kitas žingsnis

Kai bus pradėta integruoti `MainView` ir `AppController`, bus:

1. Sukurtas `src/app/bootstrap.py` modulis
2. Iš `Application.__init__()` bus iškelti komponentų sukūrimai
3. Application.execute() bus atnaujinta komponentų paleidimui
4. Testai bus atnaujinti naujam modeliui

---

## Nuorodos

- Žr. `ADR-001-composition-root.md` dėl detalaus pasirinkimo pagrindimo
- Žr. `ARCHITECTURE.md` dėl bendros sistemos architektūros
- Žr. `CORE_ARCHITECTURE.md` dėl Core sluoksnio principų
