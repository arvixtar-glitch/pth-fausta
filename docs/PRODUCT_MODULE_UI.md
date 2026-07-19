# PRODUCT_MODULE_UI.md

**Projektas:** PTH Fausta
**Dokumentas:** PRODUCT_MODULE_UI.md
**Užduotis:** Task 7.0A – Product Module UI Specification
**Versija:** 1.1
**Būsena:** Patvirtinta
**Autorius:** Claude (UI/UX inžinierius)
**Sukūrimo data:** 2026-07-19
**Paskutinis atnaujinimas:** 2026-07-19 (v1.1 – architekto ir savininko pastabų taikymas)

---

# 1. Paskirtis

Šis dokumentas apibrėžia pilną Prekių ir paslaugų (Product) modulio
naudotojo sąsają. Modulis kuriamas kaip **nuoseklus tos pačios sistemos
tęsinys**, o ne atskiras dizainas — struktūra, komponentai ir elgsenos
taisyklės perimtos iš `CUSTOMER_MODULE_UI.md` (v1.1), kuris šiuo metu yra
projekto UI etalonas.

Dokumentas remiasi:
* `UI_GUIDELINES.md` — spalvos, tipografija, komponentai, būsenos,
  prieinamumas;
* `ARCHITECTURE.md` — sluoksnių ir priklausomybių ribos;
* `CUSTOMER_MODULE_UI.md` (v1.1) — pakartotinai naudojamas sąrašo/formos
  šablonas.

Čia neprojektuojama duomenų bazė, verslo logika, ORM ar validacijos
algoritmas — tik UI ir UX.

## 1.1 Peržiūros suvestinė (v1.1)

Architekto ir savininko pastabos priimtos taip:

* **Kategorija** — pakeista iš laisvo teksto į ComboBox su galimybe pridėti
  naują reikšmę (8.1), kad nesuskiltų statistika dėl skirtingų rašybos
  variantų.
* **Barkodai, Dokumentai, Nuotraukos, Import/Export** — architekto
  patvirtinti be pakeitimų (8.3, 8.6, 12).
* **Vienetas** — papildyta pastaba, kad vienetų sąrašas ateityje taps
  atskiru administruojamu moduliu (8.1).
* **Kaina ir PVM** — pakeista į sąlyginę logiką pagal tai, ar įmonės
  profilyje įvestas PVM kodas (savininko sprendimas, žr. 8.2 ir 7.1).
* **PVM tarifas** — liks ComboBox, bet rodomas tik kai įmonė yra PVM
  mokėtoja.
* **Serijiniai numeriai** — pridėti prie ateities plėtros sąrašo (12).
* **„Kainodara“** — skirtuko pavadinimas patvirtintas toks, kad ateityje
  netektų keisti pavadinimo pridedant nuolaidas, kelias kainas ar valiutą.

---

# 2. Modulio paskirtis

Modulis valdo **prekes ir paslaugas viename bendrame sąraše**. Skirtumas
tarp jų — tik `tipas` (Prekė / Paslauga), ne atskiros lentelės ar atskiri
langai. Tai atitinka tą patį principą, kaip Customer modulyje „Kliento
tipas“ (Juridinis/Fizinis) neišskaido kliento į du skirtingus modulius.

---

# 3. Pagrindinis langas (Product List View)

Struktūra identiška `CustomerListView` (žr. `CUSTOMER_MODULE_UI.md` 2
skyrių), tik pritaikyta prekių/paslaugų kontekstui:

```text
┌────────────────────────────────────────────────────────────────┐
│ Prekės ir paslaugos      [+Nauja prekė][+Nauja paslauga][Redaguoti][Šalinti] │
│ Tvarkykite prekių ir paslaugų sąrašą...                          │
├────────────────────────────────────────────────────────────────┤
│ [Ieškoti prekės ar paslaugos...]  [Tipas ▾] [Būsena ▾]           │
├────────────────────────────────────────────────────────────────┤
│ Pavadinimas │ Kodas │ Barkodas │ Tipas │ Vnt. │ Kaina │ PVM │ Būsena │
│ ...lentelės eilutės arba tuščia/įkėlimo būsena...                 │
├────────────────────────────────────────────────────────────────┤
│ 132 įrašai                              DB prijungta │ v0.1.3     │
└────────────────────────────────────────────────────────────────┘
```

* Antraštė, aprašomasis tekstas, paieškos/filtrų eilutė ir būsenos juosta —
  tas pats išdėstymo principas, komponentai ir tarpai kaip Customer modulyje
  (pakartotinis naudojimas, ne perkūrimas).
* Įrašų skaičius rodomas būsenos juostoje apačioje (kaip patvirtinta
  Customer v1.1), ne virš lentelės.

---

# 4. Veiksmų juosta

| Mygtukas | Tipas | Aktyvus, kai |
|---|---|---|
| Nauja prekė | Primary | visada |
| Nauja paslauga | Secondary (akcentuotas, žr. 4.1) | visada |
| Redaguoti | Secondary | pažymėta lygiai vienas įrašas |
| Šalinti | Danger | pažymėta lygiai vienas įrašas |

## 4.1 Dviejų „naujo įrašo“ mygtukų pastaba

Užduotyje numatyti du atskiri mygtukai („Nauja prekė“ / „Nauja paslauga“),
o ne vienas su papildomu pasirinkimu formoje. Tai **sumažina paspaudimų
skaičių** (dizaino tikslas 8 skyriuje) — naudotojas iškart patenka į formą
su jau teisingai nustatytu tipo perjungikliu, jam nereikia po to papildomai
perjungti „Tipas“ lauko. `UI_GUIDELINES.md` numato tik vieną Primary mygtuką
ekrane, todėl „Nauja paslauga“ vizualiai lieka Secondary (kontūrinis), kad
nebūtų dviejų vienodai akcentuotų veiksmų.

Alternatyva, jei programuotojui aktualu taupyti horizontalią vietą siaurame
lange: vienas suskleidžiamas mygtukas „+ Naujas ▾“ su dviem punktais meniu
(„Prekė“, „Paslauga“). Tai lygiavertis sprendimas — pasirinkimą tarp šių
dviejų variantų siūlau palikti architektui/programuotojui pagal turimą
vietą lange.

---

# 5. Paieška

* **Momentinė** (be atskiro „Ieškoti“ mygtuko), atnaujina lentelę iš karto
  rašant.
* Placeholder — trumpas, kaip Customer modulyje: **„Ieškoti prekės ar
  paslaugos...“**.
* Ieško pagal: pavadinimą, kodą, barkodą, kategoriją — analogiškai
  `search_text` principui, aprašytam `DATABASE.md` ir pritaikytam Customer
  module (žr. `CUSTOMER_MODULE_UI.md` 2.2).

---

# 6. Filtrai

Tvarka atitinka Customer v1.1 sprendimą (tipas prieš būseną — natūralesnė
mąstymo seka):

1. **Tipas** — Visi / Prekė / Paslauga.
2. **Būsena** — Visi / Aktyvi / Neaktyvi.

Abu — išskleidžiami sąrašai (combo box), veikia kartu su paieška (loginis
IR), be atskiro patvirtinimo mygtuko.

---

# 7. Lentelė

## 7.1 Stulpeliai

| Stulpelis | Pastaba |
|---|---|
| Pavadinimas | pagrindinis identifikuojantis stulpelis, numatytasis rūšiavimas (A→Z) |
| Kodas | trumpas, atitinka Customer modulio sprendimą sutrumpinti pavadinimus lentelėje |
| Barkodas | tuščias laukas rodomas kaip „—“ |
| Tipas | „Prekė“ / „Paslauga“ |
| Vienetas | trumpinta „Vnt.“ stulpelio antraštėje dėl vietos (pilnas žodis rodomas tooltip'e) |
| Kaina | rodoma be prielaidos „be PVM“ ar „su PVM“ — konkretus rodymas priklauso nuo to, ar įmonė yra PVM mokėtoja (žr. 8.2); jei ateityje atsiras kelios kainos, stulpelis rodys pagrindinę/numatytąją (žr. 12 skyrių) |
| PVM | procentinė reikšmė (pvz., „21%“); **stulpelis rodomas tik tada, kai įmonė yra PVM mokėtoja** (turi PVM kodą įmonės profilyje) — kitu atveju stulpelis lentelėje visai nerodomas, nes visos kainos jau yra be PVM |
| Būsena | badge: žalias „Aktyvi“ / pilkas „Neaktyvi“ |

## 7.2 Siūlomi nedidelis patobulinimai

* Kadangi stulpelių šioje lentelėje daugiau (8) nei Customer sąraše (7),
  siūlau **„Vienetas“ stulpelio antraštėje trumpinti į „Vnt.“**, o pilną
  reikšmę rodyti tik pačiose eilutėse ir tooltip'e — taupo horizontalią
  vietą, neprarandant informacijos.
* Kai lentelės plotis viršija lango darbo sritį, siūlau horizontalų
  slinkimą (scroll), o ne stulpelių praleidimą — nuoseklu su bendra
  „nesukurti netikėto duomenų praradimo iš akių“ nuostata.
* „Barkodas“ stulpelį siūlau derinti su galimybe rikiuoti/filtruoti pagal
  turėjimą barkodo (pvz., greita nuoroda „be barkodo“), bet tai — neprivalomas
  patobulinimas, ne šio etapo reikalavimas.

## 7.3 Rūšiavimas, pažymėjimas, dvigubas paspaudimas, klaviatūra

Identiška Customer modulio logika (žr. `CUSTOMER_MODULE_UI.md` 3.2–3.5):
* rūšiavimas spustelėjus antraštę, kryptis keičiasi pakartotinai spaudžiant;
* vienos eilutės pažymėjimas (single-select);
* dvigubas paspaudimas atidaro redagavimo langą;
* rodyklės aukštyn/žemyn keičia pažymėjimą, Enter atidaro redagavimą,
  Delete inicijuoja šalinimą su patvirtinimu, Tab tvarka atitinka vizualinę
  seką.

---

# 8. Redagavimo langas

Naudojama **ta pati skirtukų (tabs) architektūra**, kaip Customer modulyje
nuo v1.1 (žr. `CUSTOMER_MODULE_UI.md` 5.2) — antraštė su dirty indikatoriumi
→ skirtukai → fiksuota veiksmų juosta apačioje, bendra visiems skirtukams.

```text
[ Bendri duomenys ] [ Kainodara ] [ Barkodai ] [ Pastabos ]  [ Istorija (greitai) ] [ Dokumentai (greitai) ]
```

## 8.1 Bendri duomenys

* **Tipas** — segmentuotas perjungiklis „Prekė / Paslauga“, iš anksto
  nustatytas pagal tai, kurį veiksmų juostos mygtuką naudotojas paspaudė
  (žr. 4.1).
* **Pavadinimas** (privalomas).
* **Kodas**.
* **Kategorija** — **ne laisvas tekstas.** ComboBox su esamomis kategorijomis
  + galimybė sąmoningu atskiru veiksmu „+ Nauja kategorija...“ pridėti naują
  reikšmę. Įvedus tekstą kategorija automatiškai nekuriama. Tikslas —
  išvengti duomenų kokybės problemų (skirtingi to paties pavadinimo
  variantai, pvz., „Biuro prekės“ / „Biuro prekes“ / „Biuras“, kurie
  suskaidytų statistiką). Ilgainiui kategorijos turėtų tapti atskiru
  moduliu su savo valdymu — šis ComboBox yra pereinamasis sprendimas, kol
  to modulio nėra.
* **Vienetas** — išskleidžiamas sąrašas (vnt., kg, m, m², m³, val., mėn.,
  kompl. ir pan.). Vienetų sąrašas ateityje bus administruojamas atskirame
  modulyje — tai savas žodynas, ne laisvas UI pasirinkimas, analogiškai
  Kategorijai.

Kai pasirinktas tipas „Paslauga“, UI lygmenyje laukas „Vienetas“ gali rodyti
paslaugoms būdingesnes numatytąsias reikšmes (pvz., „val.“, „mėn.“) — tai
tik numatytosios reikšmės pasiūlymas, ne privalomas apribojimas, ir
nekeičia duomenų modelio.

## 8.2 Kainodara

**Skirtuko pavadinimas „Kainodara“** (architekto pastaba) — jis pakankamai platus, kad
ateityje netektų keisti skirtuko vardo pridedant nuolaidas, kelias kainas,
valiutą ar galiojimo datas (žr. 12 skyrių).

**Laukų rinkinys priklauso nuo to, ar įmonė yra PVM mokėtoja** — t. y. ar
`CompanyView` įmonės profilyje įvestas PVM kodas. Tai savininko patvirtintas
sprendimas: jei PVM kodo nėra, įmonė sąskaitas išrašo be PVM, todėl ir
prekių/paslaugų kainos rodomos be PVM skaidymo.

**Kai įmonės profilyje PVM kodas įvestas (PVM mokėtoja):**
* Kaina (be PVM)
* PVM tarifas — ComboBox: 21% / 9% / 5% / 0% / Ne PVM objektas
* Kaina su PVM — apskaičiuojama automatiškai, tik peržiūrai (read-only)

**Kai įmonės profilyje PVM kodo nėra (ne PVM mokėtoja):**
* Kaina — vienas laukas, be jokio PVM skaidymo
* „PVM tarifas“ laukas šiuo atveju **visai neberodomas** dialoge (ne tik
  pervadinamas ar užpilkinamas) — jo rodyti nėra prasmės, kai sąskaitos
  PVM neišskiria

Dėl šios priežasties UI tekste vartojamas neutralus žodis **„Kaina“**, be
prielaidos „be PVM“ ar „su PVM“ — konkretų atvaizdavimą lemia aukščiau
aprašyta sąlyga, kurią realiai nustato Service sluoksnis (pvz.,
`CompanyService`, patikrinantis, ar profilyje yra PVM kodas); UI tik
atvaizduoja atitinkamą lauko rinkinį.

**PVM tarifo ComboBox** (kai rodomas) siūlomas kaip pasirinkimas, o ne
laisvas procentinis skaičius — praktiškiau ir apsaugo nuo klaidingų
reikšmių: `21% / 9% / 5% / 0% / Ne PVM objektas`.

## 8.3 Barkodai

Skirtingai nei Customer module, šis skirtukas projektuojamas **iškart kaip
sąrašas, ne kaip vienas laukas** — analogiškai jau įgyvendintam Banko
sąskaitų komponentui `CompanyView` lange (žr. `UI_GUIDELINES.md` 11
skyrių). Tai leidžia ateityje pridėti kelis barkodus vienam įrašui, **jau
dabar neperprojektuojant skirtuko**:

* lentelė: Barkodas | Tipas (pvz., EAN-13) | Numatytas;
* veiksmai virš lentelės: **Pridėti**, taip pat Redaguoti/Šalinti eilutės
  lygyje (kaip tekstinės nuorodos, ne ikonos — nuoseklu su Company
  sprendimu dėl klaviatūros prieinamumo);
* rezervuota vieta būsimam „Generuoti barkodą“ veiksmui — šiame etape
  neįgyvendinama, tik nurodyta pastaba UI lygmenyje.

Pradiniam etapui gali užtekti ir vieno įrašo šiame sąraše — struktūra tam
netrukdo.

## 8.4 Pastabos

Didelis daugiaeilis tekstinis laukas, be simbolių limito UI lygmenyje —
identiškai Customer moduliui.

## 8.5 Istorija (rezervuota)

Neaktyvus skirtukas su užrašu „(greitai)“ — kaip Customer module. Ateityje
rodys keitimų/įvykių žurnalą konkrečiam įrašui.

## 8.6 Dokumentai (rezervuota) — architekto pasiūlymo įvertinimas

Architektas pasiūlė papildomą skirtuką „Dokumentai“, kuriame ateityje būtų
rodoma, kuriose sąskaitose/pasiūlymuose prekė ar paslauga buvo panaudota.

**UX įvertinimas: siūlau pridėti kaip atskirą rezervuotą skirtuką, ne
sujungti su „Istorija“.** Priežastis — tai konceptualiai skirtinga
informacija:

* **Istorija** — paties įrašo pakeitimų žurnalas (kas ir kada redagavo
  prekės kainą, pavadinimą ir pan.);
* **Dokumentai** — verslo ryšys su kitais objektais (kuriuose dokumentuose
  ši prekė panaudota) — tai susiję su `document_items` lentele
  (`DATABASE.md`), ne su pačiu prekės įrašu.

Laikant juos atskirai, naudotojui bus aiškiau, ko ieškoti kiekviename
skirtuke, ir ateityje jie galės būti įgyvendinti nepriklausomai vienas nuo
kito (pvz., „Istorija“ gali atsirasti anksčiau nei „Dokumentai“, jei
audito žurnalas paprastesnis įgyvendinti). Abu skirtukai šiame etape lieka
neaktyvūs su užrašu „(greitai)“.

---

# 9. Empty State

Numatytos **dvi atskiros būsenos**, kaip ir Customer module (žr.
`CUSTOMER_MODULE_UI.md` 8 skyrių), su ta pačia logika:

## 9.1 Sąrašas tuščias (nėra nė vieno įrašo apskritai)

* Tekstas: **„Kol kas nėra nei vienos prekės ar paslaugos.“**
* Vienas pagrindinis mygtukas: **„Sukurti pirmą įrašą“** (Primary).
  Paspaudus, atidaromas redagavimo langas su numatytuoju tipu „Prekė“
  (dažniausias atvejis); naudotojas gali pakeisti tipą pačiame skirtuke
  „Bendri duomenys“, jei iš tikrųjų kūrė paslaugą.

## 9.2 Nieko nerasta (pagal paiešką/filtrus)

* Tik informacinis pranešimas, **be** veiksmo mygtuko — pvz., „Pagal
  pasirinktus filtrus nieko nerasta.“ Taip išvengiama atsitiktinio
  dublikato sukūrimo, kai įrašų iš tikrųjų yra, tik jie neatitinka filtro.

---

# 10. Loading State

Identiška Customer/Company modulių logika (žr. `UI_GUIDELINES.md` 7
skyrių, `CUSTOMER_MODULE_UI.md` 9 skyrių): kraunant duomenis lentelės
vietoje rodomas užimtumo indikatorius, ne tuščia lentelė; paieškos ir
veiksmų mygtukai lieka matomi, gali būti laikinai neaktyvūs.

---

# 11. Dirty State ir dialogų elgsena

Naudojama **ta pati UX logika**, kaip Customer module, be pakeitimų:

* bet koks lauko pakeitimas bet kuriame skirtuke pažymi formą kaip dirty;
  indikatorius bendras visam dialogui, prie antraštės;
* „Išsaugoti“ aktyvus tik esant pakeitimų ir užpildytiems privalomiems
  laukams; po paspaudimo — Saving būsena, mygtukas laikinai neaktyvus;
* „Atšaukti“ grąžina paskutinę išsaugotą būseną;
* „Uždaryti“ su neišsaugotais pakeitimais rodo patvirtinimo dialogą
  („Turite neišsaugotų pakeitimų. Ar tikrai norite uždaryti neišsaugoję?“)
  su numatytuoju fokusu ant saugesnio veiksmo;
* šalinimo veiksmas (sąraše) — patvirtinimo dialogas su įrašo pavadinimu,
  numatytasis fokusas ant „Atšaukti“;
* po sėkmingo išsaugojimo — trumpas, automatiškai po ~3 s išnykstantis
  būsenos pranešimas.

---

# 12. Ateities plėtra

Šiame etape neprojektuojama detaliai — tik užtikrinama, kad struktūra
neblokuoja:

| Būsima funkcija | Kaip UI struktūra jai jau paruošta |
|---|---|
| Nuotraukos | „Bendri duomenys“ skirtuke gali būti rezervuota maža kvadratinė vieta šalia pavadinimo lauko (placeholder ikona); atskira nuotraukų galerija galėtų tapti nauju skirtuku |
| Keli barkodai | „Barkodai“ skirtukas jau projektuojamas kaip sąrašas (8.3), ne vienas laukas — plėtra nereikalauja perprojektavimo |
| Kelios kainos, nuolaidos, valiuta, galiojimas | „Kainodara“ skirtukas šiuo etapu rodo vieną kainą, bet pavadinimas jau pakankamai platus, kad ateityje priimtų kelias kainas, nuolaidas, valiutos pasirinkimą ar galiojimo datas — nekeičiant paties skirtuko pavadinimo ar vietos |
| Sandėlio likučiai | numatoma kaip galimas naujas skirtukas (pvz., „Likučiai“) arba papildomas stulpelis sąraše — šiame etape neįtraukiama |
| Serijiniai numeriai | analogiškai Barkodų sąrašui (8.3) — jei prekei reikės individualaus sekimo (elektronika, įrankiai, įranga, kompiuteriai), tas pats sąrašo komponentas gali būti pakartotinai panaudotas naujame skirtuke arba prijungtas prie Barkodų sąrašo struktūros |
| Keli PVM tarifai | šiuo metu vienas PVM laukas „Kainodara“ skirtuke; kontekstinis PVM (pvz., pagal šalį) būtų verslo logikos, o ne UI sprendimas, UI tik atvaizduotų papildomą pasirinkimą |
| Savikaina | ateities funkcija; Task 7.0B metu laukas nerodomas ir nėra privalomas |
| Importas / eksportas | rezervuojama vieta sąrašo veiksmų juostoje papildomam `⋯` meniu (perpildymo meniu), kad 4 esami mygtukai netaptų perkrauti naujais veiksmais |

---

# 13. Dizaino tikslų atitikimas

* **Kuo mažiau paspaudimų** — atskiri „Nauja prekė“/„Nauja paslauga“
  mygtukai iš karto atidaro formą su teisingu tipu (4.1); momentinė
  paieška be papildomo mygtuko.
* **Aiški darbo eiga** — ta pati sąrašas→forma→išsaugojimas seka, kaip
  Customer module, naudotojui nereikia mokytis naujos logikos.
* **Vientisumas su Customer moduliu** — identiškas išdėstymas, spalvos,
  tipografija, skirtukų architektūra, dirty state, dialogų elgsena.
* **Komponentų pakartotinis naudojimas** — sąrašo/filtrų/lentelės/formos/
  skirtukų/dialogų komponentai turėtų būti tie patys, tik su kitais
  duomenimis; Barkodų sąrašas pakartotinai naudoja jau įgyvendintą Banko
  sąskaitų sąrašo komponentą iš `CompanyView`.

---

# 14. Rekomendacijos programuotojui

* Sąrašo, filtrų, lentelės, dirty state ir dialogų komponentus rekomenduojama
  imti tiesiai iš `CustomerListView`/`CustomerEditView` realizacijos, keičiant
  tik duomenų šaltinį ir stulpelių/laukų sąrašą — ne kurti iš naujo.
  Skirtukų (tabs) komponentas, jei jau sukurtas Customer moduliui, turėtų
  būti bendras, pakartotinai naudojamas UI elementas (žr.
  `CUSTOMER_MODULE_UI.md` 11.1).
  „Barkodai“ skirtuko sąrašo komponentą rekomenduojama imti iš jau
  įgyvendinto Banko sąskaitų komponento (`CompanyView`), nes struktūra
  (pridėti/redaguoti/šalinti eilutę, „numatytas“ žymė) sutampa.
* Validacijos taisyklės (kurie laukai iš tikrųjų privalomi, kainos
  formatas, PVM tarifo galiojimas) tvirtinamos ir įgyvendinamos `Service`
  sluoksnyje pagal `ARCHITECTURE.md`; UI tik atvaizduoja grąžintas klaidas.
* „Kategorija“ realizuojama tik kaip valdomas pasirinkimas iš kategorijų
  duomenų šaltinio su sąmoningu atskiru naujos reikšmės pridėjimo veiksmu.
  Laisvas tekstas ir automatinis kategorijos sukūrimas įvedant reikšmę
  nenaudojami.
* „Savikaina“ yra ateities funkcija: Task 7.0B metu šis laukas nerodomas ir
  nėra privalomas.

---

# 15. Versijų istorija

| Versija | Data | Patvirtino | Pakeitimai |
|---|---|---|---|
| 1.1 | 2026-07-19 | Architektas, Savininkas | Kategorija pakeista iš laisvo teksto į ComboBox su nauja reikšme; Vienetas papildytas pastaba dėl būsimo atskiro modulio; patvirtintas skirtuko pavadinimas „Kainodara“; Kaina/PVM tarifas padaryti sąlyginiai pagal įmonės PVM kodo buvimą profilyje; PVM tarifo laukas visai nerodomas, jei įmonė nėra PVM mokėtoja; pridėti Serijiniai numeriai prie ateities plėtros; patvirtinti be pakeitimų: Barkodai, Dokumentai, Nuotraukos, Import/Export. |
| 1.0 | 2026-07-19 | — | Sukurta pradinė Prekių ir paslaugų modulio UI specifikacija: sąrašo langas, veiksmų juosta, paieška, filtrai, lentelė, redagavimo langas su skirtukais (įskaitant rezervuotus „Istorija“ ir „Dokumentai“), Barkodų sąrašo komponentas, Empty/Loading/Dirty būsenos, ateities plėtros analizė, UX pastabos programuotojui. |
