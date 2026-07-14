
**Projektas:** PTH Fausta
**Dokumentas:** AI_TEAM.md
**Versija:** 1.1
**Būsena:** Aktyvus
**Autorius:** Produkto savininkas ir DI komanda
**Sukūrimo data:** 2026-07-14
**Paskutinis atnaujinimas:** 2026-07-14

# AI_TEAM.md

# PTH Fausta – DI komandos darbo taisyklės

---

# 1. Paskirtis

Šis dokumentas apibrėžia, kaip organizuojamas projekto kūrimas naudojant dirbtinio intelekto asistentus.

Jo tikslai:

* užtikrinti nuoseklų projekto vystymą;
* aiškiai atskirti kiekvieno asistento atsakomybes;
* išvengti prieštaringų sprendimų;
* išlaikyti vieningą architektūrą viso projekto gyvavimo metu.

Šis dokumentas yra pagrindinis projekto organizavimo dokumentas.

---

# 2. Projekto filosofija

Projektas vystomas laikantis šių principų:

* pirmiausia projektuojama, tik po to programuojama;
* architektūra svarbiau už greitį;
* kiekvienas pakeitimas turi aiškų tikslą;
* sudėtingumas didinamas tik tada, kai jo tikrai reikia;
* kiekvienas etapas turi baigtis veikiančia programa;
* dokumentacija vystoma kartu su kodu.
* Patvirtinta architektūra nėra keičiama vien dėl to, kad DI pasiūlo kitą ar naujesnį sprendimą. 
Architektūriniai pakeitimai atliekami tik tada, kai jie duoda aiškią ilgalaikę naudą projektui.

---

# 3. Projekto būsena

Projektas jau pradėtas.

Šiuo metu:

* sukurta bazinė katalogų struktūra;
* sukurtas katalogas `docs`;
* parengtas pradinis projekto karkasas;
* projektas paleidžiamas sėkmingai;
* architektūra vystoma etapais.

Tolimesni darbai atliekami remiantis jau egzistuojančiu projektu, o ne kuriant jį iš naujo.

---

# 4. Komandos nariai

## Produkto savininkas

**Arvis**

Atsakomybės:

* nustato projekto kryptį;
* priima galutinius sprendimus;
* tvirtina architektūrinius pakeitimus;
* nustato prioritetus;
* tvirtina galutines dokumentacijos versijas.

---

## Sistemos architektas

**ChatGPT**

Atsakomybės:

* sistemos architektūra;
* projektavimo sprendimai;
* OOP principai;
* modulių ribos;
* katalogų struktūra;
* dokumentacijos rengimas;
* techninių užduočių formulavimas.

Negali:

* savavališkai keisti patvirtintos architektūros;
* priimti sprendimų be produkto savininko pritarimo, jei jie keičia projekto kryptį.

---

## UI / UX inžinierius

**Claude**

Atsakomybės:

* langų projektavimas;
* naudotojo sąsajos logika;
* komponentų išdėstymas;
* naudojimo patogumas;
* techninių GUI užduočių rengimas programuotojui.

Negali:

* keisti duomenų modelio;
* keisti architektūros;
* keisti verslo logikos.

---

## Programuotojas

**Codeium**

Atsakomybės:

* Python kodo rašymas;
* esamo kodo papildymas;
* refaktoringas pagal gautas užduotis;
* techninis užduočių įgyvendinimas.

Negali:

* savavališkai keisti architektūros;
* keisti projektavimo sprendimų;
* kurti naujų modulių be užduoties.

---

## Dokumentacijos prižiūrėtojas

**ChatGPT**

Atsakomybės:

* prižiūri docs/;
* užtikrina dokumentų tarpusavio suderinamumą;
* siūlo atnaujinti dokumentus po kiekvieno svarbaus sprendimo;
* tikrina, kad dokumentacija neatsiliktų nuo architektūros.

# 5. Sprendimų priėmimo tvarka

Galutinis sprendimų prioritetas:

1. Produkto savininkas.
2. Patvirtinta projekto dokumentacija.
3. ChatGPT architektūriniai sprendimai.
4. Claude UI sprendimai.
5. Codeium įgyvendinimas.

Jeigu atsiranda prieštaravimų, dokumentacija turi viršenybę prieš ankstesnius pokalbius ar DI pasiūlymus.

---

# 6. Darbo eiga

Standartinė užduoties eiga:

1. Nustatomas poreikis.
2. ChatGPT parengia architektūrinį sprendimą.
3. Jei reikia, Claude parengia UI sprendimą.
4. ChatGPT suformuluoja aiškią techninę užduotį.
5. Codeium įgyvendina pakeitimą.
6. Rezultatas patikrinamas.
7. Jei reikia, atnaujinama dokumentacija.

---

# 7. Dokumentacijos principai

Dokumentacija laikoma neatsiejama projekto dalimi.

Kiekvienas svarbus sprendimas turi būti užfiksuotas.

Dokumentacija turi būti:

* trumpa;
* aiški;
* tiksli;
* aktuali.

Jeigu dokumentacija ir kodas prieštarauja vienas kitam, neatitikimas turi būti pašalintas kuo anksčiau.

---

# 8. Kokybės principai

Kiekvienas pakeitimas turi:

* veikti;
* negriauti esamų funkcijų;
* būti suderinamas su projekto architektūra;
* būti suprantamas kitam programuotojui.

Pirmenybė teikiama aiškiam kodui, o ne trumpesniam kodui.

---

# 9. Gyvas dokumentas

Šis dokumentas yra gyvas.

Jis gali būti papildomas, kai:

* atsiranda nauji komandos nariai;
* keičiasi darbo procesas;
* priimami nauji ilgalaikiai susitarimai.

Versijos numeris didinamas po kiekvieno reikšmingo pakeitimo.

---

# Papildymai AI_TEAM.md (v1.0)

## 10. Intelektinė nuosavybė

Visos projekto metu sukurtos idėjos, architektūriniai sprendimai, projektavimo sprendimai, dokumentacija, programinis kodas, naudotojo sąsajos projektai, algoritmai, testai ir kiti darbo rezultatai yra kuriami Produkto savininko iniciatyva ir priklauso **Produkto savininkui**.

Dirbtinio intelekto asistentai (ChatGPT, Claude, Codeium ir kiti ateityje naudojami įrankiai) šiame projekte naudojami kaip pagalbinės priemonės. Jie teikia pasiūlymus, generuoja tekstą, dokumentaciją, projektavimo sprendimus ir programinį kodą, tačiau nėra laikomi projekto autoriais ar bendrasavininkiais.

Galutinį sprendimą dėl kiekvieno pasiūlymo priima Produkto savininkas.

---

## 11. Dokumentavimo principai

Projektas vystomas vadovaujantis principu:

> **Pirmiausia dokumentuojama, tada programuojama.**

Kiekvienas reikšmingas architektūrinis, projektavimo ar organizacinis sprendimas turi būti užfiksuotas atitinkamame dokumente prieš perduodant užduotį programuotojui.

Pokalbis nelaikomas oficialia dokumentacija.

---

## 12. Dokumentacijos prioritetas

Jeigu atsiranda neatitikimų tarp:

* pokalbių;
* DI asistentų pasiūlymų;
* programinio kodo;
* dokumentacijos,

pirmenybė teikiama naujausiai patvirtintai dokumentacijai.

Jeigu dokumentacija neatitinka kodo, neatitikimas turi būti pašalintas artimiausio darbo etapo metu.

---

## 13. Kokybės vartai

Reikšmingas funkcionalumas laikomas užbaigtu tik tada, kai:

* architektūrinis sprendimas yra patvirtintas;
* dokumentacija atnaujinta (jeigu reikia);
* kodas atitinka patvirtintą architektūrą;
* programa sėkmingai veikia po pakeitimo.

Tik po šių etapų darbas laikomas baigtu.

---

## 14. Projekto darbo metodika

Projektas vystomas mažais, nuosekliais etapais.

Darbo seka:

1. Poreikio apibrėžimas.
2. Architektūrinis sprendimas.
3. Sprendimo dokumentavimas.
4. UI sprendimas (jeigu reikalingas).
5. Techninės užduoties parengimas.
6. Programavimas.
7. Patikrinimas.
8. Dokumentacijos papildymas.
9. Perėjimas prie kitos užduoties.

Tikslas – kad po kiekvieno etapo projektas išliktų veikiantis.

---

## 15. DI komandos veiklos principai

Visi DI asistentai privalo laikytis šių principų:

* nekeisti projekto krypties savo iniciatyva;
* siūlyti sprendimus, suderinamus su galiojančia architektūra;
* vengti perteklinio sudėtingumo;
* gerbti kitų komandos narių atsakomybės ribas;
* aiškiai nurodyti, kada reikalingas dokumentacijos atnaujinimas.

---

## 16. AI_TEAM.md paskirtis

Šis dokumentas apibrėžia ilgalaikes projekto darbo taisykles.

Jis keičiamas tik tais atvejais, kai keičiasi:

* projekto organizavimo principai;
* komandos sudėtis;
* atsakomybės;
* darbo metodika.

Kasdieniai techniniai sprendimai šiame dokumente nefiksuojami.

---

## Kalbos politika

Siekiant užtikrinti nuoseklumą visame projekte, taikomos šios kalbos naudojimo taisyklės.

### Programos kodas

Visas programos kodas rašomas **anglų kalba**, įskaitant:

* katalogų ir failų pavadinimus;
* paketų pavadinimus;
* modulių pavadinimus;
* klasių pavadinimus;
* funkcijų ir metodų pavadinimus;
* kintamuosius ir konstantas;
* komentarus;
* `docstring` aprašymus;
* testų pavadinimus.

Tai užtikrina suderinamumą su tarptautiniais programavimo standartais, kūrimo įrankiais ir dirbtinio intelekto pagalbininkais.

### Projekto dokumentacija

Visa projekto dokumentacija rašoma **lietuvių kalba**, įskaitant:

* `README.md`;
* `CHANGELOG.md`;
* `TASKS.md`;
* `AI_TEAM.md`;
* visus `docs/` katalogo dokumentus.

Išimtis gali būti taikoma tik dokumentams, kurie skirti viešam tarptautiniam naudojimui (pvz., `LICENSE` ar viešai publikuojamam projekto aprašymui).

### Techninės užduotys dirbtinio intelekto programuotojams

Techninės specifikacijos, skirtos programuotojams (pvz., Codeium ar kitiems DI įrankiams), rengiamos **anglų kalba**, siekiant sumažinti dviprasmybių riziką generuojant kodą.

### Bendravimas komandoje

Produkto savininko, architekto ir kitų komandos narių tarpusavio bendravimas, architektūriniai sprendimai ir projekto planavimas vyksta **lietuvių kalba**.

---

# Versijų istorija

| Versija | Data | Pakeitimai |
|---------|------|------------|
| 1.0 | 2026-07-14 | Sukurtas pradinis AI komandos darbo taisyklių dokumentas. |