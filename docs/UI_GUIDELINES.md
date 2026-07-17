Exit code: 0
Wall time: 0.6 seconds
Output:
# UI_GUIDELINES.md

**Projektas:** PTH Fausta
**Dokumentas:** UI_GUIDELINES.md
**Versija:** 1.0
**Būsena:** Patvirtinta kaip pradinė UI dizaino sistema
**Autorius:** Claude (UI/UX inžinierius), pataisyta pagal architekto ir savininko pastabas
**Sukūrimo data:** 2026-07-17
**Paskutinis atnaujinimas:** 2026-07-17

---

# 1. Paskirtis

Šis dokumentas apibrėžia PTH Fausta naudotojo sąsajos dizaino sistemą: spalvas,
tipografiją, tarpus, komponentų stilių, UI būsenas, prieinamumo taisykles ir
pagrindinių langų karkasą.

Tikslas – užtikrinti vizualinį ir elgsenos nuoseklumą visoje programoje, kad
kiekvienas naujas langas būtų kuriamas pagal tuos pačius principus, o ne
projektuojamas iš naujo.

Šis dokumentas apibrėžia dizainą, bet ne jo techninę realizaciją PySide6
kalba – tai priklauso techninių užduočių ir programuotojo atsakomybei.

Dokumentas gali būti papildomas naujais komponentais ir būsenomis, tačiau
esami pagrindiniai principai keičiami tik Produkto savininko patvirtinimu.

---

# 2. Projekto būsenos pastaba

Šio dokumento pirmojoje versijoje buvo klaidingai paminėta, kad Task 5.3
(Company Profile UI) jau įgyvendintas kaip veikiantis langas. Tai neatitiko
patvirtintos Git istorijos.

Teisinga formuluotė:

> Artimiausias planuojamas funkcinis modulis – Įmonės profilis ir banko
> sąskaitos. Jo galutinis UI turi būti įgyvendintas pagal šiame dokumente
> apibrėžtas gaires, kai atitinkamas etapas bus faktiškai pasiektas ir
> patvirtintas.

Šis dokumentas apibrėžia tikslinį (target) dizainą, ne esamą įgyvendinimo
būseną. Faktinė projekto būsena visada tikrinama `CHANGELOG.md` ir `TODO.md`,
ne šiame dokumente.

---

# 3. Spalvų paletė

| Paskirtis | Hex | Naudojimas |
|---|---|---|
| Primary | `#2563EB` | pagrindiniai veiksmų mygtukai, aktyvi navigacija, nuorodos, prekės ženklo identitetas |
| Primary hover | `#1D4ED8` | mygtuko hover būsena |
| Accent | `#0EA5E9` | antriniai akcentai, pažymėjimai |
| Success | `#16A34A` | patvirtinti veiksmai, „apmokėta“, teigiami indikatoriai |
| Warning | `#D97706` | įspėjimai, „laukiama“, „vėluoja“ |
| Error | `#DC2626` | klaidos, trynimo veiksmai, validacija |
| Text primary | `#0F172A` | pagrindinis tekstas, **visos antraštės (H1, H2, H3)** |
| Text secondary | `#64748B` | pagalbinis tekstas, pastabos, lentelių antraštės — **ne** antraštėms H1/H2 |
| Border | `#E2E8F0` | numatytosios linijos |
| Border strong | `#CBD5E1` | formos laukų kontūrai |
| Surface | `#FFFFFF` | kortelės, paneliai, laukai |
| Page background | `#F8FAFC` | lango / darbo srities fonas |
| Row hover | `#F8FAFC` | lentelės eilutės hover |
| Row selected | `#E6F1FB` | pažymėta lentelės eilutė (tekstas `#0C447C`) |

Taisyklė dėl spalvos reikšmės:

> Būsenos ir klaidos negali būti perteikiamos vien spalva. Semantinės spalvos
> turi būti naudojamos nuosekliai pagal jų reikšmę.

Primary spalva gali būti naudojama ir prekės ženklo identitetui (logotipas,
akcentinės linijos), ne tik funkciniams veiksmams — tai nelaikoma pažeidimu.

## 3.1 Design tokens (žetonai)

Kad gairės būtų lengvai perkeliamos į QSS, reikšmės įvardijamos kaip
centralizuoti žetonai. Programuotojas naudoja vieną žetonų šaltinį, ne
kopijuoja hex reikšmes į kiekvieną langą.

```text
color-primary            #2563EB
color-primary-hover      #1D4ED8
color-accent             #0EA5E9
color-success            #16A34A
color-warning            #D97706
color-error              #DC2626
color-text-primary       #0F172A
color-text-secondary     #64748B
color-border             #E2E8F0
color-border-strong      #CBD5E1
color-surface            #FFFFFF
color-page-background    #F8FAFC

spacing-xs   4px
spacing-sm   8px
spacing-md   16px
spacing-lg   24px
spacing-xl   32px

radius-sm    6px
radius-md    10px
```

Šis sąrašas neapibrėžia pilnos temų (theming) sistemos — tik centralizuotą
reikšmių šaltinį pirmajam etapui.

---

# 4. Tipografija

Šriftas: **Segoe UI** (natyvus Windows šriftas).

| Lygis | Loginis dydis | Storis | Naudojimas |
|---|---|---|---|
| H1 | 22 | 600 | lango / puslapio antraštė |
| H2 | 18 | 600 | dialogo, kortelės antraštė |
| H3 | 15 | 600 | formos bloko antraštė |
| Body | 13 | 400 | pagrindinis tekstas, laukų reikšmės |
| Small | 12 | 400 | pastabos, pagalbinis tekstas, lentelės antraštės |
| Button | 13 | 500 | mygtukų tekstas |

Šiame dokumente dydžiai nurodyti kaip vizualiniai orientyrai, ne griežti
fiziniai pikseliai.

> Techninėje PySide6 realizacijoje šrifto dydžiai turi būti pritaikyti Qt DPI
> skalavimui (100 %, 125 %, 150 %). Negalima remtis tik fiksuotais px —
> programuotojas naudoja loginius dydžius ir, kur įmanoma, `pt` vietoj `px`.

Visur naudojama sentence case (didžioji tik pirma raidė), be išimčių
antraštėse ir mygtukuose.

---

# 5. Tarpai (8px grid)

Naudojama tik iš šio rinkinio: `4, 8, 12, 16, 24, 32, 48` (žr. `spacing-*`
žetonus 3.1 skyriuje).

* spacing-xs (4px) – tarpas tarp glaudžiai susijusių mikro-elementų;
* spacing-sm (8px) – tarpas tarp label ir lauko;
* spacing-md (16px) – tarpas tarp laukų grupėje;
* spacing-lg (24px) – tarpas tarp formos blokų;
* spacing-xl (32px) – tarpas tarp pagrindinių lango sekcijų.

---

# 6. Komponentai

## 6.1 Mygtukai

| Tipas | Fonas | Tekstas | Naudojimas |
|---|---|---|---|
| Primary | `color-primary` | baltas | pagrindinis veiksmas lange — **vienas per ekraną** |
| Secondary | baltas, kontūras `color-border-strong` | `color-text-primary` | antriniai veiksmai (atšaukti) |
| Danger | `color-error` | baltas | negrįžtami veiksmai (šalinti), visada su patvirtinimu |
| Disabled | `#F1F5F9` | `#94A3B8` | neaktyvus veiksmas |

Kampų spindulys: `radius-sm`. Vidinis paddingas: spacing-sm spacing-md.

## 6.2 Formos

* Label visada **virš** lauko (ne kairėje) — geriau tinka ilgesniems
  lietuviškiems pavadinimams ir prisitaikymui prie lango pločio.
* Privalomas laukas žymimas raudonu `*` šalia label.
* Placeholder — pilkas, rodo pavyzdinę reikšmę, ne pasikartojantį label.
* Klaidos pranešimas rodomas po lauku, raudonu tekstu, **kartu su tekstiniu
  paaiškinimu** — ne vien lauko kontūro spalva.
* Tab tvarka atitinka vizualinę formos tvarką (žr. 8 skyrių).

## 6.3 Lentelės

* Antraštė: fonas `#F1F5F9`, tekstas `color-text-secondary`, 600 storis.
* Selected eilutė: fonas `#E6F1FB`, tekstas `#0C447C`.
* Hover eilutė: fonas `color-page-background`.

### Eilučių veiksmai (pataisyta pagal architekto pastabą)

Redagavimo/šalinimo ikonos kiekvienos eilutės gale **nenaudojamos** kaip
vienintelis būdas — desktop programoje tai sunkiau valdyti klaviatūra ir
padidina atsitiktinio ištrynimo riziką. Vietoje to:

* pagrindiniai veiksmai (Pridėti, Redaguoti, Šalinti) rodomi **virš
  lentelės**, kaip mygtukai;
* dukart spustelėjus eilutę — atidaromas redagavimas;
* eilutės gale gali būti papildomas `⋯` meniu papildomiems veiksmams;
* šalinimo veiksmas visada reikalauja patvirtinimo dialogo;
* visi veiksmai pasiekiami vien klaviatūra (Tab + Enter/Space, be pelės).

## 6.4 Ikonos

Vienodo stiliaus outline (kontūrinis) ikonų rinkinys, vienspalvis,
paveldintis teksto spalvą. Dydis: 16–18 navigacijoje ir mygtukuose, iki 24 —
tik akcentuojantiems elementams. Ikonų-mygtukai visada turi tooltip ir
accessible name (žr. 8 skyrių).

---

# 7. UI būsenos

Kiekvienam duomenimis grįstam ekranui (pvz., lentelėms, formoms) turi būti
numatytos šios būsenos, ne tik „galutinis“ vaizdas:

## Loading

* duomenų kraunant nerodoma tuščia lentelė kaip galutinė būsena;
* naudojamas aiškus užimtumo indikatorius;
* dvigubas išsaugojimas / veiksmas blokuojamas kol kraunama.

## Empty state

* rodomas paaiškinantis tekstas, ne tuščias plotas;
* pavyzdys: „Banko sąskaitų dar nėra. Pridėkite pirmąją sąskaitą.“

## Saving

* „Išsaugoti“ mygtukas laikinai neaktyvus vykdant operaciją;
* pakartotinis tos pačios operacijos siuntimas neleidžiamas;
* klaidos atveju įvesti duomenys išlieka formoje (nepradingsta).

## Error

* lauko klaida rodoma prie konkretaus lauko;
* sisteminė klaida rodoma bendrame pranešime;
* klaida visada paaiškinama tekstu arba ikona + tekstu, ne vien spalva.

## Unsaved (neišsaugoti pakeitimai)

* turi būti aiškiai matoma (pvz., žymeklis prie antraštės ar mygtuko
  būsena), kad forma turi neišsaugotų pakeitimų;
* uždarant langą su neišsaugotais pakeitimais — rodomas patvirtinimo
  dialogas;
* po sėkmingo išsaugojimo rodomas trumpas būsenos pranešimas.

---

# 8. Prieinamumas ir klaviatūros navigacija

* spalva niekada nėra vienintelis būsenos indikatorius;
* visi veiksmai pasiekiami klaviatūra, be pelės;
* Tab tvarka atitinka vizualinę formos tvarką;
* Enter vykdo pagrindinį veiksmą tik tada, kai tai saugu (nepavojingas
  veiksmas — ne šalinimas);
* Esc uždaro dialogą arba atšaukia veiksmą;
* fokusas visada aiškiai matomas (focus ring);
* ikonų mygtukai turi tooltip ir accessible name;
* teksto ir fono kontrastas turi būti pakankamas (min. WCAG AA);
* klaidos visada paaiškintos tekstu, ne tik spalva ar ikona.

---

# 9. Navigacijos sprendimas

Pasirinkta **kairė sidebar navigacija**, o ne Ribbon.

Priežastys:

* sistema yra modulinė, su galimybe augti naujais moduliais be architektūros
  keitimo (žr. `PRODUCT_SCOPE.md`) — sidebar tai palaiko geriau;
* Ribbon tinka programoms, kur dominuoja komandos vienam dokumentui
  (pvz., MS Office), o PTH Fausta dominuoja navigacija tarp modulių;
* sidebar galima suskleisti į ikonų juostą siaurame lange, išlaikant
  naudojimo patogumą.

## Navigacijos punktai (pirma versija, ne galutinis sąrašas)

```text
Pradžia
Dokumentai
Klientai
Prekės
Analitika
(skirtukas)
Nustatymai
```

> Navigacijos punktų sudėtis gali plėstis pagal patvirtintus verslo
> modulius (pvz., Mokėjimai, Šablonai, Archyvas, Numeracija, El. pašto
> istorija), tačiau pagrindinis sidebar principas lieka nekintamas.

---

# 10. Pagrindinio lango karkasas (Main Window)

Struktūra:

```text
┌─────────────────────────────────────────────┐
│ Antraštės juosta: programos pavadinimas | globali paieška | lango veiksmai │
├───────────┬───────────────────────────────────┤
│ Navigacija │ Darbo sritis                        │
│ (sidebar)  │ (metrikos, greiti veiksmai, turinys)│
├───────────┴───────────────────────────────────┤
│ Būsenos juosta: DB būsena | programos versija    │
└─────────────────────────────────────────────┘
```

## Pataisymai dėl dar neįgyvendintų modulių

* Viršutinėje juostoje **nerodoma** vartotojo profilio zona, nes projekte
  dar nėra patvirtinto naudotojų / autentifikavimo modulio.

  > Vartotojo profilio zona įtraukiama tik tada, kai projekte bus
  > patvirtintas naudotojų ir autentifikavimo modulis.

* Būsenos juostoje šiuo metu rodoma tik **DB būsena** ir **programos
  versija**.

  > „Aktyvi įmonė“ gali būti rodoma būsenos juostoje tik tada, kai Company
  > Profile modulis realiai veiks ir bus pasirinkimo tarp kelių įmonių
  > galimybė (jei tokia atsiras).

## Prisitaikymas prie lango dydžio

(Terminas „responsive“ pakeistas į „prisitaikymas prie lango dydžio“, kaip
tikslesnį PySide6 kontekste.)

Bendra logika, ne griežti absoliutūs pikselių pažadai:

> Mažėjant lango pločiui, navigacija suskleidžiama į ikonų juostą, o
> metrikų kortelės ir greitieji veiksmai persirikiuoja pagal turimą vietą.

Orientaciniai (rekomendaciniai, ne absoliutūs) plotmenų taškai:

| Plotis (orientacinis) | Elgsena |
|---|---|
| platus langas | pilnas sidebar (ikona + tekstas), kortelės vienoje eilutėje |
| vidutinis langas | sidebar suskleidžiamas į ikonų juostą su tooltip |
| siauras langas | kortelės ir veiksmai persirikiuoja į mažesnį stulpelių skaičių |

> Rekomenduojamas minimalus loginis lango plotis — apie 860 px. Galutinį
> minimumą programuotojas turi patikrinti su 100 %, 125 % ir 150 % Windows
> DPI masteliu bei ilgesniais lietuviškais tekstais — dizaino gairės
> nereikalauja absoliučių fizinių pikselių visuose ekranuose.

---

# 11. Įmonės rekvizitų langas (pavyzdys pilnam UX)

Langas skirstomas į loginius blokus su antraštėmis (ne vientisą lauko sąrašą):

1. **Rekvizitai** — pavadinimas, įmonės kodas, PVM kodas, adresas.
2. **Kontaktai** — telefonas, el. paštas, svetainė.
3. **Banko sąskaitos** — lentelė su stulpeliais Bankas / IBAN, Valiuta,
   Numatytoji (badge). Veiksmai (Pridėti, Redaguoti, Šalinti) — mygtukais
   virš lentelės, ne ikonomis kiekvienoje eilutėje (žr. 6.3).

## Veiksmų juosta (pataisyta terminija)

„Lipni“ (interneto terminas) pakeista į:

> Fiksuota veiksmų juosta lango apačioje.

Ji nesislenka kartu su forma. Mygtukai: **Atšaukti | Išsaugoti**.

Elgsena:

* „Išsaugoti“ aktyvus tik esant faktinių pakeitimų (žr. Unsaved būseną,
  7 skyrius);
* „Atšaukti“ grąžina paskutinę išsaugotą būseną;
* uždarant langą su neišsaugotais pakeitimais — rodomas patvirtinimo
  dialogas;
* po sėkmingo išsaugojimo rodomas trumpas būsenos pranešimas (ne modalinis
  dialogas).

Skirtukai (tabs) atskiria „Bendra informacija“ nuo „Banko sąskaitos“, kai
turinys nesutelpa į vieną vaizdą.

---

# 12. Lokalizacijos taisyklė

Visi naudotojui matomi tekstai (label, mygtukai, pranešimai, lentelių
antraštės, tooltip'ai) — lietuvių kalba, pagal `AI_TEAM.md` kalbos politiką.
UI komponentai projektuojami taip, kad tekstas nebūtų fiksuoto ilgio
(leidžiama laukams/mygtukams prisitaikyti prie ilgesnių lietuviškų terminų
ir būsimų vertimų).

---

# 13. Versijų istorija

| Versija | Data | Patvirtino | Pakeitimai |
|---|---|---|---|
| 1.0 | 2026-07-17 | Savininkas, Architektas | Ištaisytas klaidingas teiginys apie Task 5.3; vartotojo profilis pažymėtas kaip būsima funkcija; būsenos juosta apribota iki DB būsenos ir versijos; „responsive“ pakeista į prisitaikymą prie lango dydžio; pikselių ribos padarytos rekomendacinės su DPI pastaba; lentelių veiksmams pridėta klaviatūros prieinamumo ir saugaus šalinimo logika; „lipni“ juosta pervadinta į fiksuotą veiksmų juostą; pridėtos loading/empty/saving/error/unsaved būsenos; pridėtas prieinamumo skyrius; įtraukti design tokens; dokumentas patvirtintas kaip pradinė UI dizaino sistema. |
