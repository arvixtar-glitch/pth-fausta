# DOCUMENT_MODULE_UI.md

# PTH Fausta – Document Module UI Specification

---

**Projektas:** PTH Fausta

**Dokumentas:** DOCUMENT_MODULE_UI.md

**Versija:** 1.0

**Būsena:** Patvirtinta

**Autorius:** Architecture Team

**Dokumento tipas:** UI Specification

**Atitinka:**

- DOCUMENT_DOMAIN.md
- DATABASE.md
- UI_GUIDELINES.md
- CODING_STANDARDS.md

---

# 1. Purpose

Šis dokumentas apibrėžia oficialią Document modulio vartotojo sąsajos (UI) specifikaciją.

Jis nustato:

- dokumentų sąrašo langą;
- dokumento darbo langą;
- navigaciją;
- valdiklius;
- vartotojo veiksmus;
- būsenų atvaizdavimą;
- validacijos rodymą.

Šis dokumentas neaprašo verslo logikos.

Verslo logika apibrėžta DOCUMENT_DOMAIN.md.

---

# 2. General Principles

Sistema naudoja vieną bendrą Document modulį.

Skirtingi dokumentų tipai:

- Sąskaita faktūra
- Išankstinė sąskaita
- Komercinis pasiūlymas
- eBay sąskaita

naudoja tą pačią darbo sritį.

UI prisitaiko prie pasirinkto DocumentType.

---

# 3. Navigation

Pagrindinė navigacija:

```
Main Window
    │
    └── Dokumentai
            │
            ├── Document List
            │
            └── Document Workspace
```

Darbo sritis visada atidaroma iš sąrašo.

---

# 4. Document List

Dokumentų sąrašas pateikia visus dokumentus.

Rodomi stulpeliai:

- Numeris
- Tipas
- Data
- Pirkėjas
- Suma
- Mokėjimo būsena
- Gyvavimo būsena

Juodraščiai vietoje numerio rodo:

```
Draft
```

---

# 5. Search and Filters

Turi būti:

- paieška
- dokumento tipas
- būsena
- datos intervalas

Paieška vykdoma per search_text.

---

# 6. Toolbar

Pagrindiniai veiksmai:

- Naujas
- Atidaryti
- Kopijuoti
- Atšaukti
- Atnaujinti

Būsimi:

- PDF
- Spausdinti
- El. paštas
- QR

Gali būti nerodomi arba išjungti.

---

# 7. Document Workspace

Darbo sritis susideda iš blokų.

## Header

- DocumentType
- Data
- Mokėjimo terminas
- Numeris
- Serija

Numeris Draft režime nerodomas.

---

## Seller

Rodoma:

- pavadinimas
- kodas
- PVM kodas
- adresas
- telefonas
- el. paštas
- bankas
- IBAN

---

## Buyer

Rodoma:

- pavadinimas
- kodas
- PVM kodas
- adresas
- telefonas
- el. paštas

---

## Document Lines

Lentelės stulpeliai:

- Nr.
- Prekė / paslauga
- Mato vnt.
- Kiekis
- Kaina
- PVM
- Suma

Leidžiama:

- pasirinkti produktą;
- įvesti rankinę eilutę;
- redaguoti nukopijuotus produkto duomenis.

---

## Totals

Rodoma:

- Tarpinė suma
- Nuolaida
- PVM
- Galutinė suma

Visos sumos yra tik skaitomos.

---

## Notes

Laisvo teksto pastabos.

---

## Reserved Area

Rezervuota vieta:

- QR kodui
- papildomiems tekstams
- būsimiems modulio plėtiniams

---

# 8. Lifecycle Presentation

## Draft

Leidžiama:

- redaguoti
- išsaugoti
- finalizuoti
- ištrinti

Numerio nėra.

---

## Finalized

Leidžiama:

- peržiūrėti
- kopijuoti
- atšaukti

Apskaitinis turinys neredaguojamas.

---

## Cancelled

Leidžiama:

- peržiūrėti
- kopijuoti

Redaguoti negalima.

---

# 9. Dirty State

Sistema turi aptikti neišsaugotus pakeitimus.

Bandant uždaryti langą:

rodyti patvirtinimo dialogą.

Po sėkmingo išsaugojimo Dirty būsena panaikinama.

---

# 10. Validation

UI nerodo savo verslo logikos.

Ji tik atvaizduoja ValidationResult.

Galimos būsenos:

- Error
- Warning
- Information

Klaidos turi būti rodomos:

- prie laukų;
- bendrame klaidų sąraše.

---

# 11. Commands

Darbo lange turi būti:

- Save Draft
- Finalize
- Cancel
- Copy
- Close

---

# 12. Read-only Mode

Finalized ir Cancelled dokumentai atidaromi Read-only režimu.

Negalima:

- keisti eilučių;
- keisti kainų;
- keisti pirkėjo;
- keisti pardavėjo;
- keisti datų.

Leidžiama keisti tik operacinius statusus, jeigu tai leidžia domeno taisyklės.

---

# 13. UI Independence

Document UI:

- nevykdo SQL užklausų;
- neskaičiuoja sumų;
- negeneruoja numerių;
- nevykdo verslo validacijos.

Visa verslo logika kviečiama per Application Service.

---

# 14. Acceptance Criteria

UI laikoma įgyvendinta, kai:

- veikia vienas bendras Document Workspace;
- visi DocumentType naudoja tą pačią darbo sritį;
- Draft redaguojamas;
- Finalized yra tik skaitymui;
- Cancelled yra tik skaitymui;
- Dirty State veikia;
- Validation rodoma;
- Search ir filtrai veikia;
- Totals atsinaujina automatiškai;
- UI nepažeidžia DOCUMENT_DOMAIN.md taisyklių.

---

# Version History

| Version | Date | Changes |
|----------|------|---------|
| 1.0 | 2026-07-21 | Initial approved UI specification |