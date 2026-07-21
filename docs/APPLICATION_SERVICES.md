# APPLICATION_SERVICES.md

# PTH Fausta – Application Services Specification

---

**Projektas:** PTH Fausta

**Dokumentas:** APPLICATION_SERVICES.md

**Versija:** 1.0

**Būsena:** Patvirtinta

**Autorius:** Architecture Team

**Dokumento tipas:** Application Layer Specification

**Atitinka:**

- DOCUMENT_DOMAIN.md
- DATABASE.md
- DOCUMENT_MODULE_UI.md
- CODING_STANDARDS.md

---

# 1. Purpose

Šis dokumentas apibrėžia Application Layer paskirtį.

Application Layer koordinuoja visą sistemos darbą.

Ji:

- koordinuoja Domain objektus;
- koordinuoja Repository;
- koordinuoja EventBus;
- koordinuoja transakcijas;
- koordinuoja UI užklausas.

Application Layer pati nevykdo verslo logikos.

Visa verslo logika priklauso Domain sluoksniui.

---

# 2. Responsibilities

Application Layer atsakinga už:

- Use Cases įgyvendinimą;
- Aggregate gavimą iš Repository;
- Domain metodų kvietimą;
- Repository išsaugojimą;
- Domain Events publikavimą;
- transakcijų koordinavimą.

Application Layer nėra atsakinga už:

- SQL;
- UI;
- PDF;
- Email;
- verslo taisyklių skaičiavimą.

---

# 3. Dependency Direction

Priklausomybės:

```
UI
 │
 ▼
Application Services
 │
 ▼
Domain
 │
 ▼
Repository Interface
 │
 ▼
Infrastructure
```

Priklausomybės negali būti apverstos.

Domain nežino apie Application.

Repository Interface priklauso Domain.

Repository implementacija priklauso Infrastructure.

---

# 4. Service Principles

Kiekvienas Application Service:

- turi vieną atsakomybę;
- yra stateless;
- neturi UI priklausomybių;
- neturi SQLAlchemy priklausomybių;
- nekuria globalios būsenos.

---

# 5. Main Services

Document modulis naudoja vieną pagrindinį servisą:

```
DocumentService
```

Ateityje gali būti pridėti:

```
PaymentService

PdfService

EmailService

ReportingService
```

Jie nėra šio dokumento dalis.

---

# 6. DocumentService

DocumentService koordinuoja Document Aggregate.

Jis nėra Aggregate dalis.

Jis nėra Repository.

Jis nėra UI Controller.

---

# 7. Supported Use Cases

DocumentService privalo įgyvendinti šiuos Use Cases.

## CreateDocument

Sukuria naują Draft.

Veiksmai:

- sukuria Aggregate;
- užpildo Company Snapshot;
- parenka numatytą banko sąskaitą;
- išsaugo Repository.

---

## LoadDocument

Įkelia pilną Aggregate.

---

## SaveDraft

Išsaugo Draft.

Leidžiama nepilna validacija.

Numeris nesuteikiamas.

---

## DeleteDraft

Pašalina Draft.

Finalized dokumentų nešalina.

---

## FinalizeDocument

Koordinuoja:

- Validation;
- Totals;
- Snapshot užfiksavimą;
- numeracijos suteikimą;
- išsaugojimą;
- Event publikavimą.

Visas procesas vyksta vienoje transakcijoje.

---

## CancelDocument

Atšaukia Finalized dokumentą.

Numeris išlieka.

Istorija išlieka.

---

## CopyDocument

Sukuria naują Draft.

Kopijuoja leidžiamus duomenis.

Naujas dokumentas neturi numerio.

---

## SearchDocuments

Atlieka paiešką.

Palaikomi filtrai:

- tekstas;
- tipas;
- būsena;
- datos.

---

## UpdatePaymentStatus

Keičia PaymentStatus.

---

## UpdateDeliveryStatus

Keičia DeliveryStatus.

---

## UpdateAcceptanceStatus

Keičia AcceptanceStatus.

---

# 8. Transaction Boundary

Application Service koordinuoja vieną transakciją.

Tipinis finalizavimas:

```
Load Aggregate

↓

Validate

↓

Calculate Totals

↓

Assign Number

↓

Persist Aggregate

↓

Commit

↓

Publish Domain Events
```

Jeigu bent vienas etapas nepavyksta:

- vykdomas Rollback;
- Event nepublikuojami.

---

# 9. Event Publishing

Application Layer publikuoja tik Domain Events.

Event publikuojami tik po sėkmingo Commit.

Domain pats EventBus nekviečia.

---

# 10. Error Handling

Application Layer neignoruoja klaidų.

Domain klaidos perduodamos aukščiau.

Repository klaidos transformuojamos į Application lygio klaidas, kai reikia.

---

# 11. Controllers

UI Controller nėra verslo logikos vieta.

Controller:

- priima UI veiksmą;
- kviečia Application Service;
- perduoda rezultatą UI.

Controller neskaičiuoja sumų.

Controller nevykdo SQL.

Controller nekuria Aggregate.

---

# 12. Repository Usage

Application Layer dirba tik su Repository Interface.

Negalima:

- naudoti SQLAlchemy Session tiesiogiai;
- vykdyti SQL užklausų;
- manipuliuoti ORM objektais.

---

# 13. EventBus Usage

Application Layer:

- gauna Domain Events;
- publikuoja EventBus.

Domain nežino apie EventBus.

---

# 14. ServiceContainer

Visi Application Services registruojami Composition Root.

ServiceContainer naudojamas tik objektų sukūrimui.

Application Service negali ieškoti priklausomybių ServiceContainer viduje.

Visos priklausomybės perduodamos per konstruktorių (Constructor Injection).

---

# 15. Acceptance Criteria

Application Layer laikoma įgyvendinta, kai:

- visi Use Cases veikia;
- Domain lieka nepriklausomas;
- Repository kviečiamas tik per Interface;
- Event publikuojami tik po Commit;
- Controller neturi verslo logikos;
- SQL nevykdomas Application sluoksnyje;
- UI priklausomybių nėra.

---

# Version History

| Version | Date | Changes |
|----------|------|---------|
| 1.0 | 2026-07-21 | Initial approved specification |