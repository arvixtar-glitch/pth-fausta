# DocumentationStandard_v2.0.md

# PTH Fausta Documentation Standard

---

**Projektas:** PTH Fausta

**Dokumentas:** DocumentationStandard_v2.0.md

**Versija:** 2.0

**Būsena:** Patvirtinta

**Autorius:** Architecture Team

**Įsigalioja nuo:** Task 8.1

---

# 1. Paskirtis

Šis dokumentas nustato visų techninių dokumentų rengimo standartą PTH Fausta projekte.

Tikslai:

- užtikrinti vienodą dokumentacijos struktūrą;
- aiškiai atskirti architektūrinius sprendimus nuo implementacijos;
- sudaryti galimybę DI sistemoms ir programuotojams dirbti pagal vienodas taisykles;
- užtikrinti dokumentų nuoseklumą viso projekto metu.

Nuo šio dokumento patvirtinimo visi nauji architektūriniai dokumentai privalo laikytis šiame standarte aprašytų taisyklių.

---

# 2. Dokumentacijos filosofija

Dokumentacija nėra komentarų rinkinys.

Dokumentacija yra projekto specifikacija.

Programuotojas turi programuoti pagal dokumentaciją.

Jeigu kodas prieštarauja dokumentacijai, laikoma, kad klaida yra kode.

---

# 3. Dokumentų tipai

Projektas naudoja šiuos dokumentų tipus.

## Architektūra

ARCHITECTURE.md

## Domeno specifikacijos

DOCUMENT_DOMAIN.md

CUSTOMER_DOMAIN.md

PRODUCT_DOMAIN.md

...

## UI specifikacijos

*_MODULE_UI.md

## Database

DATABASE.md

## DI komandos dokumentai

AI_TEAM.md

## Programuotojo užduotys

TASK_x.x.md

## Architecture Decision Records

ADR-XXX.md

---

# 4. RFC principas

Nuo Documentation Standard v2.0 visi architektūriniai dokumentai naudoja RFC stiliaus taisykles.

Naudojami terminai:

SHALL

Privaloma.

SHALL NOT

Draudžiama.

SHOULD

Rekomenduojama.

SHOULD NOT

Nerekomenduojama.

MAY

Leidžiama.

OPTIONAL

Neprivaloma.

---

# 5. Taisyklių numeracija

Kiekviena verslo taisyklė turi unikalų identifikatorių.

Pavyzdžiai:

D-001

D-002

...

Document Domain.

C-001

Customer Domain.

P-001

Product Domain.

CO-001

Company Domain.

DB-001

Database.

UI-001

User Interface.

---

# 6. Vienos taisyklės formatas

Kiekviena taisyklė privalo būti pateikta vienoda forma.

Pavyzdys

---

Rule D-017

Title

Document Finalization

Requirement

A Draft document SHALL become Finalized only through Document.finalize().

Reason

Guarantees immutable accounting documents.

Implication

After finalization:

- document number assigned;
- snapshots frozen;
- editing disabled.

---

Šis formatas naudojamas visuose domeno dokumentuose.

---

# 7. Reikalavimų lygiai

Dokumentuose turi būti aiškiai atskirta:

Mandatory

Privaloma.

Recommended

Rekomenduojama.

Optional

Neprivaloma.

Future Extension

Numatyta ateičiai.

Taip išvengiama situacijos, kai programuotojas nežino, kas privaloma dabar, o kas tik planuojama.

---

# 8. Dokumento struktūra

Rekomenduojama architektūrinių dokumentų struktūra.

0. Paskirtis

1. Filosofija

2. Objektai

3. Value Objects

4. Enumerations

5. Domain Services

6. Lifecycle

7. Business Rules

8. Validation

9. Integration

10. Future Extensions

---

# 9. Diagramos

Leidžiamos tik tekstinės ASCII schemos.

Pavyzdys

```text
Draft
   │
   ▼
Finalized
   │
   ▼
Cancelled
```

Nenaudojami ekrano vaizdai ar piešiniai architektūros dokumentuose.

---

# 10. Pavyzdžiai

Leidžiami trumpi pavyzdžiai.

Pavyzdys

```text
SF-000125
```

arba

```python
Document.finalize()
```

Pilni implementacijos fragmentai architektūros dokumentuose nerašomi.

---

# 11. Implementacijos draudimas

Architektūriniai dokumentai:

NEAPRAŠO

- Python implementacijos;
- SQLAlchemy realizacijos;
- UI komponentų kodo;
- Repository realizacijos.

Jie aprašo tik architektūrą.

---

# 12. Dokumentų tarpusavio ryšiai

Dokumentai gali remtis kitais dokumentais.

Pavyzdžiui

See:

ARCHITECTURE.md

DATABASE.md

DOCUMENT_MODULE_UI.md

Nuorodos turi būti aiškios.

---

# 13. Architecture Decision Records

Visi svarbūs architektūriniai sprendimai turi būti registruojami ADR dokumentuose.

Formatas:

ADR-001

ADR-002

...

Kiekviename ADR aprašoma:

- problema;
- svarstytos alternatyvos;
- priimtas sprendimas;
- pasekmės.

---

# 14. Programuotojo komentarų standartas

Komentarai gali remtis taisyklėmis.

Pavyzdys

```python
# Implements Rule D-017
```

arba

```python
# See Rule DB-014
```

Tai leidžia lengvai susieti kodą su architektūra.

---

# 15. Testų standartas

Testų pavadinimai gali naudoti taisyklės numerį.

Pavyzdys

```python
test_D017_finalize_assigns_number()

test_D021_deleted_number_not_reused()
```

Tai leidžia greitai identifikuoti testuojamą taisyklę.

---

# 16. Failų pavadinimai

Naudojami tik didžiosiomis raidėmis rašomi architektūros dokumentai.

Pavyzdžiai

ARCHITECTURE.md

DATABASE.md

DOCUMENT_DOMAIN.md

DOCUMENT_MODULE_UI.md

AI_TEAM.md

README.md

---

# 17. Versijavimas

Kiekvienas dokumentas turi antraštę.

Privalomi laukai

Projektas

Dokumentas

Versija

Būsena

Autorius

Sukūrimo data

Paskutinis atnaujinimas

---

# 18. Changelog

Kiekviename dokumente rekomenduojama turėti trumpą pakeitimų istoriją.

Pavyzdys

v1.0

Initial version.

v1.1

Validation rules added.

v2.0

RFC documentation standard adopted.

---

# 19. DI komandos taisyklė

Architektūriniai sprendimai gali būti siūlomi skirtingų DI sistemų.

Tačiau galutinė specifikacija turi būti viena.

Prieš patvirtinimą visi pasiūlymai turi būti suvienodinti į vieną dokumentą.

Projektas neturi turėti konkuruojančių architektūrinių versijų.

---

# 20. Pagrindinis principas

Visi projekto dalyviai:

- programuotojai;
- architektai;
- testuotojai;
- DI sistemos;

vadovaujasi šia prioritetų tvarka:

1. Patvirtinta architektūros dokumentacija.
2. Patvirtinti domeno dokumentai.
3. Patvirtinta UI specifikacija.
4. Database specifikacija.
5. Implementacija.

Jeigu randamas prieštaravimas, pirmiausia taisoma implementacija, o ne dokumentacija, nebent Produkto savininkas priima naują architektūrinį sprendimą.

---

# Dokumento būsena

Šis dokumentas yra oficialus PTH Fausta dokumentacijos standartas nuo projekto Task 8.1.

Visi po šios datos kuriami architektūriniai dokumentai privalo atitikti šiame standarte aprašytus reikalavimus.
