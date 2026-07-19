CUSTOMER_MODULE_UI.md

Projektas: PTH FaustaDokumentas: CUSTOMER_MODULE_UI.mdUžduotis: Task 6.0A – Customer Module UI DesignVersija: 1.1Būsena: PatvirtintaAutorius: Claude (UI/UX inžinierius)Sukūrimo data: 2026-07-18Paskutinis atnaujinimas: 2026-07-18 (v1.1 – architekto pastabų taikymas, savininko patvirtinimas)

1. Paskirtis

Šis dokumentas apibrėžia pilną Klientų (Customers) modulio naudotojo sąsają:sąrašo langą, lentelę, veiksmų juostą, redagavimo formą, dirty state elgsenąir tuščios būsenos ekraną.

Dokumentas remiasi UI_GUIDELINES.md (spalvos, tipografija, komponentai,būsenos, prieinamumas) ir DATABASE.md clients lentelės laukais. Jokienauji duomenų laukai čia nesiūlomi ir architektūra nekeičiama — tai grynaiUI/UX sprendimas.

2. Klientų sąrašo langas

2.1 Išdėstymas (iš viršaus žemyn)

┌──────────────────────────────────────────────────────────┐
│ Klientai                              [+Naujas][Redaguoti][Šalinti] │
│ Tvarkykite klientų sąrašą...                              │
├──────────────────────────────────────────────────────────┤
│ [Paieška.......]  [Būsena ▾] [Tipas ▾]        24 klientai │
├──────────────────────────────────────────────────────────┤
│ Pavadinimas │ Įm.kodas │ PVM │ Tel. │ El.paštas │ Miestas │ Būsena │
│ ...lentelės eilutės arba tuščia/įkėlimo būsena...          │
└──────────────────────────────────────────────────────────┘

Antraštė (H1) – „Klientai“ + trumpas aprašomasis tekstas (Small,color-text-secondary) apie modulio paskirtį.

Veiksmų juosta – dešinėje, tame pačiame lygyje kaip antraštė.

Paieška ir filtrai – atskira eilutė po antrašte, prieš lentelę.

Lentelė užima likusią darbo srities vietą, su vidiniu slinkimu, jeieilučių daugiau nei telpa.

Dešinėje virš lentelės — bendras klientų skaičius (Small,color-text-secondary).

2.2 Paieška ir filtrai

Paieškos lauko placeholder — „Ieškoti kliento...“ (trumpa, nesnaudotojui nesvarbu, pagal kuriuos konkrečiai laukus vyksta paieška —sistema pati ieško pagal search_text principą, žr. DATABASE.md:pavadinime, kode, PVM kode, telefone, el. paštu, adrese).

Filtrai išdėstyti šia tvarka: Tipas (Visi / Juridinis / Fizinis), tadaBūsena (Visi / Aktyvus / Neaktyvus). Tvarka atitinka natūraliąnaudotojo mąstymo seką dirbant su klientais — pirmiausia tipas, tik po tobūsena. Abu — išskleidžiami sąrašai (combo box), ne atskiri mygtukai.

Paieška ir filtrai veikia kartu (loginis IR), atnaujina lentelę iš karto,be atskiro „Ieškoti“ mygtuko.

2.3 Klientų skaičius

Bendras klientų skaičius (pvz., „24 klientai“) rodomas būsenos juostojeapačioje, ne virš lentelės — tai bendra sistemos informacija, atitinkantiWindows darbalaukio programų įprotį (žr. Main Window būsenos juostą,UI_GUIDELINES.md 10 skyrius). Skaičius atsinaujina kartu su filtrais(rodo matomų, o ne visų DB įrašų kiekį).

3. Lentelė

3.1 Stulpeliai

Stulpelis

DB laukas

Pastaba

Pavadinimas

name

pagrindinis identifikuojantis stulpelis

Kodas

company_code

trumpinta iš „Įmonės kodas“ dėl vietos taupymo lentelėje; tuščias laukas rodomas kaip „—“. Patvirtinta Produkto savininko 2026-07-18.

PVM kodas

vat_code

tuščias laukas rodomas kaip „—“

Telefonas

phone



El. paštas

email



Miestas

city



Būsena

status

badge: žalias „Aktyvus“ / pilkas „Neaktyvus“

3.2 Rūšiavimas

Numatytasis rūšiavimas — pagal Pavadinimą, didėjančiai (A→Z).

Spustelėjus stulpelio antraštę — rūšiuojama pagal tą stulpelį; pakartotinaspaspaudimas keičia kryptį. Aktyvus rūšiavimo stulpelis žymimas rodykle(▲/▼) antraštėje.

Antraštė pasiekiama klaviatūra (Tab), rūšiavimas suveikia Enter/Space.

3.3 Pažymėjimas

Vienos eilutės pažymėjimas (single-select) pirmajam etapui — atitinkaveiksmų juostos loginiką (Redaguoti/Šalinti veikia su vienu klientu).

Pažymėta eilutė — fonas color-row-selected (#E6F1FB), tekstas#0C447C, pagal UI_GUIDELINES.md.

Kelių eilučių pažymėjimas (žymimieji langeliai, masiniai veiksmai) —galima ateities plėtra, šiame etape neprojektuojama.

3.4 Dvigubas paspaudimas

Dvigubas paspaudimas ant eilutės atidaro tos pačios eilutės klientoredagavimo langą — lygiavertis veiksmas mygtukui „Redaguoti“.

3.5 Klaviatūros navigacija

Rodyklės Aukštyn/Žemyn — perkelia pažymėjimą tarp eilučių.

Enter ant pažymėtos eilutės — atidaro redagavimo langą (kaip dvigubaspaspaudimas).

Delete klavišas ant pažymėtos eilutės — inicijuoja šalinimo veiksmą(su tuo pačiu patvirtinimo dialogu, kaip mygtukas „Šalinti“).

Tab tvarka: Paieška → Būsenos filtras → Tipo filtras → veiksmų mygtukai→ lentelė (antraštės → eilutės).

4. Veiksmų juosta (sąrašo lange)

Mygtukas

Tipas

Aktyvus, kai

Naujas klientas

Primary

visada

Redaguoti

Secondary

pažymėta lygiai viena eilutė

Šalinti

Danger

pažymėta lygiai viena eilutė

4.1 Šalinimo patvirtinimo dialogas

Modalinis dialogas: „Ar tikrai norite pašalinti klientą {pavadinimas}?Šio veiksmo nebus galima atšaukti.“

Mygtukai: Atšaukti (secondary, numatytasis fokusas) / Šalinti(danger). Numatytasis fokusas ant „Atšaukti“, kad atsitiktinis Enterpaspaudimas nepašalintų kliento (pagal UI_GUIDELINES.md 8 skyrių).

Esc uždaro dialogą be pašalinimo.

5. Kliento redagavimo langas

Atidaromas kaip modalinis dialogas virš sąrašo lango — ta pati schema,kaip jau įgyvendinta CompanyView.

5.1 Antraštė

„Naujas klientas“ (kuriant) arba „Redaguoti klientą“ (redaguojant).

Šalia antraštės — dirty state indikatorius (žr. 6 skyrių), rodomas tikkai yra neišsaugotų pakeitimų.

5.2 Struktūra: skirtukai (tabs), ne vienas slenkantis puslapis

Pakeitimas nuo v1.0: pirminėje versijoje visi blokai buvo vienojeslenkančioje formoje. Architekto pastaba priimta — pereinama prieskirtukų (tabs), nes:

kliento kortelė ateityje neišvengiamai augs (Skolos, Dokumentai, Istorija,Mokėjimai ir kt.);

jei dabar liktų vienas ilgas puslapis, vėliau tektų perprojektuoti visąišdėstymą; su skirtukais nauja informacija tiesiog prideda naują skirtuką,nekeičiant esamos struktūros;

tai suvienodina šabloną su būsimais ProductView, UserView ir pan. —visi „kortelės tipo“ langai naudos tą pačią skirtukų architektūrą.

Skirtukai:

[ Duomenys ] [ Kontaktai ] [ Adresas ] [ Pastabos ]  [ Istorija (greitai) ]

Duomenys — Kliento tipas (segmentuotas perjungiklis „Juridinisasmuo / Fizinis asmuo“, atitinka client_type), Pavadinimas (privalomas),Kodas (privalomas juridiniam asmeniui, atitinka company_code), PVMkodas (neprivalomas). Perjungiant tipą į „Fizinis asmuo“, UI lygmenyjegali paslėpti „Kodas“/„PVM kodas“ laukus — tai atvaizdavimo elgsena, DBlaukų sudėties nekeičia.

Kontaktai — Telefonas, El. paštas.

Adresas — Gatvė (address), Miestas (city), Pašto kodas(postal_code), Šalis (country_code, numatytoji „Lietuva“).

Pastabos — didelis daugiaeilis tekstinis laukas (notes), besimbolių limito UI lygmenyje.

Istorija — rezervuota, neaktyvi skirtuko vieta su užrašu „(greitai)“;neįgyvendinama šiame etape (žr. 11 skyrių).

Visi privalomi laukai žymimi raudonu *, pagal UI_GUIDELINES.md 6.2.

5.3 Dirty state ir skirtukai

Dirty indikatorius (žr. 7 skyrių) lieka bendras visam dialogui,rodomas prie antraštės, nepriklausomai nuo to, kuriame skirtuke pakeitimaspadarytas — naudotojui nereikia atsiminti, kuriame skirtuke likoneišsaugotų duomenų.

Fiksuota veiksmų juosta apačioje (Uždaryti / Atšaukti / Išsaugoti) yrabendra visiems skirtukams — nesikeičia perjungiant tarp jų.

Galima ateities plėtra (neprivaloma dabar): mažas indikatorius ant patiesskirtuko pavadinimo, rodantis, kuriame konkrečiai skirtuke yraneišsaugotų pakeitimų.

6. Veiksmų juosta (redagavimo lange)

Fiksuota juosta apačioje (ne slenkanti su turiniu):

[Uždaryti]                      [Atšaukti] [Išsaugoti]

Ta pati logika, kaip CompanyView:

Išsaugoti (Primary) — aktyvus tik esant faktinių pakeitimų (dirty) IRprivalomiems laukams užpildytiems; po paspaudimo — Saving būsena(žr. UI_GUIDELINES.md 7 skyrių), mygtukas laikinai neaktyvus, kadneįvyktų dvigubas išsaugojimas.

Atšaukti — grąžina paskutinę išsaugotą būseną, formos langas liekaatidarytas.

Uždaryti — uždaro dialogą; jei yra neišsaugotų pakeitimų, prieš tairodomas patvirtinimo dialogas (žr. 6 skyrių žemiau).

7. Dirty State

7.1 Pakeitimų aptikimas

Bet koks lauko pakeitimas (tekstas, pasirinkimas, tipo perjungimas)pažymi formą kaip „dirty“, lyginant su paskutine išsaugota reikšme.

Dirty būsena rodoma:

mažu indikatoriumi šalia antraštės („● Neišsaugoti pakeitimai“,color-warning, tekstas + spalva — ne vien spalva);

„Išsaugoti“ mygtuko aktyvavimu.

7.2 Uždarymo dialogas

Bandant uždaryti langą (mygtuku „Uždaryti“, „X“, Esc arba pereinant įkitą sidebar punktą) su neišsaugotais pakeitimais — rodomas patvirtinimodialogas: „Turite neišsaugotų pakeitimų. Ar tikrai norite uždarytineišsaugoję?“

Mygtukai: Grįžti į formą (secondary, numatytasis fokusas) / Uždarytineišsaugant (danger).

7.3 Sėkmės pranešimas

Po sėkmingo išsaugojimo — trumpas būsenos pranešimas („Klientasišsaugotas“), rodomas viršuje arba apačioje kaip nemodalinis pranešimas(toast/banner), automatiškai išnykstantis po ~3 sekundžių, be naudotojoveiksmo.

8. Empty State (sąrašo lange)

Kai klientų sąraše nėra nė vieno įrašo:

Paieškos ir filtrų juosta lieka matoma, bet neaktyvi (jei tuščia dėl to,kad klientų iš viso nėra, o ne dėl filtro — žr. pastabą 8.1);

centre rodoma:

apskritas ikonos ženklas (neutralus, ne klaidos spalva);

tekstas: „Kol kas nėra nė vieno kliento.“;

papildomas paaiškinimas (Small, secondary tekstas);

vienas pagrindinis mygtukas: „Sukurti pirmą klientą“ (Primary),atidarantis tą patį redagavimo langą kaip „Naujas klientas“.

8.1 Skirtumas nuo „nieko nerasta pagal filtrą“

Jei klientų yra, bet paieška/filtras negrąžina rezultatų, rodomas kitoks,neutralus tekstas („Pagal pasirinktus filtrus klientų nerasta.“) be„Sukurti pirmą klientą“ mygtuko, kad naudotojas neperkurtų egzistuojančiokliento. Tai dvi skirtingos empty-state variacijos, ne viena.

9. Įkėlimo (loading) būsena

Kraunant klientų sąrašą — lentelės vietoje rodomas užimtumo indikatorius,ne tuščia lentelė ir ne „nėra klientų“ tekstas.

Paieškos ir veiksmų mygtukai lieka matomi, bet gali būti laikinaineaktyvūs, kol duomenys kraunami.

10. Navigacija

Klientų modulis rodomas pagrindiniame programos lange (MainView darbosrityje), pasiekiamas per sidebar punktą „Klientai“ — taip, kaip apibrėžtaUI_GUIDELINES.md 9 skyriuje.

Papildomo „Atgal“ mygtuko nereikia — tai ne atskiras dialogas, onuolatinis darbo srities turinys; grįžimas vyksta pasirenkant kitąsidebar punktą.

Kliento redagavimo langas atidaromas kaip modalinis dialogas viršsąrašo (tokia pati schema kaip CompanyView), nes tai laikinas,užduočiai skirtas kontekstas, o ne nuolatinis navigacijos taškas.

11. Pritaikymas ateičiai

Nuo v1.1 redagavimo langas naudoja skirtukų (tabs) struktūrą (žr. 5.2), kuripati savaime yra pritaikymo ateičiai mechanizmas — nauja informacija pridedamakaip naujas skirtukas, neperprojektuojant esamos struktūros. Šiame etapeneprojektuojama detaliai, tik rezervuojama vieta:

skirtukas „Istorija“ jau įtrauktas į karkasą kaip neaktyvus, su užrašu„(greitai)“;

būsimam turiniui numatomos šios sritys (be detalaus UI dabar):

dokumentų istorija;

skolų informacija;

paskutinis dokumentas;

pirkimų statistika;

mokėjimai.

sąrašo lentelėje ateityje gali atsirasti papildomi neprivalomi stulpeliai(pvz., „Paskutinis dokumentas“, „Skola“) — dabartinis stulpelių sąrašastam nekliudo, nes lentelė projektuojama kaip plečiama.

11.1 Pakartotinai naudojamas šablonas

Redagavimo lango schema (antraštė + dirty indikatorius → skirtukai →fiksuota veiksmų juosta) sąmoningai suprojektuota vienoda CompanyViewir CustomerView languose. Tikslas — kad ta pati schema būtų pakartotinainaudojama būsimuose moduliuose (ProductView, UserView ir kt.), taipsumažinant bendrą programos sudėtingumą ir palengvinant programuotojo darbą,nes kiekvienam naujam „kortelės tipo“ langui nereikia iš naujo projektuotielgsenos taisyklių.

12. Naudotojo scenarijai

12.1 Naujo kliento sukūrimas

Naudotojas sidebar meniu pasirenka „Klientai“.

Spaudžia „Naujas klientas“ (arba „Sukurti pirmą klientą“, jei sąrašastuščias).

Atsidaro redagavimo langas su tuščiais laukais.

Pildo bent privalomus laukus (Pavadinimas, Įmonės kodas, jei tipasJuridinis).

Spaudžia „Išsaugoti“ → rodoma Saving būsena → sėkmės pranešimas →dialogas gali likti atidarytas arba užsidaryti (sprendžia programuotojaspagal CompanyView esamą elgesį).

12.2 Esamo kliento redagavimas

Naudotojas pažymi eilutę lentelėje (paspaudimu arba klaviatūra).

Spaudžia „Redaguoti“ arba dukart spusteli eilutę.

Atsidaro redagavimo langas su užpildytais duomenimis.

Pakeitus bent vieną lauką, atsiranda dirty indikatorius, aktyvuojasi„Išsaugoti“.

Jei naudotojas bando uždaryti langą neišsaugojęs — rodomas patvirtinimodialogas (7.2).

12.3 Kliento šalinimas

Naudotojas pažymi eilutę.

Spaudžia „Šalinti“ (arba Delete klavišą).

Rodomas patvirtinimo dialogas su kliento pavadinimu.

Patvirtinus — klientas pašalinamas, sąrašas atnaujinamas, rodomas trumpasbūsenos pranešimas.

12.4 Pirmas atidarymas (tuščias sąrašas)

Naudotojas pirmą kartą atidaro „Klientai“.

Matomas Empty State su pagrindiniu mygtuku „Sukurti pirmą klientą“.

Toliau — kaip 12.1 scenarijus.

13. Rekomendacijos programuotojui

Lentelės, filtrų ir dirty state logiką rekomenduojama įgyvendintipakartotinai naudojant tuos pačius komponentus/šablonus, kurie jausukurti CompanyView (dirty state mechanizmas jau yra — žr. kontekstą),kad nebūtų dubliuojamas kodas tarp modulių.

Rekomenduojama skirtukų (tabs) komponentą redagavimo languose sukurti kaipvieną bendrą, pakartotinai naudojamą UI elementą (ne atskirai kiekvienamlangui), nes ta pati struktūra numatoma ir būsimiems ProductView,UserView bei kitiems „kortelės tipo“ langams (žr. 11.1).

Šioje specifikacijoje aprašytos tik UI elgsenos taisyklės. Validacijostaisyklės (kurie laukai iš tikrųjų privalomi, formatų tikrinimas) turibūti tvirtinamos ir įgyvendinamos Service sluoksnyje pagalARCHITECTURE.md priklausomybių taisykles — UI tik atvaizduoja klaidas,kurias grąžina verslo sluoksnis.

Kliento tipo lauko (Fizinis/Juridinis) sąlyginis laukų rodymas/slėpimasyra grynai UI lygmens elgsena ir neturi įtakos clients lentelėsstruktūrai, apibrėžtai DATABASE.md.

Prieš įgyvendinant, rekomenduojama patikrinti šią specifikaciją suarchitektu dėl client_type reikšmių pavadinimų (pvz., ar DB saugomakaip individual/company, ar kitaip) — tai daro architektas, ne UIsluoksnis.

14. Versijų istorija

Versija

Data

Patvirtino

Pakeitimai

1.1

2026-07-18

Savininkas

Sutrumpintas paieškos placeholder („Ieškoti kliento...“); filtrai sukeisti (Tipas → Būsena); klientų skaičius perkeltas į būsenos juostą; lentelės stulpelis „Įmonės kodas“ → „Kodas“ (patvirtinta savininko); redagavimo langas pertvarkytas iš vieno slenkančio puslapio į skirtukų (tabs) struktūrą su rezervuota „Istorija“ vieta; papildyta pastaba apie pakartotinai naudojamą CompanyView/CustomerView šabloną.

1.0

2026-07-18

—

Sukurta pradinė Klientų modulio UI specifikacija: sąrašo langas, lentelė, veiksmų juosta, redagavimo forma, dirty state, empty state, navigacija, pritaikymas ateičiai, naudotojo scenarijai.
