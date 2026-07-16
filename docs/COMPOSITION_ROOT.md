# Composition Root

**Dokumentas:** COMPOSITION_ROOT.md
**Versija:** 2.0
**Būsena:** Įgyvendinta
**Data:** 2026-07-16

---

## Paskirtis

Composition Root yra vienintelė vieta, kurioje kuriamas ir sujungiamas pagrindinis programos objektų grafas. Jis įgyvendintas modulyje `src/app/bootstrap.py`.

`bootstrap()` tik sukuria objektus, perduoda jų priklausomybes, registruoja pagrindines instancijas ir grąžina paruoštą `Application`. Funkcija nepaleidžia kontrolerio, nerodo lango ir nevykdo Qt įvykių ciklo.

Composition Root pasirinktas kaip atskiras aukščiausio lygio modulis, kad objektų grafo surinkimas nebūtų maišomas su programos gyvavimo ciklu ar Core infrastruktūra. Tai išlaiko vieną aiškią komponentų kūrimo vietą ir leidžia testuoti surinkimą atskirai nuo programos vykdymo.

## Architektūrinio sprendimo pagrindimas

Buvo vertintos dvi vietos objektų grafui surinkti:

### `Application` klasė – atmesta

Jeigu konkrečius komponentus kurtų pati `Application`, ji vienu metu valdytų gyvavimo ciklą ir vykdytų Composition Root darbą. Dėl to Core klasė priklausytų nuo Qt, konkretaus View ir kontrolerio, būtų sunkiau testuojama ir pažeistų vienos atsakomybės bei priklausomybių inversijos principus.

### Atskiras `bootstrap.py` – pasirinkta

`src/app/bootstrap.py` gali teisėtai importuoti konkrečius Core, infrastruktūros, MVC ir GUI komponentus, nes yra aukščiausio lygio surinkimo modulis. `Application` priklauso tik nuo mažų Core protokolų, o konkrečios realizacijos jai perduodamos konstruktoriuje.

`bootstrap.py` nėra `app.core` dalis. Įkėlus jį į Core paketą atsirastų neleistina Core priklausomybė nuo GUI, MVC ir Qt infrastruktūros.

## Atsakomybių ribos

### `main.py`

`main.py` tik iškviečia `bootstrap()`, gauna `Application`, paleidžia `execute()` ir grąžina išėjimo kodą operacinei sistemai. Jis nekuria atskirų servisų, `QApplication`, View ar kontrolerių ir nevykdo registracijos.

### `bootstrap.py`

Composition Root:

* sukuria arba panaudoja vienintelę `QApplication`;
* sukuria konkrečias komponentų instancijas;
* aiškiai perduoda konstruktorių priklausomybes;
* registruoja instancijas `ServiceContainer`;
* grąžina sukomponuotą `Application`.

Composition Root nevykdo `Application.execute()`, `QtEventLoop.run()`, navigacijos, kontrolerio `start()` ar View `show()`. Jame nėra verslo logikos, globalaus servisų registro ar importų šalutinių efektų.

### `Application`

`Application` valdo paleidimo ir uždarymo seką. Ji nekuria konkrečių servisų, GUI objektų ar Qt aplikacijos ir neimportuoja PySide6, `MainView` arba `AppController`.

### MVC ir servisai

`MainView` atsako tik už pagrindinio lango pateikimą. `AppController` valdo View paleidimą ir sustabdymą. `NavigationService` aktyvuoja pradinį kontrolerį ir uždaro aktyvų kontrolerį, bet jų nekuria ir savarankiškai nepasirenka. `AppState` saugo vykdymo būseną, o `EventBus` lieka silpnai susietų įvykių kanalu.

## Faktinė kūrimo seka

```text
1. QApplication (sukuriama arba panaudojama esama)
2. QtEventLoop
3. ServiceContainer
4. AppState
5. EventBus
6. NavigationService
7. MainView
8. AppController
9. Application
10. return Application
```

`QApplication` visada egzistuoja prieš kuriant `MainView`. `bootstrap()` naudoja esamą tinkamą instanciją arba sukuria vieną naują su proceso argumentais.

## Objektų grafas

```text
QApplication ──→ QtEventLoop ──→ Application
AppState ──────────────────────→ Application
NavigationService ─────────────→ Application
MainView ──→ AppController ────→ Application

ServiceContainer
├── AppState
├── EventBus
├── NavigationService
├── MainView
├── AppController
└── QtEventLoop
```

`ServiceContainer` savyje neregistruojamas ir nėra perduodamas į `Application`. `EventBus` registruojamas, bet nėra dirbtinai perduodamas jo nereikalaujantiems komponentams. Visame grafe naudojama po vieną kiekvieno pagrindinio komponento instanciją.

## Registravimo taisyklės

Konteineryje registruojamos jau sukurtos instancijos pagal konkretų jų tipą. Tas pats tipas neregistruojamas pakartotinai ir esama registracija tyliai neperrašoma.

`ServiceContainer` valdo tik Composition Root. Komponentai jo nenaudoja kaip paslėpto Service Locator, kai priklausomybę galima perduoti tiesiogiai. Konteineris neregistruojamas pats savyje ir nėra `Application`, `MainView` ar `AppController` priklausomybė.

`QApplication` konteineryje neregistruojama, nes dabartiniame objekte nėra komponento, kuris turėtų ją gauti iš registro. `QtEventLoop` registruojamas pagal konkretų tipą.

## Gyvavimo ciklas

`src/app/main.py` iškviečia `bootstrap()`, gauna `Application` ir kviečia `execute()`.

`Application` valdo gyvavimo ciklą per Core protokolus:

```text
Application.run()
├── AppState.start()
├── NavigationPort.navigate_to(AppController)
└── EventLoopPort.run()

Application.shutdown()
├── NavigationPort.close_current()
├── AppState.stop()
└── EventLoopPort.quit()
```

Qt įvykių ciklą valdo `Application` per `EventLoopPort`. Konkretus `QtEventLoop` adapteris deleguoja veiksmus jau sukurtai `QApplication` ir pats jos nekuria.

`Application.execute()` naudoja `try/finally`, todėl `shutdown()` vykdomas ir `run()` klaidos atveju. Gyvavimo ciklo operacijų klaidos nėra nutylimos; dabartinė realizacija išsaugo standartinę Python `finally` semantiką.

## Qt infrastruktūros riba

Vienintelė `QApplication` sukuriama `bootstrap.py` prieš `MainView`. Jei tinkama instancija jau egzistuoja, ji panaudojama pakartotinai. `QtEventLoop` gauna tą pačią instanciją ir tik deleguoja `exec()` bei `quit()` kvietimus.

Qt įvykių ciklas nepaleidžiamas Composition Root. Jį paleidžia `Application.run()` per `EventLoopPort`, todėl Core testams nereikia tikros PySide6 aplikacijos.

## Priklausomybių ribos

Leidžiama kryptis:

```text
main.py → bootstrap.py → konkretūs komponentai → Core
```

Core sluoksnis neimportuoja `bootstrap.py`, PySide6, `MainView` ar `AppController`. Qt infrastruktūra lieka `app.infrastructure`, o konkretūs GUI ir MVC komponentai sujungiami tik Composition Root.

Papildomos taisyklės:

* `MainView` nekuria `QApplication` ar `AppController`;
* `AppController` nekuria View, servisų ar konteinerio;
* `NavigationService` nekuria kontrolerių;
* `ServiceContainer` nepriklauso nuo konkrečių registruojamų klasių;
* `EventBus` nepriklauso nuo konkrečių prenumeratorių;
* Core protokolai neimportuoja konkrečių realizacijų;
* priklausomybės perduodamos konstruktoriais pagal faktines klasių sąsajas;
* nenaudojamas automatinis priklausomybių aptikimas, refleksija ar DI karkasas.

## Testavimo strategija

Composition Root testai pakeičia išorinių komponentų konstruktorius kontroliuojamais testiniais objektais ir užfiksuoja sukurtą konteinerį. Jie patvirtina registracijas, instancijų tapatumą, vienintelės `QApplication` naudojimą ir gyvavimo ciklo šalutinių veiksmų nebuvimą.

Qt adapteris testuojamas atskirai, nepaleidžiant tikro įvykių ciklo. Integracinė paleidimo patikra vykdoma `offscreen` režimu, automatiškai uždarant pagrindinį langą.

## Plėtimo principai

Naujas komponentas į Composition Root įtraukiamas tik tada, kai egzistuoja patvirtinta jo atsakomybė ir faktinė konstruktoriaus priklausomybė. Naujos priklausomybės nepridedamos vien dėl to, kad objektas jau yra konteineryje.

Skirtingi paleidimo scenarijai ar papildomas factory sluoksnis gali būti svarstomi tik atskiro architektūrinio sprendimo metu. Dabartinis `bootstrap()` sąmoningai lieka trumpas, tiesioginis ir be sąlyginių verslo scenarijų.

## Įgyvendinti komponentai

* `QApplication` ir `QtEventLoop` integracija;
* `ServiceContainer`;
* `AppState`;
* `EventBus`;
* `NavigationService`;
* `MainView`;
* `AppController`;
* `Application` gyvavimo ciklo priklausomybių injekcija;
* `main.py` integracija;
* Composition Root automatiniai testai.

## Nuorodos

* `ADR-001-composition-root.md` – Composition Root vietos sprendimas.
* `CORE_ARCHITECTURE.md` – Core sluoksnio principai.
* `ARCHITECTURE.md` – bendra sistemos architektūra.
