# DOCUMENT_DOMAIN.md

# PTH Fausta Document Domain Specification

---

**Projektas:** PTH Fausta

**Dokumentas:** DOCUMENT_DOMAIN.md

**Versija:** 1.0 (Draft)

**Būsena:** Kuriama

**Autorius:** Architecture Team

**Dokumento tipas:** Domain Specification

**Atitinka:** DocumentationStandard_v2.0

---

# 0. Purpose

Šis dokumentas apibrėžia **Document domeno** architektūrą.

Jis yra vienintelis oficialus dokumentų modulio verslo logikos šaltinis.

Dokumente aprašoma:

- domeno modelis;
- objektų tarpusavio ryšiai;
- gyvavimo ciklas;
- verslo taisyklės;
- validavimo taisyklės;
- integracija su kitais moduliais.

Šis dokumentas **neaprašo** Python implementacijos.

---

# 1. Domain Philosophy

Document modulis yra vienas pagrindinių PTH Fausta sistemos domenų.

Jo paskirtis – saugoti ir valdyti apskaitinius dokumentus viso jų gyvavimo metu.

Sistema nelaiko skirtingų dokumentų tipų atskiromis sistemomis.

Vietoje to naudojamas vienas bendras Document Aggregate.

Dokumento tipas apibrėžia tik elgseną.

Tai leidžia:

- sumažinti dubliuojamą kodą;
- užtikrinti vienodą dokumentų gyvavimo ciklą;
- supaprastinti palaikymą;
- lengvai pridėti naujus dokumentų tipus ateityje.

---

# 2. Aggregate Root

Document Aggregate sudaro vieną nedalomą verslo objektą.

Visi su dokumentu susiję duomenys priklauso šiam Aggregate.

```
                    Document
                        │
        ┌───────────────┼────────────────┐
        │               │                │
     Header          Lines          Totals
        │               │                │
        │               │                │
   Snapshots      DocumentLine      Calculated
        │
        │
 Metadata
```

Joks kitas modulis negali tiesiogiai keisti Aggregate vidaus.

Visi pakeitimai atliekami tik per Document.

---

## Rule D-001

### Title

Single Aggregate Root

### Requirement

The system SHALL use exactly one Aggregate Root named **Document**.

### Reason

Ensures transactional consistency.

### Implication

All document modifications are performed through the Document aggregate.

---

## Rule D-002

### Title

Aggregate Ownership

### Requirement

All DocumentLine objects SHALL belong to exactly one Document.

### Reason

Prevents shared mutable state.

### Implication

Document lines cannot exist independently.

---

## Rule D-003

### Title

Aggregate Consistency

### Requirement

A Document SHALL always remain internally consistent after every business operation.

### Reason

Guarantees valid business state.

### Implication

Business operations may reject invalid changes before they are committed.

---

# 3. Document Entity

Document yra pagrindinis domeno objektas.

Jis reprezentuoja vieną verslo dokumentą nepriklausomai nuo jo tipo.

Document saugo:

- identitetą;
- tipą;
- gyvavimo būseną;
- numeraciją;
- datas;
- pirkėjo informaciją;
- pardavėjo informaciją;
- eilutes;
- apskaičiuotas sumas;
- momentines (Snapshot) kopijas;
- pateikimo nustatymus.

Document pats atsako už savo būsenos keitimą.

Išoriniai moduliai negali keisti jo būsenos tiesiogiai.

---

## Rule D-004

### Title

Document Identity

### Requirement

Every Document SHALL have exactly one immutable identifier.

### Reason

Guarantees unique identity.

### Implication

The identifier never changes during the document lifetime.

---

## Rule D-005

### Title

Document Type

### Requirement

Every Document SHALL have exactly one DocumentType.

### Reason

Defines business behaviour.

### Implication

Document type cannot be undefined.

---

## Rule D-006

### Title

Single Lifecycle

### Requirement

A Document SHALL have exactly one Lifecycle State.

### Reason

Prevents ambiguous state transitions.

### Implication

The lifecycle state determines allowed operations.

---

## Rule D-007

### Title

Document Ownership

### Requirement

A Document SHALL own all business data required to reproduce itself.

### Reason

Historical documents must remain unchanged.

### Implication

Future modifications of Customer, Company or Product modules SHALL NOT modify historical documents.

---

## Rule D-008

### Title

Immutable History

### Requirement

Historical information SHALL be preserved using immutable snapshots.

### Reason

Accounting documents must remain historically accurate.

### Implication

Snapshots become part of the document history.

---

# 4. Scope

Document Domain yra atsakingas už:

- dokumentų kūrimą;
- redagavimą;
- finalizavimą;
- atšaukimą;
- numeracijos inicijavimą;
- sumų apskaičiavimą;
- PVM logiką;
- momentinių kopijų saugojimą;
- dokumento paruošimą spausdinimui;
- PDF generavimo duomenų pateikimą.

Document Domain nėra atsakingas už:

- PDF piešimą;
- UI atvaizdavimą;
- el. pašto siuntimą;
- duomenų bazės realizaciją;
- SQL užklausas.

---

## Rule D-009

### Title

Single Responsibility

### Requirement

The Document Domain SHALL contain only document business logic.

### Reason

Maintains clear architectural boundaries.

### Implication

Infrastructure responsibilities belong to other modules.

---

## Rule D-010

### Title

UI Independence

### Requirement

The Document Domain SHALL NOT depend on UI components.

### Reason

Allows reuse by different presentation layers.

### Implication

Business rules remain identical regardless of UI.
---

# 5. Entities

Document Domain naudoja šias pagrindines Entity klases.

```
Document
    │
    ├── DocumentLine
    │
    ├── DocumentTotals
    │
    ├── SellerSnapshot
    │
    ├── BuyerSnapshot
    │
    ├── TaxSnapshot
    │
    ├── PresentationSnapshot
    │
    └── Metadata
```

Tik **Document** yra Aggregate Root.

Visos kitos Entity priklauso Document Aggregate ir negali egzistuoti savarankiškai.

---

## Rule D-011

### Title

Aggregate Composition

### Requirement

Every Entity inside the Document Domain SHALL belong to exactly one Document Aggregate.

### Reason

Maintains aggregate consistency.

### Implication

Entities cannot be shared between Documents.

---

## Rule D-012

### Title

Aggregate Lifetime

### Requirement

Child Entities SHALL have the same lifetime as their parent Document.

### Reason

Simplifies lifecycle management.

### Implication

Deleting a Document removes all child entities.

---

# 5.1 DocumentLine

DocumentLine reprezentuoja vieną dokumento eilutę.

Ji aprašo vieną parduodamą prekę arba paslaugą.

DocumentLine nėra Product kopija.

Ji saugo tik tą informaciją, kuri reikalinga konkrečiam dokumentui.

Tipiniai duomenys:

- eilutės numeris;
- prekės pavadinimas;
- aprašymas;
- matavimo vienetas;
- kiekis;
- vieneto kaina;
- nuolaida;
- PVM tarifas;
- eilutės suma.

---

## Rule D-013

### Title

Independent Line Data

### Requirement

A DocumentLine SHALL store its own business values.

### Reason

Historical documents must remain unchanged after Product modifications.

### Implication

Editing a Product SHALL NOT modify existing DocumentLines.

---

## Rule D-014

### Title

Line Ordering

### Requirement

DocumentLines SHALL preserve their order.

### Reason

Document layout depends on line sequence.

### Implication

Sorting is performed explicitly.

---

## Rule D-015

### Title

Line Numbering

### Requirement

Each DocumentLine SHALL have a sequential line number.

### Reason

Improves readability.

### Implication

Line numbers may be recalculated after insert or delete operations.

---

## Rule D-016

### Title

Line Ownership

### Requirement

A DocumentLine SHALL belong to exactly one Document.

### Reason

Ensures ownership.

### Implication

Moving a line between documents is implemented as copy and delete.

---

# 5.2 DocumentTotals

DocumentTotals saugo apskaičiuotas dokumento sumas.

Tai nėra rankiniu būdu redaguojami duomenys.

Visos reikšmės gaunamos skaičiuojant DocumentLine kolekciją.

Tipiniai laukai:

- subtotal;
- discount total;
- taxable amount;
- VAT total;
- grand total.

---

## Rule D-017

### Title

Calculated Totals

### Requirement

DocumentTotals SHALL always be calculated.

### Reason

Prevents inconsistent financial data.

### Implication

Users cannot edit totals directly.

---

## Rule D-018

### Title

Totals Source

### Requirement

DocumentTotals SHALL be derived only from DocumentLines.

### Reason

Provides a single source of truth.

### Implication

Changing a line immediately invalidates previous totals.

---

# 5.3 Metadata

Metadata aprašo techninę dokumento informaciją.

Tai nėra verslo informacija.

Tipiniai laukai:

- creation timestamp;
- last modification timestamp;
- finalized timestamp;
- cancelled timestamp;
- created by;
- modified by.

---

## Rule D-019

### Title

Metadata Separation

### Requirement

Metadata SHALL be separated from business data.

### Reason

Improves maintainability.

### Implication

Business logic SHALL NOT depend on technical timestamps.

---

## Rule D-020

### Title

Automatic Metadata

### Requirement

Metadata SHALL be maintained automatically by the system.

### Reason

Prevents manual inconsistencies.

### Implication

Users cannot directly edit metadata.

---

# 5.4 Historical Snapshots

Document saugo istorines momentines kopijas.

Jos naudojamos tam, kad seni dokumentai išliktų identiški net ir pasikeitus sistemos duomenims.

Naudojami Snapshot objektai:

- SellerSnapshot
- BuyerSnapshot
- TaxSnapshot
- PresentationSnapshot

---

## Rule D-021

### Title

Immutable Snapshots

### Requirement

Snapshots SHALL become immutable after document finalization.

### Reason

Preserves accounting history.

### Implication

Snapshots cannot be edited.

---

## Rule D-022

### Title

Historical Accuracy

### Requirement

Historical documents SHALL NOT depend on current Company, Customer or Product data.

### Reason

Guarantees legal correctness.

### Implication

All required historical information must exist inside the document.

---

## Rule D-023

### Title

Snapshot Ownership

### Requirement

Every Snapshot SHALL belong to exactly one Document.

### Reason

Simplifies lifecycle management.

### Implication

Snapshots are deleted together with the document.

---

# 5.5 Entity Relationships

```
Document
│
├── DocumentLine [1..*]
│
├── DocumentTotals [1]
│
├── Metadata [1]
│
├── SellerSnapshot [1]
│
├── BuyerSnapshot [1]
│
├── TaxSnapshot [1]
│
└── PresentationSnapshot [1]
```

Visi ryšiai yra sudėtiniai (composition).

Nė viena iš šių Entity negali egzistuoti be savo Document Aggregate.

---

## Rule D-024

### Title

Composition

### Requirement

All child entities SHALL use composition instead of aggregation.

### Reason

Ensures lifecycle consistency.

### Implication

Removing the Document removes all owned entities.

---

## Rule D-025

### Title

Aggregate Boundary

### Requirement

External modules SHALL access child entities only through the Document Aggregate.

### Reason

Protects domain integrity.

### Implication

Repositories expose only the Aggregate Root.
---

# 6. Value Objects

Value Objects aprašo nekintamas verslo reikšmes.

Jie neturi savarankiškos tapatybės (Identity).

Du Value Objects laikomi lygiais, jeigu visos jų reikšmės sutampa.

Value Objects naudojami:

- verslo logikai;
- skaičiavimams;
- validacijai;
- palyginimams.

Jie negali egzistuoti savarankiškai.

---

## Rule D-026

### Title

Immutable Value Objects

### Requirement

All Value Objects SHALL be immutable.

### Reason

Prevents accidental modification.

### Implication

Changing a value creates a new Value Object.

---

## Rule D-027

### Title

Equality by Value

### Requirement

Value Objects SHALL be compared by their values.

### Reason

Identity is irrelevant.

### Implication

Two Value Objects with identical values are considered equal.

---

# 6.1 DocumentNumber

DocumentNumber reprezentuoja oficialų dokumento numerį.

Jį sudaro:

- numeracijos serija;
- eilės numeris;
- suformatuotas vaizdas.

Pavyzdžiai:

```
SF-000001

IS-000152

KP-001245
```

DocumentNumber sukuriamas tik naudojant DocumentNumberingService.

---

## Rule D-028

### Title

Official Number

### Requirement

DocumentNumber SHALL be assigned only by DocumentNumberingService.

### Reason

Ensures unique numbering.

### Implication

Users cannot assign official document numbers.

---

## Rule D-029

### Title

Immutable Number

### Requirement

DocumentNumber SHALL become immutable after assignment.

### Reason

Accounting numbers cannot change.

### Implication

Number edits are prohibited.

---

## Rule D-030

### Title

Unique Number

### Requirement

Every finalized document SHALL have a unique DocumentNumber.

### Reason

Legal accounting requirement.

### Implication

Duplicate numbers are forbidden.

---

# 6.2 Money

Money reprezentuoja piniginę reikšmę.

Money nėra Decimal pakaitalas.

Tai verslo objektas.

Money naudojamas:

- kainoms;
- sumoms;
- PVM;
- nuolaidoms;
- tarpiniams skaičiavimams.

---

## Rule D-031

### Title

Currency Precision

### Requirement

Money SHALL preserve accounting precision.

### Reason

Prevents rounding errors.

### Implication

Floating point calculations SHALL NOT be used.

---

## Rule D-032

### Title

Currency Consistency

### Requirement

All calculations SHALL use Money objects.

### Reason

Provides consistent financial calculations.

### Implication

Primitive numeric values should not be used in business calculations.

---

# 6.3 Quantity

Quantity reprezentuoja parduodamą kiekį.

Ji naudojama:

- prekėms;
- paslaugoms;
- darbo valandoms;
- svoriui;
- ilgiui.

---

## Rule D-033

### Title

Non-negative Quantity

### Requirement

Quantity SHALL NOT be negative.

### Reason

Negative quantities require explicit business operations such as credit documents.

### Implication

Negative values are rejected during validation.

---

# 6.4 Percentage

Percentage naudojamas:

- nuolaidoms;
- PVM tarifams;
- būsimiems procentiniams skaičiavimams.

---

## Rule D-034

### Title

Percentage Range

### Requirement

Percentage SHALL represent values between 0 and 100 unless explicitly specified otherwise.

### Reason

Avoids invalid business values.

### Implication

Validation rejects invalid percentages.

---

# 6.5 VatRate

VatRate reprezentuoja PVM tarifą.

Tipinės reikšmės:

- 0 %
- 9 %
- 21 %

Sistema gali būti išplėsta papildomiems tarifams.

---

## Rule D-035

### Title

Supported VAT Rates

### Requirement

VatRate SHALL use configured tax rates.

### Reason

Allows future legislative changes.

### Implication

VAT rates are configurable rather than hardcoded.

---

## Rule D-036

### Title

Historical VAT

### Requirement

Documents SHALL preserve the VAT rate used during finalization.

### Reason

Historical accounting accuracy.

### Implication

Future VAT changes SHALL NOT affect historical documents.

---

# 6.6 Business Dates

Document Domain naudoja kelias verslo datas.

Pavyzdžiai:

- document date;
- due date;
- finalized date;
- cancelled date.

Kiekviena data turi aiškią verslo paskirtį.

---

## Rule D-037

### Title

Business Date Meaning

### Requirement

Each business date SHALL have exactly one defined meaning.

### Reason

Avoids ambiguity.

### Implication

One date cannot represent multiple business events.

---

# 6.7 Value Object Summary

Naudojami Value Objects:

- DocumentNumber
- Money
- Quantity
- Percentage
- VatRate

Ateityje gali būti pridėti:

- Currency
- ExchangeRate
- TaxIdentifier
- PaymentTerm
- DiscountPolicy

Tai nekeičia esamų verslo taisyklių.

---

## Rule D-038

### Title

Future Extensibility

### Requirement

New Value Objects MAY be introduced without changing existing business rules.

### Reason

Supports future system growth.

### Implication

The domain model remains extensible while preserving backward compatibility.
---

# 7. Enumerations

Enumerations apibrėžia baigtinius ir domeno požiūriu aiškiai atskirtus reikšmių rinkinius.

Document Domain naudoja šias pagrindines enumeracijas:

- DocumentType;
- LifecycleState;
- PaymentStatus;
- DeliveryStatus;
- AcceptanceStatus;
- PriceBasis;
- VatTreatment.

Enumeracijų reikšmės yra sistemos domeno dalis.

Jos negali būti laisvai kuriamos ar keičiamos naudotojo.

Naudotojo nustatymai gali keisti dokumento tipo elgseną, numeracijos seriją ir pateikimą, tačiau negali sukurti naujos sistemos domeno reikšmės be architektūrinio pakeitimo.

---

## Rule D-039

### Title

Explicit Domain Enumerations

### Requirement

Finite domain states and classifications SHALL be represented by explicit enumerations.

### Reason

Prevents ambiguous or unsupported values.

### Implication

Free-form text SHALL NOT be used instead of defined domain enumerations.

---

## Rule D-040

### Title

Stable Enumeration Meaning

### Requirement

Every enumeration value SHALL have exactly one defined business meaning.

### Reason

Prevents inconsistent interpretation between modules.

### Implication

The same enumeration value cannot represent different business concepts.

---

# 7.1 DocumentType

DocumentType apibrėžia dokumento verslo paskirtį.

Palaikomi dokumentų tipai:

- `INVOICE`;
- `PROFORMA`;
- `COMMERCIAL_OFFER`;
- `EBAY_INVOICE`.

Lietuviškame naudotojo sąsajos sluoksnyje jie gali būti rodomi kaip:

| Sistemos reikšmė | Rodomas pavadinimas |
|---|---|
| `INVOICE` | Sąskaita faktūra |
| `PROFORMA` | Išankstinė sąskaita |
| `COMMERCIAL_OFFER` | Komercinis pasiūlymas |
| `EBAY_INVOICE` | eBay sąskaita |

Visi dokumentų tipai naudoja tą patį Document Aggregate.

DocumentType gali lemti:

- numatytąją numeracijos seriją;
- privalomus laukus;
- galimas verslo datas;
- pateikimo nustatymus;
- validavimo taisykles;
- numatytąjį tekstą;
- galimus proceso statusus.

---

## Rule D-041

### Title

Single Document Type

### Requirement

Every Document SHALL have exactly one DocumentType.

### Reason

Document behaviour depends on its business purpose.

### Implication

A Document cannot exist without a valid DocumentType.

---

## Rule D-042

### Title

Shared Aggregate

### Requirement

All supported DocumentType values SHALL use the same Document Aggregate.

### Reason

Avoids duplicated domain models and inconsistent behaviour.

### Implication

Separate Invoice, Proforma, CommercialOffer or EbayInvoice aggregate roots SHALL NOT be created.

---

## Rule D-043

### Title

System-defined Types

### Requirement

DocumentType values SHALL be defined by the system.

### Reason

Each type may require specific domain rules and validation.

### Implication

Users SHALL NOT create arbitrary DocumentType values through application settings.

---

## Rule D-044

### Title

Type-specific Configuration

### Requirement

Each DocumentType MAY have its own configurable settings.

### Reason

Different document types require different numbering and presentation behaviour.

### Implication

Configuration changes SHALL NOT require separate aggregate implementations.

---

## Rule D-045

### Title

Document Type Stability

### Requirement

A finalized Document SHALL NOT change its DocumentType.

### Reason

Changing the type would alter the historical meaning of the document.

### Implication

A different type requires creation of a new Document.

---

# 7.2 LifecycleState

LifecycleState apibrėžia pagrindinę dokumento gyvavimo būseną.

Galimos reikšmės:

- `DRAFT`;
- `FINALIZED`;
- `CANCELLED`.

Gyvavimo ciklas:

```text
Draft
  │
  │ Finalize
  ▼
Finalized
  │
  │ Cancel
  ▼
Cancelled
```

`DRAFT` reiškia, kad dokumentas dar ruošiamas.

`FINALIZED` reiškia, kad dokumentas patvirtintas, jam suteiktas oficialus numeris ir jo apskaitiniai duomenys užfiksuoti.

`CANCELLED` reiškia, kad anksčiau finalizuotas dokumentas buvo atšauktas, tačiau išsaugomas istorijoje.

Nuolatinis dokumento ištrynimas nėra LifecycleState.

Tai atskira administracinė operacija, valdoma sistemos nustatymais.

---

## Rule D-046

### Title

Single Lifecycle State

### Requirement

Every Document SHALL have exactly one LifecycleState.

### Reason

Prevents ambiguous document state.

### Implication

Lifecycle-dependent operations are determined by this state.

---

## Rule D-047

### Title

Initial State

### Requirement

A newly created Document SHALL have the `DRAFT` LifecycleState.

### Reason

Every document must be prepared and validated before finalization.

### Implication

A Document cannot be created directly as finalized or cancelled.

---

## Rule D-048

### Title

Final State Meaning

### Requirement

The `FINALIZED` state SHALL represent an officially issued document.

### Reason

Finalization establishes the accounting record.

### Implication

A finalized Document has an official immutable number and frozen historical data.

---

## Rule D-049

### Title

Cancellation Meaning

### Requirement

The `CANCELLED` state SHALL represent a finalized document that is no longer active but remains part of the historical record.

### Reason

Accounting history must remain traceable.

### Implication

Cancellation SHALL NOT remove the document or release its number.

---

## Rule D-050

### Title

Hard Delete Separation

### Requirement

Permanent deletion SHALL NOT be represented as a LifecycleState.

### Reason

Deletion removes the aggregate and therefore cannot be a persistent state of that aggregate.

### Implication

Hard delete is handled as a separate administrative operation.

---

# 7.3 PaymentStatus

PaymentStatus apibrėžia dokumento apmokėjimo būseną.

Tai nėra LifecycleState dalis.

Galimos pradinės reikšmės:

- `NOT_APPLICABLE`;
- `UNPAID`;
- `PARTIALLY_PAID`;
- `PAID`;
- `OVERDUE`.

`NOT_APPLICABLE` naudojama dokumentams, kuriems apmokėjimo stebėjimas netaikomas.

Pavyzdžiui, komerciniam pasiūlymui apmokėjimo būsena gali būti `NOT_APPLICABLE`.

---

## Rule D-051

### Title

Independent Payment State

### Requirement

PaymentStatus SHALL be independent from LifecycleState.

### Reason

Document issuance and payment are different business processes.

### Implication

A finalized Document may be unpaid, partially paid, paid or overdue.

---

## Rule D-052

### Title

Payment Applicability

### Requirement

A DocumentType that does not represent a payable obligation SHALL use `NOT_APPLICABLE` unless later converted into another business document.

### Reason

Prevents false payment information.

### Implication

Payment-related operations are disabled when PaymentStatus is `NOT_APPLICABLE`.

---

# 7.4 DeliveryStatus

DeliveryStatus apibrėžia dokumento perdavimo gavėjui būseną.

Galimos pradinės reikšmės:

- `NOT_SENT`;
- `SENT`;
- `DELIVERED`;
- `DELIVERY_FAILED`;
- `NOT_APPLICABLE`.

Ši būsena gali būti naudojama:

- el. pašto siuntimui;
- būsimam elektroniniam pristatymui;
- rankiniam perdavimo pažymėjimui.

DeliveryStatus nekeičia dokumento apskaitinio turinio.

---

## Rule D-053

### Title

Independent Delivery State

### Requirement

DeliveryStatus SHALL be independent from LifecycleState.

### Reason

Document delivery is an operational process, not an accounting lifecycle transition.

### Implication

Changing DeliveryStatus SHALL NOT modify finalized document business data.

---

# 7.5 AcceptanceStatus

AcceptanceStatus apibrėžia dokumento priėmimo arba patvirtinimo iš gavėjo pusės būseną.

Galimos pradinės reikšmės:

- `NOT_APPLICABLE`;
- `PENDING`;
- `ACCEPTED`;
- `REJECTED`;
- `EXPIRED`.

Ši būsena ypač aktuali:

- komerciniams pasiūlymams;
- išankstinėms sąskaitoms;
- būsimiems dokumentų derinimo procesams.

AcceptanceStatus nekeičia LifecycleState automatiškai.

Pavyzdžiui, komercinis pasiūlymas gali būti finalizuotas, bet jo AcceptanceStatus gali likti `PENDING`.

---

## Rule D-054

### Title

Independent Acceptance State

### Requirement

AcceptanceStatus SHALL be independent from LifecycleState.

### Reason

Recipient acceptance is a separate business process.

### Implication

Acceptance changes SHALL NOT directly modify document lifecycle or historical snapshots.

---

# 7.6 PriceBasis

PriceBasis apibrėžia, kaip interpretuojama dokumento eilutės vieneto kaina.

Galimos reikšmės:

- `NET`;
- `GROSS`.

`NET` reiškia, kad įvesta vieneto kaina yra be PVM.

`GROSS` reiškia, kad įvesta vieneto kaina jau apima PVM.

PriceBasis turi būti vienareikšmiškai apibrėžtas, kad DocumentTotalsService galėtų teisingai apskaičiuoti mokesčius ir galutines sumas.

---

## Rule D-055

### Title

Explicit Price Basis

### Requirement

Every taxable DocumentLine SHALL have an explicit PriceBasis.

### Reason

Tax calculations depend on whether VAT is included in the entered price.

### Implication

The system SHALL NOT infer PriceBasis from display formatting.

---

## Rule D-056

### Title

Price Basis Preservation

### Requirement

The PriceBasis used for a finalized DocumentLine SHALL be preserved historically.

### Reason

Recalculation must reproduce the original accounting result.

### Implication

Future default-setting changes SHALL NOT affect finalized document lines.

---

# 7.7 VatTreatment

VatTreatment apibrėžia, kaip dokumento eilutei taikomas PVM.

Galimos pradinės reikšmės:

- `STANDARD`;
- `ZERO_RATE`;
- `EXEMPT`;
- `OUT_OF_SCOPE`;
- `NOT_APPLICABLE`.

Reikšmių paskirtis:

| Reikšmė | Paskirtis |
|---|---|
| `STANDARD` | Taikomas nustatytas teigiamas PVM tarifas |
| `ZERO_RATE` | Taikomas 0 % PVM tarifas |
| `EXEMPT` | Operacija neapmokestinama PVM pagal taikomą pagrindą |
| `OUT_OF_SCOPE` | Operacija nepatenka į PVM taikymo sritį |
| `NOT_APPLICABLE` | Pardavėjas nėra PVM mokėtojas arba PVM logika dokumentui netaikoma |

`ZERO_RATE`, `EXEMPT` ir `OUT_OF_SCOPE` nėra tapačios reikšmės, net jei apskaičiuota PVM suma yra lygi nuliui.

---

## Rule D-057

### Title

Explicit VAT Treatment

### Requirement

Every DocumentLine SHALL have an explicit VatTreatment.

### Reason

A zero VAT amount may have different legal and accounting meanings.

### Implication

The system SHALL NOT determine tax meaning only from the numeric VAT rate.

---

## Rule D-058

### Title

VAT Treatment Consistency

### Requirement

VatTreatment and VatRate SHALL form a valid combination.

### Reason

Prevents contradictory tax data.

### Implication

For example, `STANDARD` requires a configured positive VatRate, while `ZERO_RATE` requires a zero rate.

---

## Rule D-059

### Title

Non-VAT Payer Treatment

### Requirement

When the seller is not a VAT payer, applicable DocumentLines SHALL use `NOT_APPLICABLE` VatTreatment.

### Reason

VAT SHALL NOT be calculated or presented as charged tax by a non-VAT payer.

### Implication

VAT totals and VAT-specific presentation elements are omitted.

---

## Rule D-060

### Title

Historical Tax Meaning

### Requirement

VatTreatment used during finalization SHALL be preserved as part of the document history.

### Reason

Tax classification must remain reproducible and auditable.

### Implication

Later tax configuration changes SHALL NOT alter finalized documents.

---

# 7.8 Status Independence

LifecycleState, PaymentStatus, DeliveryStatus ir AcceptanceStatus aprašo skirtingus dokumento aspektus.

Pavyzdys:

```text
LifecycleState:  FINALIZED
PaymentStatus:   UNPAID
DeliveryStatus:  SENT
AcceptanceStatus: NOT_APPLICABLE
```

Kitas pavyzdys:

```text
LifecycleState:   FINALIZED
PaymentStatus:    NOT_APPLICABLE
DeliveryStatus:   DELIVERED
AcceptanceStatus: ACCEPTED
```

Šios būsenos negali būti sujungiamos į vieną bendrą statusą.

---

## Rule D-061

### Title

Orthogonal Statuses

### Requirement

LifecycleState, PaymentStatus, DeliveryStatus and AcceptanceStatus SHALL remain separate domain concepts.

### Reason

Each status represents a different business process.

### Implication

The system SHALL NOT use one overloaded status enumeration for all document states.

---

## Rule D-062

### Title

No Implicit Cross-transition

### Requirement

Changing one orthogonal status SHALL NOT automatically change another status unless an explicit business rule defines that transition.

### Reason

Prevents hidden side effects.

### Implication

For example, marking a Document as paid does not finalize, deliver or accept it.

---

# 7.9 Enumeration Extension

Naujos enumeracijų reikšmės gali būti pridedamos tik tada, kai atsiranda aiškus naujas verslo poreikis.

Nauja reikšmė negali pakeisti jau egzistuojančios reikšmės prasmės.

Pridedant naują reikšmę turi būti įvertinta:

- domeno logika;
- validacija;
- duomenų bazės suderinamumas;
- UI atvaizdavimas;
- istorinių dokumentų suderinamumas;
- testai.

---

## Rule D-063

### Title

Backward-compatible Enumeration Extension

### Requirement

New enumeration values MAY be added only without changing the meaning of existing values.

### Reason

Preserves historical and implementation compatibility.

### Implication

Existing stored documents must retain their original interpretation.
---

# 8. Domain Services

Domain Services įgyvendina verslo logiką, kuri nepriklauso vienai konkrečiai Entity.

Jie:

- nevykdo UI logikos;
- nevykdo duomenų bazės operacijų;
- nekaupia būsenos;
- atlieka verslo skaičiavimus ir sprendimus.

Document Domain naudoja šiuos pagrindinius servisus:

- DocumentNumberingService
- DocumentTotalsService
- DocumentValidationService

Ateityje gali būti pridėti:

- DocumentConversionService
- DocumentTemplateService
- PaymentCalculationService

---

## Rule D-064

### Title

Stateless Services

### Requirement

Domain Services SHALL be stateless.

### Reason

Business calculations must be deterministic.

### Implication

A service SHALL NOT store document-specific state between calls.

---

## Rule D-065

### Title

Business Responsibility

### Requirement

Domain Services SHALL contain only business logic.

### Reason

Preserves architectural separation.

### Implication

Infrastructure code belongs outside the domain layer.

---

# 8.1 DocumentNumberingService

DocumentNumberingService atsako už oficialių dokumentų numerių suteikimą.

Joks kitas objektas negali generuoti dokumentų numerių.

Service naudoja:

- DocumentType;
- numeracijos seriją;
- einamąją seką.

Rezultatas:

DocumentNumber.

---

## Rule D-066

### Title

Single Number Generator

### Requirement

Only DocumentNumberingService SHALL assign official document numbers.

### Reason

Ensures uniqueness.

### Implication

Documents cannot generate their own numbers.

---

## Rule D-067

### Title

Number Assignment Time

### Requirement

Official document numbers SHALL be assigned only during document finalization.

### Reason

Draft documents are not official accounting records.

### Implication

Draft documents SHALL NOT consume official numbers.

---

## Rule D-068

### Title

Atomic Number Assignment

### Requirement

Number assignment SHALL be atomic.

### Reason

Prevents duplicate document numbers.

### Implication

Concurrent finalization SHALL NOT produce identical numbers.

---

## Rule D-069

### Title

Never Reuse Numbers

### Requirement

Assigned document numbers SHALL NEVER be reused.

### Reason

Accounting numbering must remain historically unique.

### Implication

Cancelled or permanently deleted documents keep their reserved number forever.

---

# 8.2 DocumentTotalsService

DocumentTotalsService atsako už visų finansinių sumų apskaičiavimą.

Jis analizuoja DocumentLine kolekciją.

Apskaičiuoja:

- subtotal;
- discounts;
- taxable amount;
- VAT;
- total;
- total in words (jeigu reikalinga).

---

## Rule D-070

### Title

Calculated Totals Only

### Requirement

Financial totals SHALL always be calculated by DocumentTotalsService.

### Reason

Prevents inconsistent accounting data.

### Implication

Users SHALL NOT edit calculated totals directly.

---

## Rule D-071

### Title

Source of Calculation

### Requirement

DocumentTotalsService SHALL calculate totals only from DocumentLines.

### Reason

Maintains a single source of truth.

### Implication

No manual total adjustments are allowed.

---

## Rule D-072

### Title

Deterministic Calculation

### Requirement

Identical input SHALL always produce identical totals.

### Reason

Financial calculations must be reproducible.

### Implication

Hidden mutable state is prohibited.

---

## Rule D-073

### Title

Currency Precision

### Requirement

Financial calculations SHALL preserve accounting precision.

### Reason

Avoids cumulative rounding errors.

### Implication

Binary floating point arithmetic SHALL NOT be used.

---

# 8.3 DocumentValidationService

DocumentValidationService atsako už dokumento verslo taisyklių tikrinimą.

Jis netaiso klaidų.

Jis tik nustato:

- ar dokumentas galioja;
- kokios rastos klaidos;
- kokie perspėjimai.

Rezultatas turi būti struktūrizuotas.

---

## Rule D-074

### Title

Validation Responsibility

### Requirement

DocumentValidationService SHALL validate business rules but SHALL NOT modify the document.

### Reason

Validation and correction are different responsibilities.

### Implication

Validation returns results without changing domain objects.

---

## Rule D-075

### Title

Structured Validation

### Requirement

Validation SHALL return structured validation results.

### Reason

Allows UI to present meaningful feedback.

### Implication

Validation errors SHALL NOT be represented only as plain text.

---

## Rule D-076

### Title

Draft Validation

### Requirement

Draft validation MAY allow incomplete information.

### Reason

Documents are created incrementally.

### Implication

Missing fields do not necessarily block saving a draft.

---

## Rule D-077

### Title

Finalization Validation

### Requirement

Finalization SHALL require complete business validation.

### Reason

Official accounting documents must be complete.

### Implication

A document that fails validation SHALL NOT be finalized.

---

# 8.4 Service Cooperation

Tipinis dokumento finalizavimo procesas:

```text
User
 │
 ▼
Document.finalize()
 │
 ├──────────────► DocumentValidationService
 │                    │
 │                    ▼
 │              Validation OK
 │
 ├──────────────► DocumentTotalsService
 │                    │
 │                    ▼
 │             Totals calculated
 │
 ├──────────────► DocumentNumberingService
 │                    │
 │                    ▼
 │             Number assigned
 │
 ▼
LifecycleState = FINALIZED
```

Document koordinuoja procesą.

Servisai vykdo tik savo atsakomybę.

---

## Rule D-078

### Title

Aggregate Coordination

### Requirement

The Document Aggregate SHALL coordinate business services.

### Reason

Aggregate Root is responsible for maintaining consistency.

### Implication

Services SHALL NOT call each other directly to perform lifecycle operations.

---

## Rule D-079

### Title

Single Responsibility

### Requirement

Each Domain Service SHALL have exactly one primary business responsibility.

### Reason

Improves maintainability and testability.

### Implication

Complex services SHALL be split instead of accumulating unrelated logic.

---

## Rule D-080

### Title

Service Independence

### Requirement

Domain Services SHALL remain independent from UI, persistence and infrastructure.

### Reason

Allows business logic to be reused across different application layers.

### Implication

Services can be tested without database or graphical interface.
---

# 9. Document Lifecycle

Document Lifecycle apibrėžia dokumento gyvavimo kelią nuo sukūrimo iki galutinės būsenos.

Pagrindinės būsenos:

- `DRAFT`;
- `FINALIZED`;
- `CANCELLED`.

Galimi pagrindiniai perėjimai:

```text
Create
  │
  ▼
DRAFT
  │
  │ Finalize
  ▼
FINALIZED
  │
  │ Cancel
  ▼
CANCELLED
```

Papildoma administracinė operacija:

```text
FINALIZED
  │
  │ Permanent Delete
  │  only when explicitly enabled
  ▼
Aggregate removed
```

Nuolatinis ištrynimas nėra gyvavimo būsena.

Tai išskirtinė administracinė operacija, kuri gali būti leidžiama tik sistemos nustatymuose.

---

# 9.1 Draft Creation

Naujas dokumentas visada pradedamas kaip juodraštis.

Juodraštis gali būti kuriamas:

- kaip visiškai naujas dokumentas;
- kopijuojant kitą dokumentą;
- konvertuojant kitą dokumentą pagal atskirai apibrėžtą procesą;
- naudojant dokumento tipo numatytuosius nustatymus.

Juodraštis dar nėra oficialus apskaitinis dokumentas.

Jis neturi oficialaus dokumento numerio.

---

## Rule D-081

### Title

Draft Creation

### Requirement

Every newly created Document SHALL start in the `DRAFT` LifecycleState.

### Reason

A document must be prepared before becoming an official record.

### Implication

Direct creation of finalized or cancelled documents is prohibited.

---

## Rule D-082

### Title

No Official Number for Draft

### Requirement

A Draft Document SHALL NOT have an official DocumentNumber.

### Reason

Drafts are not issued accounting records.

### Implication

Saving, editing or reopening a Draft does not consume a numbering sequence value.

---

## Rule D-083

### Title

Incomplete Draft

### Requirement

A Draft Document MAY contain incomplete business information.

### Reason

Document preparation is incremental.

### Implication

Draft saving and finalization use different validation levels.

---

## Rule D-084

### Title

Draft Persistence

### Requirement

A Draft Document MAY be saved and reopened multiple times before finalization.

### Reason

Users must be able to continue unfinished work.

### Implication

Draft persistence SHALL NOT change its lifecycle or assign an official number.

---

# 9.2 Draft Editing

Tik juodraštis gali būti laisvai redaguojamas.

Redaguojant juodraštį gali būti keičiama:

- dokumento data;
- mokėjimo terminas;
- pirkėjas;
- pardavėjo duomenys, kol jie dar neužfiksuoti finalizavimo metu;
- dokumento eilutės;
- kainos;
- kiekiai;
- nuolaidos;
- PVM duomenys;
- pastabos;
- pateikimo nustatymai;
- kiti dokumento tipui leidžiami laukai.

Kiekvienas verslo pakeitimas turi išlaikyti Document Aggregate vidinį vientisumą.

---

## Rule D-085

### Title

Draft Editability

### Requirement

Only a Document in the `DRAFT` LifecycleState SHALL be editable as a business document.

### Reason

Issued accounting data must remain historically stable.

### Implication

Finalized and cancelled documents cannot be edited as drafts.

---

## Rule D-086

### Title

Controlled Modification

### Requirement

Draft modifications SHALL be performed through Document business operations.

### Reason

The Aggregate Root must protect its invariants.

### Implication

Application and UI layers SHALL NOT directly mutate internal Document state.

---

## Rule D-087

### Title

Totals Recalculation

### Requirement

Any Draft change affecting financial values SHALL invalidate and recalculate DocumentTotals.

### Reason

Displayed and persisted totals must reflect current line data.

### Implication

Previously calculated totals cannot remain authoritative after a financial change.

---

## Rule D-088

### Title

Draft Type Change

### Requirement

A Draft Document MAY change its DocumentType only while the change can be completed without violating type-specific business rules.

### Reason

A user may select the wrong document type during preparation.

### Implication

The change requires revalidation and may reset incompatible type-specific settings.

---

# 9.3 Draft Deletion

Kadangi juodraštis neturi oficialaus dokumento numerio ir nėra išduotas apskaitinis dokumentas, jis gali būti ištrintas.

Juodraščio ištrynimas pašalina:

- Document Aggregate;
- jo eilutes;
- apskaičiuotas sumas;
- momentines kopijas;
- techninius metaduomenis;
- kitus jam priklausančius duomenis.

---

## Rule D-089

### Title

Draft Deletion

### Requirement

A Draft Document MAY be permanently deleted.

### Reason

An unissued document is not part of the official accounting history.

### Implication

Deleting a Draft does not create a cancelled record and does not affect numbering.

---

## Rule D-090

### Title

Draft Delete Confirmation

### Requirement

Draft deletion SHOULD require user confirmation when the Document contains entered business data.

### Reason

Prevents accidental loss of work.

### Implication

Empty, automatically created Drafts MAY be removed with a lighter confirmation process.

---

# 9.4 Finalization

Finalizavimas yra pagrindinis dokumento gyvavimo ciklo veiksmas.

Finalizuojant:

1. patikrinama dokumento būsena;
2. atliekama pilna verslo validacija;
3. apskaičiuojamos galutinės sumos;
4. sukuriamos arba užfiksuojamos istorinės momentinės kopijos;
5. atominiu būdu suteikiamas oficialus dokumento numeris;
6. užfiksuojamas finalizavimo laikas;
7. LifecycleState pakeičiamas į `FINALIZED`;
8. apskaitinė dokumento dalis tampa nekintama.

Finalizavimas turi būti vykdomas kaip vienas nuoseklus procesas.

---

## Rule D-091

### Title

Draft-only Finalization

### Requirement

Only a Document in the `DRAFT` LifecycleState SHALL be finalized.

### Reason

Prevents repeated or invalid lifecycle transitions.

### Implication

Finalized and cancelled Documents cannot be finalized again.

---

## Rule D-092

### Title

Complete Validation Before Finalization

### Requirement

A Document SHALL pass complete finalization validation before an official number is assigned.

### Reason

Invalid documents must not consume official accounting numbers.

### Implication

Validation failure leaves the Document as Draft and without an official number.

---

## Rule D-093

### Title

Final Totals

### Requirement

DocumentTotals SHALL be recalculated and confirmed during finalization.

### Reason

The finalized record must contain authoritative financial results.

### Implication

Finalization SHALL NOT rely solely on previously cached Draft totals.

---

## Rule D-094

### Title

Snapshot Finalization

### Requirement

All historical snapshots required to reproduce the Document SHALL be completed and frozen during finalization.

### Reason

Future master-data changes must not alter the issued document.

### Implication

Finalization fails when mandatory snapshot data cannot be created.

---

## Rule D-095

### Title

Finalization Number Assignment

### Requirement

DocumentNumber SHALL be assigned during the successful finalization operation.

### Reason

The number identifies the officially issued document.

### Implication

Number assignment and lifecycle transition must belong to the same consistency boundary.

---

## Rule D-096

### Title

Atomic Finalization

### Requirement

Finalization SHALL be atomic from the application perspective.

### Reason

The system must not leave a partially finalized document.

### Implication

If any mandatory finalization step fails, the Document remains Draft and no official result is committed.

---

## Rule D-097

### Title

Finalized Immutability

### Requirement

The accounting content of a Finalized Document SHALL be immutable.

### Reason

Issued documents must preserve historical accuracy.

### Implication

Seller, buyer, lines, tax data, dates, totals, type and official number cannot be edited.

---

# 9.5 Changes Allowed After Finalization

Finalizuoto dokumento apskaitiniai duomenys nekinta.

Tačiau gali būti keičiami su dokumento vykdymu susiję proceso duomenys, jeigu jie nekeičia išduoto dokumento turinio.

Galimi pavyzdžiai:

- PaymentStatus;
- DeliveryStatus;
- AcceptanceStatus;
- faktinio apmokėjimo data;
- išsiuntimo techniniai duomenys;
- vidinės sistemos žymos;
- procesiniai komentarai, kurie nėra dokumento spausdinamo turinio dalis.

Šie pakeitimai turi būti aiškiai atskirti nuo apskaitinio dokumento turinio.

---

## Rule D-098

### Title

Operational Metadata After Finalization

### Requirement

Operational process data MAY be updated after finalization when it does not alter the issued accounting content.

### Reason

Payment, delivery and acceptance continue after document issuance.

### Implication

Such changes SHALL NOT modify historical snapshots, totals, lines or DocumentNumber.

---

## Rule D-099

### Title

Printed Content Protection

### Requirement

Data that affects the issued or reproducible printed document SHALL NOT be modified after finalization.

### Reason

A regenerated document must match the original accounting record.

### Implication

Fields presented in the official document belong to the immutable historical content unless explicitly classified otherwise.

---

# 9.6 Cancellation

Atšaukimas naudojamas tada, kai finalizuotas dokumentas turi likti apskaitos istorijoje, tačiau nebeturi būti laikomas aktyviu.

Atšaukiant:

- oficialus numeris išsaugomas;
- istoriniai duomenys išsaugomi;
- LifecycleState pakeičiamas į `CANCELLED`;
- užfiksuojamas atšaukimo laikas;
- gali būti saugoma atšaukimo priežastis;
- dokumentas negali būti redaguojamas ar iš naujo finalizuojamas.

Atšaukimas nėra dokumento ištrynimas.

---

## Rule D-100

### Title

Finalized-only Cancellation

### Requirement

Only a Finalized Document SHALL be cancelled.

### Reason

A Draft can be deleted and an already cancelled document cannot be cancelled again.

### Implication

Cancellation from Draft or Cancelled state is prohibited.

---

## Rule D-101

### Title

Cancellation Preservation

### Requirement

Cancellation SHALL preserve the complete Document Aggregate and its official number.

### Reason

The historical record must remain auditable.

### Implication

Cancellation does not delete lines, snapshots, totals or attached historical references.

---

## Rule D-102

### Title

Cancellation Reason

### Requirement

The system SHOULD require a cancellation reason.

### Reason

Provides an audit explanation for why the document became inactive.

### Implication

The reason becomes immutable cancellation metadata.

---

## Rule D-103

### Title

Cancelled Immutability

### Requirement

A Cancelled Document SHALL remain immutable.

### Reason

Cancellation must not become an alternative editing mechanism.

### Implication

A cancelled document cannot return to Draft or Finalized state.

---

## Rule D-104

### Title

Number Retention After Cancellation

### Requirement

The DocumentNumber of a Cancelled Document SHALL remain permanently reserved.

### Reason

Accounting numbering history cannot be rewritten.

### Implication

The numbering sequence never rolls back after cancellation.

---

# 9.7 Correction of Finalized Documents

Finalizuotas dokumentas netaisomas tiesiogiai.

Jeigu jame randama klaida, priklausomai nuo verslo situacijos gali būti:

- atšaukiamas klaidingas dokumentas;
- sukuriamas naujas dokumentas;
- sukuriama ankstesnio dokumento kopija kaip naujas Draft;
- ateityje sukuriamas kreditinis ar korekcinis dokumentas;
- atliekamas kitas teisės aktuose ir sistemos architektūroje numatytas veiksmas.

Naujas dokumentas visada gauna naują identitetą ir, finalizavimo metu, naują oficialų numerį.

---

## Rule D-105

### Title

No Direct Correction

### Requirement

A Finalized Document SHALL NOT be returned to Draft for correction.

### Reason

Returning an issued document to an editable state would destroy historical integrity.

### Implication

Corrections require a new business document or cancellation process.

---

## Rule D-106

### Title

Copy as New Draft

### Requirement

The system MAY create a new Draft by copying data from an existing Document.

### Reason

Reduces repeated data entry while preserving history.

### Implication

The copied Draft receives a new identifier, has no official number and is independent from the source Document.

---

## Rule D-107

### Title

Source Reference

### Requirement

A corrective or copied Document MAY retain a reference to its source Document.

### Reason

Improves traceability.

### Implication

The reference SHALL NOT create shared mutable business data between aggregates.

---

# 9.8 Permanent Deletion of Finalized Documents

Pagal numatytąją sistemos elgseną finalizuoti dokumentai nėra šalinami.

Jie atšaukiami ir paliekami istorijoje.

Tačiau Produkto savininko patvirtintu sprendimu sistemos nustatymuose gali būti įjungta galimybė visam laikui ištrinti finalizuotą arba atšauktą dokumentą.

Siūlomi nustatymai:

```text
DocumentManagementSettings

allow_hard_delete_finalized
delete_related_files_by_default
```

`allow_hard_delete_finalized` nustato, ar leidžiamas nuolatinis finalizuotų ir atšauktų dokumentų trynimas.

`delete_related_files_by_default` nustato numatytąją susijusių sugeneruotų failų trynimo parinktį.

Ši operacija skirta išskirtiniams administraciniams atvejams.

---

## Rule D-108

### Title

Hard Delete Disabled by Default

### Requirement

Permanent deletion of Finalized and Cancelled Documents SHALL be disabled by default.

### Reason

Historical accounting records should normally be preserved.

### Implication

The standard user workflow uses cancellation instead of permanent deletion.

---

## Rule D-109

### Title

Explicit Hard Delete Setting

### Requirement

A Finalized or Cancelled Document MAY be permanently deleted only when `allow_hard_delete_finalized` is explicitly enabled.

### Reason

The operation must be an intentional Product Owner-controlled capability.

### Implication

Without the setting, the application SHALL reject the operation.

---

## Rule D-110

### Title

Strong Confirmation

### Requirement

Permanent deletion of a Finalized or Cancelled Document SHALL require strong user confirmation.

### Reason

The operation is irreversible and removes accounting history from the system.

### Implication

A simple single-click deletion SHALL NOT be sufficient.

---

## Rule D-111

### Title

Complete Aggregate Deletion

### Requirement

Hard delete SHALL remove the Document Aggregate and all dependent persisted data owned exclusively by it.

### Reason

Prevents orphaned internal records.

### Implication

Lines, snapshots, totals, metadata and other owned records are removed together.

---

## Rule D-112

### Title

Related File Policy

### Requirement

Deletion of generated PDF or export files SHALL follow the explicit user choice or the configured `delete_related_files_by_default` setting.

### Reason

Database records and external files may require different retention decisions.

### Implication

The deletion confirmation must communicate which related files will be removed or retained.

---

## Rule D-113

### Title

Deleted Number Never Reused

### Requirement

The DocumentNumber of a permanently deleted Document SHALL NEVER be reused.

### Reason

Number reuse would create ambiguous or conflicting accounting history.

### Implication

Hard delete SHALL NOT decrement, reset or roll back the numbering sequence.

---

## Rule D-114

### Title

No Lifecycle Transition for Hard Delete

### Requirement

Hard delete SHALL remove the aggregate rather than assign a new LifecycleState.

### Reason

A deleted aggregate cannot retain a persistent lifecycle state.

### Implication

`DELETED` SHALL NOT be added to LifecycleState.

---

# 9.9 Lifecycle Transition Matrix

Leidžiami perėjimai:

| Dabartinė būsena | Veiksmas | Rezultatas |
|---|---|---|
| Nėra dokumento | Create | `DRAFT` |
| `DRAFT` | Save | `DRAFT` |
| `DRAFT` | Edit | `DRAFT` |
| `DRAFT` | Delete | Aggregate pašalinamas |
| `DRAFT` | Finalize | `FINALIZED` |
| `FINALIZED` | Update operational status | `FINALIZED` |
| `FINALIZED` | Cancel | `CANCELLED` |
| `FINALIZED` | Hard delete, kai leidžiama | Aggregate pašalinamas |
| `CANCELLED` | Update permitted operational metadata | `CANCELLED` |
| `CANCELLED` | Hard delete, kai leidžiama | Aggregate pašalinamas |

Draudžiami perėjimai:

| Dabartinė būsena | Draudžiamas veiksmas |
|---|---|
| `DRAFT` | Cancel |
| `FINALIZED` | Edit accounting content |
| `FINALIZED` | Finalize again |
| `FINALIZED` | Return to Draft |
| `CANCELLED` | Edit accounting content |
| `CANCELLED` | Finalize |
| `CANCELLED` | Return to Draft |
| `CANCELLED` | Return to Finalized |

---

## Rule D-115

### Title

Explicit Lifecycle Transitions

### Requirement

Every LifecycleState change SHALL occur through an explicit documented business operation.

### Reason

Prevents accidental or hidden state changes.

### Implication

Direct assignment of LifecycleState outside Document behaviour is prohibited.

---

## Rule D-116

### Title

Invalid Transition Rejection

### Requirement

The Document Aggregate SHALL reject every lifecycle transition not explicitly permitted by this specification.

### Reason

Protects the lifecycle state machine.

### Implication

Undefined transitions SHALL NOT be silently accepted or automatically corrected.

---

# 9.10 Lifecycle Audit

Svarbūs gyvavimo ciklo įvykiai turi būti atsekami.

Mažiausiai turi būti saugoma:

- sukūrimo data ir laikas;
- paskutinio pakeitimo data ir laikas;
- finalizavimo data ir laikas;
- atšaukimo data ir laikas;
- veiksmą atlikęs naudotojas, kai sistemoje egzistuoja naudotojų identifikavimas;
- atšaukimo priežastis;
- nuolatinio ištrynimo patvirtinimo informacija, jeigu taikomas atskiras audito mechanizmas.

Kadangi hard delete pašalina patį Aggregate, galimas bendras sistemos audito žurnalas nėra Document Aggregate dalis.

---

## Rule D-117

### Title

Lifecycle Timestamps

### Requirement

Creation, finalization and cancellation events SHALL record their respective timestamps.

### Reason

Lifecycle history must be traceable.

### Implication

These timestamps are maintained automatically and cannot be manually edited.

---

## Rule D-118

### Title

Lifecycle Actor

### Requirement

When user identity is available, lifecycle-changing operations SHOULD record the responsible actor.

### Reason

Improves accountability and auditability.

### Implication

The actor reference belongs to lifecycle metadata rather than editable document content.

---

## Rule D-119

### Title

External Hard Delete Audit

### Requirement

When permanent deletion auditing is required, the audit record SHALL exist outside the deleted Document Aggregate.

### Reason

The aggregate itself no longer exists after hard delete.

### Implication

Audit logging is an Application or Infrastructure responsibility and SHALL NOT prevent aggregate removal.
---

# 10. Business Rules

Business Rules apibrėžia privalomą Document Aggregate elgseną ir jo duomenų tarpusavio suderinamumą.

Šios taisyklės taikomos nepriklausomai nuo:

- naudotojo sąsajos;
- duomenų bazės struktūros;
- PDF generavimo technologijos;
- konkretaus Application Service;
- dokumento atvaizdavimo formos.

Business Rules saugo Document Aggregate vientisumą.

Jos negali būti apeinamos tiesiogiai keičiant objektų laukus, ORM įrašus ar UI būseną.

---

## Rule D-120

### Title

Aggregate Invariant Protection

### Requirement

The Document Aggregate SHALL enforce all mandatory business invariants before accepting a state-changing operation.

### Reason

Invalid document state must not enter the domain model.

### Implication

Application, UI and persistence layers SHALL NOT bypass Document business operations.

---

## Rule D-121

### Title

No Primitive State Mutation

### Requirement

Business-significant Document values SHALL be changed through explicit domain operations.

### Reason

Direct field assignment can bypass validation and lifecycle rules.

### Implication

Public mutable fields SHALL NOT be used for protected business state.

---

## Rule D-122

### Title

Consistent Aggregate State

### Requirement

After every successful business operation, the Document Aggregate SHALL remain internally consistent.

### Reason

Partially applied operations create invalid accounting data.

### Implication

An operation either completes fully or leaves the aggregate unchanged.

---

# 10.1 Document Identity

Kiekvienas Document turi vidinį sistemos identitetą.

Šis identitetas nėra oficialus dokumento numeris.

Vidinis identitetas naudojamas:

- Aggregate atpažinimui;
- duomenų bazės ryšiams;
- nuorodoms tarp dokumentų;
- auditui;
- techniniam dokumento suradimui.

Oficialus DocumentNumber yra atskira verslo reikšmė, suteikiama tik finalizavimo metu.

Pavyzdys:

```text
Internal Document ID:
8d7dbca4-642e-40d4-b8b9-5be330e10db4

Official Document Number:
SF-000128
```

Juodraštis turi vidinį identitetą, tačiau neturi oficialaus numerio.

---

## Rule D-123

### Title

Internal Identity

### Requirement

Every Document SHALL receive a unique internal identity when created.

### Reason

Draft Documents must be identifiable before official numbering.

### Implication

The internal identity exists throughout the complete aggregate lifetime.

---

## Rule D-124

### Title

Identity and Number Separation

### Requirement

Document identity and DocumentNumber SHALL remain separate concepts.

### Reason

The official number does not exist during the Draft lifecycle.

### Implication

DocumentNumber SHALL NOT be used as the aggregate primary identity.

---

## Rule D-125

### Title

Immutable Internal Identity

### Requirement

The internal Document identity SHALL be immutable.

### Reason

Changing identity would break references and aggregate continuity.

### Implication

Copying or converting a Document creates a new internal identity.

---

# 10.2 Official Document Numbering

Oficialų dokumento numerį sudaro:

- numeracijos serija;
- sekos numeris;
- formatavimo taisyklė;
- galutinis tekstinis atvaizdavimas.

Pavyzdinė struktūra:

```text
Series:     SF
Sequence:   128
Formatted:  SF-000128
```

Numeracijos serija gali priklausyti nuo:

- DocumentType;
- įmonės;
- finansinių metų;
- sistemos nustatymų;
- būsimos kelių padalinių architektūros.

Numeracijos sekos valdymas yra atskira infrastruktūros ir transakcijų atsakomybė, tačiau jos verslo principai apibrėžiami šiame domene.

---

## Rule D-126

### Title

Number Composition

### Requirement

An official DocumentNumber SHALL contain a configured numbering series and a unique sequence value.

### Reason

The complete number must identify its numbering context.

### Implication

A sequence value without its series SHALL NOT be treated as a complete official number.

---

## Rule D-127

### Title

Configured Series

### Requirement

The numbering series SHALL be resolved from the applicable DocumentType and numbering configuration.

### Reason

Different document types may require separate numbering sequences.

### Implication

The UI SHALL NOT invent or concatenate numbering series independently.

---

## Rule D-128

### Title

Series Required for Finalization

### Requirement

A valid numbering series SHALL exist before a Document can be finalized.

### Reason

The system cannot create a valid official number without a numbering context.

### Implication

Missing or invalid numbering configuration blocks finalization.

---

## Rule D-129

### Title

Sequence Monotonicity

### Requirement

Within one numbering sequence, assigned sequence values SHALL increase monotonically.

### Reason

Accounting document numbering must remain ordered and traceable.

### Implication

The next assigned value SHALL be greater than every previously assigned value in that sequence.

---

## Rule D-130

### Title

Numbering Scope

### Requirement

Every numbering sequence SHALL have an explicitly defined scope.

### Reason

Uniqueness cannot be guaranteed without knowing where the sequence applies.

### Implication

The scope MAY include Company, DocumentType, series and accounting period.

---

## Rule D-131

### Title

Number Uniqueness Within Scope

### Requirement

A formatted DocumentNumber SHALL be unique within its defined numbering scope.

### Reason

Two official documents cannot share the same accounting identifier.

### Implication

The persistence layer SHALL enforce a compatible uniqueness constraint.

---

## Rule D-132

### Title

Formatting Does Not Change Meaning

### Requirement

DocumentNumber formatting SHALL NOT alter the underlying sequence value.

### Reason

Display formatting and sequence semantics are separate concerns.

### Implication

Changing padding or separators does not reset or create a new sequence unless the numbering configuration explicitly defines a new scope.

---

## Rule D-133

### Title

Preserved Final Number

### Requirement

The complete formatted DocumentNumber assigned during finalization SHALL be preserved historically.

### Reason

Future formatting configuration changes must not alter issued documents.

### Implication

A finalized Document does not regenerate its number from current settings.

---

## Rule D-134

### Title

No Manual Sequence Rollback

### Requirement

Users SHALL NOT decrease or roll back an active numbering sequence below an already assigned value.

### Reason

Rollback could produce duplicate or reused numbers.

### Implication

Administrative numbering changes require validation against historical assignments.

---

## Rule D-135

### Title

Numbering Gap Acceptance

### Requirement

The system MAY contain gaps between assigned document numbers.

### Reason

Cancelled, deleted or failed external processes must not cause number reuse.

### Implication

A numbering gap SHALL NOT automatically be repaired by reassigning historical numbers.

---

## Rule D-136

### Title

Failed Finalization Number Handling

### Requirement

A failed finalization operation SHALL NOT leave a Document in a partially numbered finalized state.

### Reason

Number assignment and finalization belong to one consistency operation.

### Implication

Transaction handling must either commit the complete finalization or roll back the document change according to the numbering storage strategy.

---

# 10.3 Business Dates

Document gali turėti kelias skirtingas datas.

Pagrindinės datos:

- `document_date`;
- `due_date`;
- `created_at`;
- `updated_at`;
- `finalized_at`;
- `cancelled_at`.

Papildomos datos gali būti:

- paslaugos suteikimo data;
- prekių pristatymo data;
- apmokėjimo data;
- pasiūlymo galiojimo data;
- išsiuntimo data.

Kiekviena data turi vieną aiškią verslo reikšmę.

Techniniai laiko žymenys nėra keičiami naudotojo, išskyrus atskirai apibrėžtas importo ar migracijos procedūras.

---

## Rule D-137

### Title

Document Date Required

### Requirement

A Document SHALL have a valid document date before finalization.

### Reason

An issued business document must belong to a defined date.

### Implication

A missing document date blocks finalization.

---

## Rule D-138

### Title

Draft Date Editing

### Requirement

The document date MAY be changed while the Document is Draft.

### Reason

The user may prepare a document for a different business date.

### Implication

Changing the date triggers validation of all date-dependent rules.

---

## Rule D-139

### Title

Finalized Date Immutability

### Requirement

The document date of a Finalized Document SHALL be immutable.

### Reason

The date is part of the issued accounting content.

### Implication

A changed date requires a new corrective Document.

---

## Rule D-140

### Title

Due Date Applicability

### Requirement

A due date SHALL be required only when the applicable DocumentType and payment terms require it.

### Reason

Not every document creates a payable obligation.

### Implication

Commercial offers and other non-payable documents MAY omit the due date.

---

## Rule D-141

### Title

Due Date Order

### Requirement

When present, the due date SHALL NOT be earlier than the document date unless an explicit business rule allows it.

### Reason

A payment obligation normally cannot expire before the document exists.

### Implication

Invalid date order blocks finalization.

---

## Rule D-142

### Title

Payment Term Derivation

### Requirement

A due date MAY be derived from the document date and a configured PaymentTerm.

### Reason

Automatic calculation reduces data-entry errors.

### Implication

The resulting due date becomes an explicit Document value and is preserved during finalization.

---

## Rule D-143

### Title

Finalization Timestamp

### Requirement

`finalized_at` SHALL record when successful finalization was committed.

### Reason

The lifecycle event requires an auditable timestamp.

### Implication

The value is system-maintained and cannot be manually edited.

---

## Rule D-144

### Title

Cancellation Timestamp

### Requirement

`cancelled_at` SHALL be present only when LifecycleState is `CANCELLED`.

### Reason

The timestamp and lifecycle state must remain consistent.

### Implication

A Draft or Finalized Document SHALL NOT contain a cancellation timestamp.

---

## Rule D-145

### Title

Date and Time Separation

### Requirement

Business dates and technical timestamps SHALL remain separate concepts.

### Reason

A document date represents a business day, while lifecycle timestamps represent precise system events.

### Implication

A timestamp SHALL NOT silently replace a required business date.

---

## Rule D-146

### Title

Timezone Consistency

### Requirement

Lifecycle timestamps SHALL use one application-wide timezone strategy.

### Reason

Inconsistent timezone handling creates incorrect audit ordering.

### Implication

Storage and display timezone rules SHALL be defined centrally outside the Document Aggregate.

---

# 10.4 Seller Information

Seller information identifies the company issuing the document.

Seller data may originate from the active Company profile, but the final document stores its own historical SellerSnapshot.

Seller information may include:

- legal name;
- company code;
- VAT payer code;
- address;
- phone number;
- email address;
- website;
- bank name;
- bank account;
- other legally or commercially required details.

The exact set of required seller fields depends on:

- seller legal form;
- VAT payer status;
- DocumentType;
- applicable document template;
- current business requirements.

---

## Rule D-147

### Title

Seller Required

### Requirement

Every Document SHALL be associated with exactly one seller.

### Reason

A business document must identify its issuer.

### Implication

A Document cannot be finalized without valid seller information.

---

## Rule D-148

### Title

Seller Source

### Requirement

A Draft MAY initialize seller information from the active Company profile.

### Reason

Current company master data is the normal source for new documents.

### Implication

The Document SHALL NOT depend on the Company profile after finalization.

---

## Rule D-149

### Title

Seller Snapshot

### Requirement

Finalization SHALL preserve all seller information required to reproduce the issued Document.

### Reason

Later Company profile changes must not alter historical documents.

### Implication

PDF regeneration uses SellerSnapshot rather than current Company data.

---

## Rule D-150

### Title

Seller Name Required

### Requirement

Seller legal or business name SHALL be present before finalization.

### Reason

The issuer must be identifiable.

### Implication

An empty seller name blocks finalization.

---

## Rule D-151

### Title

Seller Registration Data

### Requirement

Seller registration identifiers SHALL be validated according to their configured applicability.

### Reason

Different sellers may have different legally required identifiers.

### Implication

A missing non-applicable identifier does not invalidate the Document, but a required one does.

---

## Rule D-152

### Title

Seller VAT Status

### Requirement

The seller VAT payer status SHALL be explicit and preserved in TaxSnapshot.

### Reason

VAT calculation and presentation depend on the seller's tax status at issuance time.

### Implication

Current Company VAT status changes SHALL NOT affect finalized Documents.

---

## Rule D-153

### Title

Seller VAT Code Consistency

### Requirement

When the seller is marked as a VAT payer, a valid VAT payer identifier SHALL be present when required by the configured jurisdiction rules.

### Reason

Tax status and identifying data must not contradict each other.

### Implication

An inconsistent VAT payer configuration blocks finalization.

---

## Rule D-154

### Title

Seller Bank Data Applicability

### Requirement

Seller payment account details SHALL be required only when the DocumentType, template or payment method requires them.

### Reason

Not every document needs payment instructions.

### Implication

Missing bank details do not invalidate non-payable documents.

---

## Rule D-155

### Title

Seller Draft Refresh

### Requirement

A Draft MAY explicitly refresh its seller information from the current Company profile.

### Reason

Company information may change while a Draft is being prepared.

### Implication

Refreshing SHALL be a visible business operation and SHALL replace only permitted Draft seller data.

---

## Rule D-156

### Title

No Automatic Historical Refresh

### Requirement

Finalized and Cancelled Documents SHALL NOT automatically refresh seller information from Company master data.

### Reason

Historical content must remain unchanged.

### Implication

Master-data synchronization applies only to eligible Draft Documents.

---

# 10.5 Buyer Information

Buyer information identifies the recipient or customer of the document.

Buyer data may originate from:

- Customer master data;
- manually entered one-time buyer information;
- imported transaction data;
- a previous Document copied into a new Draft.

Finalization preserves the buyer information in BuyerSnapshot.

Buyer information may include:

- buyer name;
- company or personal identifier;
- VAT payer code;
- address;
- phone number;
- email address;
- delivery details;
- contact person;
- other document-specific details.

Ne visi DocumentType privalo turėti vienodą pirkėjo duomenų rinkinį.

---

## Rule D-157

### Title

Buyer Applicability

### Requirement

Buyer information SHALL be required according to the applicable DocumentType and finalization policy.

### Reason

Different document types may have different recipient requirements.

### Implication

A type-specific validation rule determines the minimum required buyer data.

---

## Rule D-158

### Title

Single Buyer Context

### Requirement

A Document SHALL represent one buyer context.

### Reason

One official document must have one clearly defined recipient.

### Implication

Multiple unrelated buyers SHALL NOT be combined into one Document.

---

## Rule D-159

### Title

Buyer Master-data Reference

### Requirement

A Draft MAY reference an existing Customer entity as the source of buyer information.

### Reason

Customer master data reduces repeated entry.

### Implication

The Customer reference does not replace BuyerSnapshot.

---

## Rule D-160

### Title

One-time Buyer

### Requirement

A Draft MAY contain manually entered buyer information without creating a persistent Customer entity.

### Reason

Not every transaction requires a permanent customer record.

### Implication

Finalization preserves the entered buyer data directly in BuyerSnapshot.

---

## Rule D-161

### Title

Buyer Name Requirement

### Requirement

When buyer identification is required, the buyer name SHALL be present before finalization.

### Reason

The recipient must be identifiable.

### Implication

An empty required buyer name blocks finalization.

---

## Rule D-162

### Title

Buyer Identifier Applicability

### Requirement

Buyer registration or personal identifiers SHALL be validated only when required by the DocumentType, buyer category or applicable business policy.

### Reason

Private individuals and legal entities may require different data.

### Implication

The system SHALL NOT require a company code for every buyer.

---

## Rule D-163

### Title

Buyer Snapshot

### Requirement

Finalization SHALL preserve all buyer data required to reproduce the issued Document.

### Reason

Later Customer changes must not alter historical documents.

### Implication

Finalized Document rendering uses BuyerSnapshot rather than current Customer data.

---

## Rule D-164

### Title

Buyer Draft Refresh

### Requirement

A Draft linked to a Customer MAY explicitly refresh buyer information from current Customer master data.

### Reason

Customer details may change before document issuance.

### Implication

Refresh is permitted only before finalization and requires revalidation.

---

## Rule D-165

### Title

No Automatic Buyer Synchronization

### Requirement

Customer master-data changes SHALL NOT automatically modify existing Documents.

### Reason

Automatic synchronization could unexpectedly change Draft content and must never change historical content.

### Implication

Draft refresh requires an explicit operation; finalized and cancelled Documents remain unchanged.

---

## Rule D-166

### Title

Buyer Contact Separation

### Requirement

Buyer legal identity and buyer contact information SHALL remain distinguishable.

### Reason

A contact person may change without changing the legal recipient.

### Implication

Contact name, phone and email SHALL NOT be treated as the buyer's legal identity.

---

## Rule D-167

### Title

Buyer and Delivery Address

### Requirement

Buyer legal address and delivery address MAY be stored separately.

### Reason

The recipient's registered location may differ from the delivery location.

### Implication

The template and DocumentType determine which address is presented.

---

## Rule D-168

### Title

Buyer Data Validation

### Requirement

Buyer data validation SHALL report field-specific errors and warnings.

### Reason

The user must understand which recipient information is invalid or incomplete.

### Implication

A generic “invalid buyer” message is insufficient for finalization feedback.
---

# 10.6 Document Lines

DocumentLine reprezentuoja vieną parduodamą objektą.

Tai gali būti:

- prekė;
- paslauga;
- darbo laikas;
- transportas;
- nuolaidos eilutė;
- kita parduodama pozicija.

Kiekviena eilutė priklauso tik vienam Document.

---

## Rule D-169

### Title

At Least One Line

### Requirement

A Document SHALL contain at least one DocumentLine before finalization.

### Reason

An accounting document without business content has no meaning.

### Implication

Empty Documents cannot be finalized.

---

## Rule D-170

### Title

Line Ownership

### Requirement

Every DocumentLine SHALL belong to exactly one Document.

### Reason

DocumentLines cannot exist independently.

### Implication

Removing the Document removes all its lines.

---

## Rule D-171

### Title

Line Ordering

### Requirement

DocumentLines SHALL preserve their explicit order.

### Reason

Printed documents must reproduce the intended order.

### Implication

Automatic sorting SHALL NOT change business order.

---

## Rule D-172

### Title

Sequential Line Numbers

### Requirement

Displayed line numbers SHALL be sequential.

### Reason

Improves readability.

### Implication

Deleting a line renumbers remaining visible line numbers.

---

## Rule D-173

### Title

Immutable Finalized Lines

### Requirement

DocumentLines SHALL become immutable after finalization.

### Reason

Issued accounting data must remain unchanged.

### Implication

Adding, removing or modifying lines is prohibited.

---

# 10.7 Quantities and Prices

Kiekviena eilutė turi:

- Quantity;
- Unit Price;
- PriceBasis;
- VatRate;
- VatTreatment.

Jeigu dokumento tipui leidžiamos nuolaidos, jos tampa eilutės verslo dalimi.

---

## Rule D-174

### Title

Positive Quantity

### Requirement

Quantity SHALL be greater than zero unless a future document type explicitly allows otherwise.

### Reason

Negative quantities require separate business documents.

### Implication

Zero or negative quantity blocks validation.

---

## Rule D-175

### Title

Non-negative Price

### Requirement

Unit Price SHALL NOT be negative.

### Reason

Negative prices create ambiguous accounting meaning.

### Implication

Corrections use dedicated business processes.

---

## Rule D-176

### Title

Explicit Price Basis

### Requirement

Each taxable line SHALL define its PriceBasis.

### Reason

Tax calculation depends on entered price meaning.

### Implication

Price interpretation cannot be inferred.

---

## Rule D-177

### Title

Line Independence

### Requirement

Each DocumentLine SHALL calculate its own financial values independently.

### Reason

Totals are derived from individual lines.

### Implication

Changing one line affects only recalculated totals.

---

# 10.8 Discounts

Nuolaidos gali būti:

- eilutės lygio;
- dokumento lygio (ateityje).

Nuolaidos nekeičia dokumento numeracijos ar gyvavimo ciklo.

---

## Rule D-178

### Title

Discount Range

### Requirement

Percentage discounts SHALL remain within valid configured limits.

### Reason

Invalid discounts produce invalid totals.

### Implication

Validation rejects unsupported values.

---

## Rule D-179

### Title

Discount Calculation

### Requirement

Discounts SHALL participate in total calculations through DocumentTotalsService.

### Reason

Ensures consistent accounting calculations.

### Implication

Manual total corrections are prohibited.

---

# 10.9 VAT Rules

PVM apskaičiavimas priklauso nuo:

- Seller VAT status;
- VatTreatment;
- VatRate;
- PriceBasis.

Document Domain nenumato konkrečių valstybės įstatymų.

Jis apibrėžia tik bendrus verslo principus.

---

## Rule D-180

### Title

Explicit VAT Behaviour

### Requirement

VAT calculation SHALL always use explicit VatTreatment and VatRate.

### Reason

Zero VAT may have multiple legal meanings.

### Implication

Numeric VAT alone is insufficient.

---

## Rule D-181

### Title

Non-VAT Seller

### Requirement

When Seller is not a VAT payer, VAT SHALL NOT be calculated as charged tax.

### Reason

Tax presentation depends on seller status.

### Implication

TaxSnapshot preserves the applied logic.

---

## Rule D-182

### Title

Historical VAT

### Requirement

Finalized VAT calculations SHALL remain reproducible.

### Reason

Historical accounting data must not change.

### Implication

Later VAT configuration changes do not affect finalized Documents.

---

# 10.10 Financial Calculations

Visi finansiniai skaičiavimai vykdomi naudojant Money Value Object.

Document saugo tik galutinį rezultatą.

Skaičiavimus atlieka DocumentTotalsService.

---

## Rule D-183

### Title

Single Calculation Engine

### Requirement

DocumentTotalsService SHALL be the only source of financial calculations.

### Reason

Avoids inconsistent totals.

### Implication

No duplicated calculation logic.

---

## Rule D-184

### Title

Deterministic Totals

### Requirement

The same Document content SHALL always produce identical totals.

### Reason

Accounting results must be reproducible.

### Implication

Calculation depends only on business input.

---

## Rule D-185

### Title

No Manual Totals

### Requirement

Calculated totals SHALL NOT be edited directly.

### Reason

Totals are derived values.

### Implication

Business data changes require recalculation.

---

# 10.11 Rounding

Apvalinimas yra apskaitos dalis.

Visas apvalinimo taisykles vykdo DocumentTotalsService.

---

## Rule D-186

### Title

Centralized Rounding

### Requirement

Financial rounding SHALL be performed only by DocumentTotalsService.

### Reason

Different rounding implementations produce inconsistent accounting results.

### Implication

UI SHALL NOT implement its own accounting rounding.

---

## Rule D-187

### Title

Consistent Rounding Rules

### Requirement

The same rounding rules SHALL be used throughout the application.

### Reason

Financial consistency.

### Implication

Reports, PDF and UI display identical totals.

---

# 10.12 Currency

Document Domain palaiko vieną dokumento valiutą.

Ateityje gali būti įvestas kelių valiutų palaikymas.

---

## Rule D-188

### Title

Single Document Currency

### Requirement

Every Document SHALL use exactly one currency.

### Reason

Mixed-currency accounting requires separate business rules.

### Implication

All line totals use the same currency.

---

## Rule D-189

### Title

Historical Currency

### Requirement

Finalized Documents SHALL preserve their currency.

### Reason

Historical financial values must remain reproducible.

### Implication

Future company default currency changes do not affect historical Documents.

---

# 10.13 Presentation Settings

Presentation Settings apibrėžia tik dokumento pateikimą.

Pavyzdžiai:

- logotipo rodymas;
- parašo rodymas;
- antspaudo rodymas;
- papildomi tekstai;
- šablono pasirinkimas.

Tai nėra apskaitos duomenys.

Finalizuojant sukuriamas PresentationSnapshot.

---

## Rule D-190

### Title

Presentation Snapshot

### Requirement

Presentation settings used during finalization SHALL be preserved.

### Reason

Regenerated documents should match the original presentation.

### Implication

Later template changes do not modify historical documents.

---

## Rule D-191

### Title

Presentation Independence

### Requirement

Presentation settings SHALL NOT change accounting content.

### Reason

Layout and business data are separate concerns.

### Implication

Changing a logo cannot modify totals or taxes.

---

# 10.14 Notes

Document gali turėti papildomas pastabas.

Pastabos gali būti:

- spausdinamos;
- vidinės;
- automatiškai sugeneruotos.

---

## Rule D-192

### Title

Note Classification

### Requirement

Document notes SHALL explicitly define their intended purpose.

### Reason

Printed and internal notes have different business meaning.

### Implication

Internal notes are never included in official document output.

---

## Rule D-193

### Title

Historical Printed Notes

### Requirement

Printed notes SHALL become immutable after finalization.

### Reason

They are part of the issued document.

### Implication

Editing printed notes requires a new Document.

---

# 10.15 Business Rule Summary

Business Rules together define the mandatory behaviour of the Document Aggregate.

They ensure:

- consistent lifecycle;
- immutable accounting history;
- deterministic calculations;
- correct numbering;
- reproducible historical documents;
- separation between accounting content and presentation.

---

## Rule D-194

### Title

Business Rule Authority

### Requirement

These Business Rules SHALL be considered authoritative for every implementation of the Document Domain.

### Reason

Maintains one consistent business model across the application.

### Implication

Implementation details SHALL conform to this specification.
---

# 11. Domain Events

Domain Events reprezentuoja reikšmingus verslo įvykius, įvykusius Document domene.

Įvykis aprašo faktą, kuris jau įvyko.

Jis nėra komanda.

Pavyzdžiui:

✔ DocumentFinalized

reiškia:

> Dokumentas jau sėkmingai finalizuotas.

o ne:

> Finalizuok dokumentą.

Domain Events leidžia kitiems sistemos moduliams reaguoti į Document domeno pokyčius nepažeidžiant Aggregate ribų.

---

## Rule D-195

### Title

Past Tense Events

### Requirement

Domain Events SHALL represent completed business facts.

### Reason

Events describe what has happened.

### Implication

Commands and events SHALL remain separate concepts.

---

## Rule D-196

### Title

Immutable Events

### Requirement

Published Domain Events SHALL be immutable.

### Reason

Historical business facts cannot change.

### Implication

Event data is read-only after publication.

---

## Rule D-197

### Title

Domain Ownership

### Requirement

Every Domain Event SHALL belong to exactly one Domain.

### Reason

Avoids ambiguous business ownership.

### Implication

Document events belong exclusively to Document Domain.

---

# 11.1 Event Publication

Document Aggregate publikuoja Domain Events tik po sėkmingai įvykdytos verslo operacijos.

Jeigu operacija neįvyksta, įvykis neskelbiamas.

Tipinis procesas:

```text
Business Operation
        │
        ▼
Aggregate Updated
        │
        ▼
Domain Event Created
        │
        ▼
EventBus Publish
```

---

## Rule D-198

### Title

Publish After Success

### Requirement

Domain Events SHALL be published only after successful completion of the corresponding business operation.

### Reason

The event must describe an actual business fact.

### Implication

Failed operations SHALL NOT publish success events.

---

## Rule D-199

### Title

Aggregate Consistency

### Requirement

A published Domain Event SHALL represent a consistent Aggregate state.

### Reason

Subscribers rely on valid business data.

### Implication

Events SHALL NOT expose partially updated aggregates.

---

# 11.2 Standard Document Events

Document Domain apibrėžia šiuos pagrindinius įvykius:

- DocumentCreated
- DocumentUpdated
- DocumentFinalized
- DocumentCancelled
- DocumentCopied
- DocumentDeleted

Šie įvykiai aprašo pagrindinius Aggregate gyvavimo faktus.

---

## Rule D-200

### Title

Stable Event Set

### Requirement

Core Domain Events SHALL have stable business meaning.

### Reason

Subscribers depend on consistent event semantics.

### Implication

Existing event meaning SHALL NOT change incompatibly.

---

# 11.3 DocumentCreated

DocumentCreated publikuojamas sukūrus naują Draft dokumentą.

Minimalūs duomenys:

- DocumentId
- DocumentType
- CreatedAt

Dokumentas dar neturi oficialaus numerio.

---

## Rule D-201

### Title

Draft Creation Event

### Requirement

DocumentCreated SHALL be published after successful Draft creation.

### Reason

Other modules may initialize related resources.

### Implication

The event SHALL NOT contain an official DocumentNumber.

---

# 11.4 DocumentUpdated

DocumentUpdated publikuojamas tik tada, kai pasikeičia verslo reikšmę turintys Draft duomenys.

Nedideli UI pakeitimai ar laikini redagavimo veiksmai nėra Domain Events.

---

## Rule D-202

### Title

Business Update Event

### Requirement

DocumentUpdated SHALL represent meaningful business changes only.

### Reason

Avoids excessive event traffic.

### Implication

Pure UI state changes SHALL NOT publish Domain Events.

---

# 11.5 DocumentFinalized

DocumentFinalized yra vienas svarbiausių sistemos įvykių.

Minimalūs duomenys:

- DocumentId
- DocumentNumber
- DocumentType
- FinalizedAt

Nuo šio momento dokumentas tampa oficialiu apskaitos dokumentu.

---

## Rule D-203

### Title

Finalization Event

### Requirement

DocumentFinalized SHALL be published after successful document finalization.

### Reason

Other modules may generate PDF, archive the document or initiate delivery.

### Implication

The event SHALL include the assigned DocumentNumber.

---

# 11.6 DocumentCancelled

DocumentCancelled publikuojamas po sėkmingo atšaukimo.

Minimalūs duomenys:

- DocumentId
- DocumentNumber
- CancelledAt

---

## Rule D-204

### Title

Cancellation Event

### Requirement

DocumentCancelled SHALL be published after successful cancellation.

### Reason

Other modules may update archives and reports.

### Implication

Cancellation subscribers SHALL preserve historical references.

---

# 11.7 DocumentCopied

DocumentCopied publikuojamas sukūrus naują Draft pagal kitą dokumentą.

Minimalūs duomenys:

- SourceDocumentId
- NewDocumentId

---

## Rule D-205

### Title

Copy Event

### Requirement

DocumentCopied SHALL identify both the source and the new Document.

### Reason

Supports traceability.

### Implication

The copied Document remains an independent Aggregate.

---

# 11.8 DocumentDeleted

DocumentDeleted publikuojamas tik tada, kai Aggregate iš tikrųjų pašalinamas.

Jis gali būti naudojamas:

- archyvų sinchronizavimui;
- paieškos indeksų atnaujinimui;
- susijusių failų šalinimui;
- kitoms infrastruktūros užduotims.

---

## Rule D-206

### Title

Deletion Event

### Requirement

DocumentDeleted SHALL be published only after successful aggregate deletion.

### Reason

Subscribers must react only to completed deletion.

### Implication

Deletion events are never published for cancelled documents.

---

# 11.9 Event Consumers

Document Domain nežino, kas naudos jo įvykius.

Galimi prenumeratoriai:

- PDF Module
- Email Module
- Statistics Module
- Audit Module
- Search Index
- Notification Module
- Integration Module

Document Domain nėra priklausomas nuo nė vieno jų.

---

## Rule D-207

### Title

Unknown Subscribers

### Requirement

The Document Domain SHALL remain independent from event subscribers.

### Reason

Preserves loose coupling.

### Implication

The Aggregate publishes events without knowing who consumes them.

---

## Rule D-208

### Title

Multiple Subscribers

### Requirement

A Domain Event MAY have multiple subscribers.

### Reason

Several independent modules may react to the same business fact.

### Implication

Subscribers SHALL remain independent from one another.

---

# 11.10 Event Payload

Domain Event turi perduoti tik tiek informacijos, kiek būtina verslo faktui aprašyti.

Tipiniai laukai:

- EventId
- EventType
- OccurredAt
- AggregateId
- AggregateVersion (jeigu naudojama)
- Business Data

Event neturi perduoti viso Aggregate objekto.

---

## Rule D-209

### Title

Minimal Event Payload

### Requirement

Domain Events SHALL contain only the data required by subscribers.

### Reason

Large payloads increase coupling.

### Implication

Subscribers retrieve additional information through appropriate services when necessary.

---

## Rule D-210

### Title

No Aggregate Transfer

### Requirement

A Domain Event SHALL NOT expose the complete Aggregate instance.

### Reason

Protects Aggregate boundaries.

### Implication

Only relevant identifiers and business values are published.

---

# 11.11 Event Ordering

Vieno Document Aggregate įvykiai turi išlaikyti loginę seką.

Pavyzdys:

```text
DocumentCreated

↓

DocumentUpdated

↓

DocumentFinalized

↓

DocumentCancelled
```

Įvykių tvarka tarp skirtingų Aggregate nėra apibrėžiama šiame dokumente.

---

## Rule D-211

### Title

Aggregate Event Order

### Requirement

Events originating from the same Aggregate SHALL preserve their logical business order.

### Reason

Subscribers must process lifecycle events consistently.

### Implication

DocumentFinalized cannot precede DocumentCreated.

---

# 11.12 Event Versioning

Domain Events gali būti plečiami.

Tačiau:

- esama reikšmė negali būti pakeista;
- laukai gali būti papildyti;
- suderinamumas turi būti išlaikytas.

---

## Rule D-212

### Title

Backward-compatible Events

### Requirement

Domain Event evolution SHALL preserve backward compatibility.

### Reason

Subscribers may depend on existing event contracts.

### Implication

Existing event fields SHALL NOT change incompatible meaning.

---

# 11.13 Event Summary

Domain Events sudaro oficialų Document Domain komunikacijos mechanizmą.

Jie:

- atskiria modulius;
- leidžia plėsti sistemą;
- palaiko EventBus architektūrą;
- nepažeidžia Aggregate ribų.

---

## Rule D-213

### Title

Official Domain Communication

### Requirement

Document Domain SHALL communicate significant business facts through Domain Events.

### Reason

Supports modular and event-driven architecture.

### Implication

Cross-module reactions SHOULD use Domain Events instead of direct Aggregate dependencies.
---

# 12. Repository Contracts

Repository yra vienintelis oficialus Aggregate saugojimo mechanizmas.

Document Domain nežino:

- SQL;
- ORM;
- SQLite;
- PostgreSQL;
- failų sistemos;
- debesijos saugyklos.

Jam svarbu tik Repository kontraktas.

Repository atsako už:

- Aggregate įkėlimą;
- Aggregate išsaugojimą;
- paiešką;
- egzistavimo tikrinimą.

---

## Rule D-214

### Title

Repository Abstraction

### Requirement

The Document Domain SHALL depend only on the DocumentRepository contract.

### Reason

Preserves infrastructure independence.

### Implication

The Aggregate SHALL NOT access databases directly.

---

## Rule D-215

### Title

Aggregate Persistence

### Requirement

Repositories SHALL persist complete Document Aggregates.

### Reason

The Aggregate is the consistency boundary.

### Implication

Partial persistence of owned entities is prohibited.

---

# 12.1 Save

Repository privalo išsaugoti visą Aggregate.

Tai apima:

- Document;
- DocumentLines;
- Totals;
- Snapshots;
- Metadata.

Jeigu Aggregate neegzistuoja — sukuriamas.

Jeigu egzistuoja — atnaujinamas.

---

## Rule D-216

### Title

Aggregate Save

### Requirement

Saving SHALL persist the complete Aggregate as one business unit.

### Reason

Prevents inconsistent stored state.

### Implication

The persistence mechanism SHALL preserve Aggregate consistency.

---

## Rule D-217

### Title

Single Save Entry Point

### Requirement

DocumentRepository SHALL expose one official save operation for Aggregate persistence.

### Reason

Reduces inconsistent persistence paths.

### Implication

Application Services SHALL NOT save owned entities separately.

---

# 12.2 Load

Repository turi gebėti įkelti pilną Aggregate.

Įkėlus Document:

- visi DocumentLines;
- visi Snapshot objektai;
- Totals;
- Metadata

turi būti prieinami kaip viena Aggregate būsena.

---

## Rule D-218

### Title

Complete Aggregate Load

### Requirement

Loading SHALL reconstruct the complete Aggregate.

### Reason

Business operations require a consistent Aggregate.

### Implication

Repositories SHALL NOT return partially loaded Documents.

---

## Rule D-219

### Title

Identity Load

### Requirement

Repository SHALL support loading by internal Document identity.

### Reason

Aggregate identity is the primary lookup mechanism.

### Implication

DocumentNumber is not the primary persistence identity.

---

# 12.3 Find by Number

Sistema turi leisti surasti dokumentą pagal oficialų numerį.

Tai dažniausiai naudojama:

- paieškai;
- spausdinimui;
- pakartotiniam PDF generavimui.

---

## Rule D-220

### Title

Lookup by Official Number

### Requirement

Repository SHALL support lookup by DocumentNumber.

### Reason

Users frequently identify documents by official number.

### Implication

The lookup returns at most one Aggregate.

---

# 12.4 Search

Repository gali teikti paieškos operacijas.

Pavyzdžiai:

- pagal pirkėją;
- pagal datą;
- pagal dokumento tipą;
- pagal būseną;
- pagal numerį;
- pagal laikotarpį.

Repository neapibrėžia UI filtrų.

---

## Rule D-221

### Title

Business Search

### Requirement

Repository MAY expose business-oriented search operations.

### Reason

Supports common application use cases.

### Implication

Search contracts remain independent from UI implementation.

---

## Rule D-222

### Title

Search Criteria

### Requirement

Search operations SHALL use explicit business criteria.

### Reason

Improves readability and future extensibility.

### Implication

Repositories SHOULD avoid long parameter lists.

---

# 12.5 Existence Checks

Kai kurios verslo operacijos reikalauja tik patikrinti egzistavimą.

Pavyzdžiui:

- ar numeris jau naudojamas;
- ar Aggregate egzistuoja;
- ar galima sukurti ryšį.

---

## Rule D-223

### Title

Existence Operations

### Requirement

Repository MAY expose optimized existence checks.

### Reason

Avoids unnecessary Aggregate loading.

### Implication

Existence checks SHALL NOT reconstruct full Aggregates.

---

# 12.6 Delete

Repository palaiko Aggregate pašalinimą.

Tačiau Document Domain leidžia šią operaciją tik pagal Lifecycle taisykles.

Repository pats verslo taisyklių netikrina.

---

## Rule D-224

### Title

Repository Delete

### Requirement

Repository SHALL remove the complete Aggregate when requested by an authorized business operation.

### Reason

Persistence follows domain decisions.

### Implication

Lifecycle validation occurs before Repository deletion.

---

# 12.7 Transactions

Repository privalo užtikrinti, kad Aggregate būtų išsaugotas nuosekliai.

Verslo požiūriu:

- arba visas Aggregate išsaugomas;
- arba neišsaugoma nieko.

---

## Rule D-225

### Title

Atomic Persistence

### Requirement

Repository SHALL preserve Aggregate consistency during persistence.

### Reason

Partial persistence corrupts business data.

### Implication

Persistence failures SHALL leave no partially stored Aggregate state.

---

# 12.8 Concurrency

Kelios darbo vietos ateityje gali redaguoti skirtingus dokumentus vienu metu.

Repository turi palaikyti pasirinktą konkurencijos valdymo strategiją.

Ši specifikacija nenurodo konkretaus mechanizmo.

Galimi pavyzdžiai:

- optimistic locking;
- version field;
- timestamp comparison.

---

## Rule D-226

### Title

Concurrency Strategy

### Requirement

Repository SHALL support a defined concurrency control strategy.

### Reason

Prevents silent overwriting of business data.

### Implication

The implementation may choose the appropriate mechanism.

---

# 12.9 Repository Independence

Repository nėra:

- Service;
- Controller;
- UI komponentas;
- SQL užklausų rinkinys.

Repository yra domeno kontraktas.

---

## Rule D-227

### Title

Repository Responsibility

### Requirement

Repository SHALL manage Aggregate persistence only.

### Reason

Keeps architectural responsibilities separated.

### Implication

Business calculations and validation belong elsewhere.

---

# 12.10 Repository Summary

DocumentRepository užtikrina:

- Aggregate saugojimą;
- Aggregate atkūrimą;
- paiešką;
- egzistavimo tikrinimą;
- švarų atskyrimą nuo infrastruktūros.

Jis sudaro ribą tarp Document Domain ir Persistence sluoksnio.

---

## Rule D-228

### Title

Official Persistence Contract

### Requirement

DocumentRepository SHALL be the official persistence contract of the Document Domain.

### Reason

Provides one stable abstraction for every infrastructure implementation.

### Implication

Future ORM or database changes SHALL NOT require changes to the Document Aggregate.
---

# 13. Domain Exceptions

Domain Exceptions apibrėžia verslo klaidas, kurios gali atsirasti vykdant Document Domain operacijas.

Jos nėra:

- SQL klaidos;
- tinklo klaidos;
- failų sistemos klaidos;
- UI klaidos.

Jos aprašo tik verslo logikos pažeidimus.

Domain Exceptions leidžia Application sluoksniui tinkamai reaguoti į verslo situacijas, neanalizuojant tekstinių klaidų pranešimų.

---

## Rule D-229

### Title

Business Exceptions Only

### Requirement

Domain Exceptions SHALL represent business rule violations only.

### Reason

Separates business logic from technical failures.

### Implication

Infrastructure exceptions SHALL NOT be defined inside the Document Domain.

---

## Rule D-230

### Title

Stable Exception Meaning

### Requirement

Every Domain Exception SHALL have exactly one business meaning.

### Reason

Application Services depend on predictable behaviour.

### Implication

One exception type SHALL NOT represent unrelated business errors.

---

# 13.1 Lifecycle Exceptions

Gyvavimo ciklo klaidos atsiranda bandant atlikti neleistinus būsenų perėjimus.

Pavyzdžiai:

- Draft finalizuojamas du kartus;
- Cancel taikomas Draft dokumentui;
- Finalized dokumentas grąžinamas į Draft.

Galimos išimtys:

- `DocumentAlreadyFinalized`
- `DocumentAlreadyCancelled`
- `InvalidLifecycleTransition`

---

## Rule D-231

### Title

Lifecycle Protection

### Requirement

Invalid lifecycle operations SHALL raise lifecycle-related Domain Exceptions.

### Reason

Protects Aggregate state.

### Implication

Undefined lifecycle transitions are rejected immediately.

---

# 13.2 Validation Exceptions

Kai kurios verslo operacijos negali būti tęsiamos dėl neteisingų dokumento duomenų.

Pavyzdžiai:

- nėra pirkėjo;
- nėra pardavėjo;
- nėra eilučių;
- neteisinga data;
- neteisingas PVM.

Galimos išimtys:

- `DocumentValidationFailed`
- `RequiredFieldMissing`
- `InvalidVatConfiguration`

---

## Rule D-232

### Title

Validation Failure

### Requirement

Business validation failures SHALL raise explicit validation exceptions when the operation cannot continue.

### Reason

The caller must distinguish invalid business data from technical failures.

### Implication

The exception SHOULD include structured validation details.

---

# 13.3 Numbering Exceptions

Numeracijos klaidos atsiranda, kai negalima suteikti oficialaus dokumento numerio.

Pavyzdžiai:

- nėra numeracijos serijos;
- dubliuotas numeris;
- sugadinta numeracijos seka.

Galimos išimtys:

- `MissingNumberSeries`
- `DuplicateDocumentNumber`
- `NumberingConfigurationError`

---

## Rule D-233

### Title

Numbering Failure

### Requirement

Numbering problems SHALL raise numbering-specific Domain Exceptions.

### Reason

Official numbering is a critical business process.

### Implication

The Document remains unfinalized.

---

# 13.4 Aggregate Exceptions

Aggregate klaidos susijusios su pačiu Document objektu.

Pavyzdžiai:

- nerastas dokumentas;
- sugadinta Aggregate būsena;
- pažeistas invariantas.

Galimos išimtys:

- `DocumentNotFound`
- `DocumentInvariantViolation`

---

## Rule D-234

### Title

Aggregate Integrity

### Requirement

Aggregate integrity violations SHALL raise dedicated Domain Exceptions.

### Reason

The Aggregate must never continue in an inconsistent state.

### Implication

The current business operation is aborted.

---

# 13.5 Repository Exceptions

Repository gali pranešti apie verslo lygio saugojimo konfliktus.

Pavyzdžiai:

- konkurencijos konfliktas;
- versijos konfliktas.

Techninės SQL ar tinklo klaidos nepriklauso Domain sluoksniui.

Galimos išimtys:

- `DocumentConcurrencyConflict`
- `DocumentVersionConflict`

---

## Rule D-235

### Title

Business Persistence Conflicts

### Requirement

Business-level persistence conflicts MAY be represented as Domain Exceptions.

### Reason

Concurrency is a business concern from the Aggregate perspective.

### Implication

Pure infrastructure failures remain outside the Domain.

---

# 13.6 Exception Handling

Domain Exceptions nėra skirtos rodyti naudotojui tiesiogiai.

Jos perduodamos į Application sluoksnį.

Application sluoksnis:

- nusprendžia, kaip reaguoti;
- suformuoja naudotojui suprantamą pranešimą;
- gali registruoti auditą;
- gali inicijuoti papildomus veiksmus.

---

## Rule D-236

### Title

Application Translation

### Requirement

Domain Exceptions SHALL be translated into user-facing responses by the Application layer.

### Reason

Business exceptions are not UI messages.

### Implication

Domain code SHALL NOT contain localized user interface text.

---

# 13.7 Exception Summary

Domain Exceptions sudaro oficialų Document Domain klaidų modelį.

Jos:

- apsaugo Aggregate;
- aiškiai apibrėžia verslo klaidas;
- atskiria verslo ir technines problemas;
- leidžia Application sluoksniui vienodai apdoroti klaidas.

---

## Rule D-237

### Title

Official Business Error Model

### Requirement

Domain Exceptions SHALL be the official mechanism for reporting business rule violations within the Document Domain.

### Reason

Provides consistent error handling across the application.

### Implication

Business logic SHALL NOT rely on generic exceptions for expected domain failures.
---

# 14. Integration Boundaries

Document Domain nėra izoliuota sistema.

Ji bendradarbiauja su kitais moduliais.

Tačiau bendradarbiavimas vyksta tik per aiškiai apibrėžtas ribas.

Document Domain:

- nenaudoja kitų Aggregate vidinės būsenos;
- nekeičia kitų Aggregate duomenų;
- nepažeidžia kitų Domain taisyklių.

Kiekvienas Domain lieka savo verslo taisyklių savininku.

---

## Rule D-238

### Title

Bounded Context Independence

### Requirement

The Document Domain SHALL remain independent from the internal implementation of other Domains.

### Reason

Preserves modular architecture.

### Implication

Document accesses other Domains only through their public contracts.

---

## Rule D-239

### Title

No Cross-Aggregate Modification

### Requirement

Document operations SHALL NOT directly modify Aggregates owned by other Domains.

### Reason

Each Aggregate protects its own invariants.

### Implication

Cross-domain updates are coordinated by the Application layer.

---

# 14.1 Company Domain

Company Domain saugo įmonės pagrindinius duomenis.

Document Domain naudoja Company kaip pradinį pardavėjo informacijos šaltinį.

Tipiniai naudojami duomenys:

- pavadinimas;
- kodas;
- PVM kodas;
- adresas;
- banko sąskaitos;
- kontaktai;
- logotipas;
- numatytieji nustatymai.

Finalizavimo metu sukuriamas SellerSnapshot.

Po to Company pakeitimai istorinių dokumentų nekeičia.

---

## Rule D-240

### Title

Company Snapshot

### Requirement

Document SHALL copy required seller data from Company during finalization.

### Reason

Historical documents must remain reproducible.

### Implication

Later Company changes do not modify finalized Documents.

---

# 14.2 Customer Domain

Customer Domain valdo klientų registrą.

Document gali naudoti Customer kaip:

- pirkėjo šaltinį;
- paieškos šaltinį;
- automatinio užpildymo šaltinį.

Customer nėra istorinių dokumentų saugykla.

Tam naudojamas BuyerSnapshot.

---

## Rule D-241

### Title

Customer Snapshot

### Requirement

Finalized Documents SHALL preserve buyer information independently from Customer master data.

### Reason

Customer records may change over time.

### Implication

Historical Documents remain unchanged.

---

# 14.3 Product Domain

Product Domain saugo prekių ir paslaugų katalogą.

Document gali naudoti Product informaciją kuriant Draft.

Pavyzdžiai:

- pavadinimas;
- kodas;
- vienetas;
- numatytoji kaina;
- PVM tarifas.

Po pasirinkimo informacija tampa DocumentLine dalimi.

---

## Rule D-242

### Title

Product Copy

### Requirement

DocumentLines SHALL copy required Product data during insertion into a Document.

### Reason

Historical documents must not depend on changing Product data.

### Implication

Editing Product master data does not alter finalized Documents.

---

# 14.4 Numbering Module

Document Domain bendradarbiauja su numeracijos mechanizmu.

Document pats numerių negeneruoja.

Jis tik paprašo:

DocumentNumberingService

suteikti oficialų numerį.

---

## Rule D-243

### Title

External Number Provider

### Requirement

Document SHALL obtain official numbers only through DocumentNumberingService.

### Reason

Keeps numbering centralized.

### Implication

Number generation is not implemented inside the Aggregate.

---

# 14.5 PDF Module

PDF Module nėra Document Domain dalis.

Jo atsakomybė:

- PDF generavimas;
- šablonų taikymas;
- failų kūrimas.

Document perduoda tik verslo duomenis.

---

## Rule D-244

### Title

PDF Independence

### Requirement

Document Domain SHALL NOT generate PDF files.

### Reason

PDF generation is infrastructure functionality.

### Implication

PDF Module consumes finalized Document data.

---

# 14.6 Email Module

Email Module atsako už:

- el. laiško sudarymą;
- PDF pridėjimą;
- siuntimą;
- siuntimo istoriją.

Document Domain nesiunčia laiškų.

---

## Rule D-245

### Title

Email Independence

### Requirement

Document Domain SHALL NOT send emails.

### Reason

Email delivery is outside business document responsibilities.

### Implication

Email Module reacts to Domain Events.

---

# 14.7 Storage Module

Storage Module atsako už:

- PDF archyvą;
- eksportuotus failus;
- kitus sugeneruotus dokumentus.

Document Domain nežino failų kelių.

---

## Rule D-246

### Title

Storage Independence

### Requirement

Document Domain SHALL remain independent from physical file storage.

### Reason

Storage technology may change.

### Implication

The Aggregate stores no filesystem-specific information.

---

# 14.8 Reporting Module

Reporting Module naudoja finalizuotus dokumentus.

Jis:

- skaičiuoja statistiką;
- kuria ataskaitas;
- analizuoja duomenis.

Reporting nekeičia Document.

---

## Rule D-247

### Title

Read-only Reporting

### Requirement

Reporting SHALL treat finalized Documents as read-only business data.

### Reason

Reports analyze rather than modify accounting history.

### Implication

Reporting modules never update Document Aggregates.

---

# 14.9 EventBus

EventBus yra oficialus komunikacijos mechanizmas tarp modulių.

Document Domain:

- publikuoja Domain Events;
- nepriklauso nuo prenumeratorių.

EventBus nėra Document Domain dalis.

---

## Rule D-248

### Title

EventBus Communication

### Requirement

Cross-module business notifications SHOULD use EventBus.

### Reason

Supports loose coupling.

### Implication

Document Domain remains unaware of subscribers.

---

# 14.10 Future Integrations

Ateityje gali būti prijungti papildomi moduliai.

Pavyzdžiai:

- REST API;
- eBay integracija;
- internetinė parduotuvė;
- apskaitos eksportas;
- banko integracija;
- EDI;
- valstybinių sistemų integracijos.

Document Domain dėl to neturi keistis.

---

## Rule D-249

### Title

Stable Domain Core

### Requirement

New integrations SHALL extend the system without changing existing Document business rules.

### Reason

The Domain model should remain stable.

### Implication

Integrations are implemented outside the Aggregate.

---

# 14.11 Dependency Diagram

```text
                 Company
                    │
                    ▼
Customer ─────► Document ◄───── Product
                    │
                    ▼
          Document Domain Events
                    │
               EventBus
                    │
      ┌────────┬────────┬─────────┐
      ▼        ▼        ▼         ▼
    PDF      Email   Reporting  Storage
```

Document yra centrinis verslo objektas.

Tačiau jis nepriklauso nė vienam infrastruktūros moduliui.

---

## Rule D-250

### Title

Dependency Direction

### Requirement

Dependencies SHALL point toward the Document Domain rather than from the Document Domain into infrastructure.

### Reason

Preserves Clean Architecture principles.

### Implication

Infrastructure depends on the Domain, not vice versa.

---

# 14.12 Integration Summary

Document Domain:

- naudoja Company;
- naudoja Customer;
- naudoja Product;
- naudoja NumberingService;
- publikuoja Domain Events;
- nesiunčia el. laiškų;
- negeneruoja PDF;
- nerašo failų;
- nevykdo SQL.

Taip išlaikoma aiški Domain, Application ir Infrastructure sluoksnių atsakomybė.

---

## Rule D-251

### Title

Official Integration Boundary

### Requirement

These integration boundaries SHALL define every supported interaction between the Document Domain and other modules.

### Reason

Protects Domain integrity while allowing system growth.

### Implication

New integrations SHALL conform to these boundaries.
---

# 15. Glossary

Šiame skyriuje apibrėžiami pagrindiniai terminai, naudojami Document Domain.

Terminai šiame dokumente turi normatyvinę reikšmę.

Jeigu kituose projekto dokumentuose naudojama ta pati sąvoka, ji turi būti suprantama taip, kaip apibrėžta šiame žodyne.

---

## Aggregate

Verslo objektas, kuris sudaro vieną nuoseklumo ribą (Consistency Boundary).

Document Aggregate sudaro:

- Document
- DocumentLines
- Totals
- Snapshots
- Metadata

---

## Aggregate Root

Pagrindinis Aggregate objektas.

Tik Aggregate Root leidžia keisti Aggregate būseną.

Document Aggregate Root yra Document.

---

## Application Layer

Sluoksnis, koordinuojantis verslo operacijas.

Jis:

- kviečia Domain;
- valdo Repository;
- publikuoja Domain Events;
- koordinuoja kitus modulius.

Application Layer neapibrėžia verslo taisyklių.

---

## Buyer Snapshot

Pirkėjo duomenų kopija, išsaugoma finalizuojant dokumentą.

Ji užtikrina istorinių dokumentų nekintamumą.

---

## Cancelled Document

Dokumentas, kuris oficialiai panaikintas.

Jo apskaitinis turinys išlieka nepakitęs.

---

## Document

Pagrindinis Document Domain Aggregate Root.

Jis reprezentuoja vieną verslo dokumentą.

---

## DocumentLine

Viena dokumento eilutė.

Ji negali egzistuoti be Document Aggregate.

---

## Document Number

Oficialus verslo numeris.

Skiriamas tik finalizavimo metu.

Jis nėra Aggregate identifikatorius.

---

## Document Type

Dokumento verslo tipas.

Pavyzdžiui:

- Invoice
- Proforma
- Commercial Offer
- eBay Invoice

---

## Domain

Verslo modelio sluoksnis.

Jame aprašomos:

- verslo taisyklės;
- Aggregate;
- Value Objects;
- Domain Services;
- Domain Events.

---

## Domain Event

Įvykęs verslo faktas.

Pavyzdžiui:

- DocumentCreated
- DocumentFinalized
- DocumentCancelled

---

## Draft

Dar neredaguotas arba dar nepatvirtintas dokumentas.

Draft gali būti keičiamas.

---

## EventBus

Komponentas, perduodantis Domain Events tarp modulių.

EventBus nėra Document Domain dalis.

---

## Finalization

Verslo operacija, kurios metu Draft tampa oficialiu apskaitos dokumentu.

Jos metu:

- suteikiamas numeris;
- sukuriami Snapshot;
- užfiksuojama istorinė būsena.

---

## Finalized Document

Oficialiai užbaigtas dokumentas.

Jo apskaitinis turinys tampa nekintamas.

---

## Lifecycle

Dokumento būsenų modelis.

Standartinės būsenos:

- Draft
- Finalized
- Cancelled

---

## Metadata

Techniniai Aggregate duomenys.

Pavyzdžiai:

- CreatedAt
- UpdatedAt
- FinalizedAt

---

## Presentation Snapshot

Spausdinimo nustatymų kopija.

Ji leidžia ateityje atkurti identišką dokumento išvaizdą.

---

## Repository

Domain kontraktas Aggregate saugojimui ir atkūrimui.

Repository nėra SQL implementacija.

---

## Seller Snapshot

Pardavėjo duomenų kopija.

Ji išsaugoma finalizavimo metu.

---

## Snapshot

Istorinė verslo duomenų kopija.

Snapshot apsaugo istorinius dokumentus nuo vėlesnių pagrindinių duomenų pakeitimų.

---

## Value Object

Objektas, neturintis savo tapatybės.

Jis apibrėžiamas tik savo verte.

Pavyzdžiai:

- Money
- Quantity
- Percentage
- VatRate

---

## Rule D-252

### Title

Canonical Terminology

### Requirement

The terminology defined in this Glossary SHALL be considered authoritative throughout the PTH Fausta project documentation.

### Reason

Consistent terminology reduces ambiguity and improves communication.

### Implication

New documentation SHOULD reuse these definitions whenever applicable.
---

# 16. Appendix

Šis skyrius pateikia papildomą informaciją apie Document Domain specifikacijos taikymą, susijusius architektūros dokumentus ir šio dokumento gyvavimo taisykles.

---

# 16.1 Scope of this Specification

Ši specifikacija apibrėžia tik Document Domain.

Ji apima:

- Domain Model;
- Aggregate;
- Entities;
- Value Objects;
- Enumerations;
- Domain Services;
- Lifecycle;
- Business Rules;
- Domain Events;
- Repository Contracts;
- Domain Exceptions;
- Integration Boundaries.

Ji neapibrėžia:

- vartotojo sąsajos;
- SQL modelio;
- ORM implementacijos;
- PDF generavimo;
- el. pašto siuntimo;
- failų saugojimo;
- infrastruktūros technologijų.

---

## Rule D-253

### Title

Domain Specification Scope

### Requirement

This specification SHALL define only the business behaviour of the Document Domain.

### Reason

Maintains a clear separation between business rules and implementation details.

### Implication

Technical implementation documents SHALL extend, but never redefine, this specification.

---

# 16.2 Related Documents

Document Domain yra viena bendros architektūros dalis.

Su juo susiję dokumentai apima (bet jais neapsiriboja):

- Documentation Standard
- AI Team Guidelines
- Application Layer Specification
- Infrastructure Specification
- Database Model
- EventBus Specification
- Navigation Specification
- UI Architecture
- Project Coding Standards

Šie dokumentai papildo vienas kitą.

Esant prieštaravimui, Domain taisyklės turi pirmenybę prieš infrastruktūros sprendimus.

---

## Rule D-254

### Title

Architecture Consistency

### Requirement

Related architecture documents SHALL remain consistent with this Domain specification.

### Reason

The Domain model is the foundation of the application architecture.

### Implication

Implementation documents SHALL adapt to Domain rules, not the opposite.

---

# 16.3 Change Management

Document Domain laikomas ilgalaike architektūrine specifikacija.

Pakeitimai turi būti atliekami tik tada, kai:

- pasikeičia verslo reikalavimai;
- randama architektūrinė klaida;
- būtina išplėsti Domain modelį.

Redakciniai pataisymai gali būti atliekami laisvai, jei jie nekeičia verslo prasmės.

---

## Rule D-255

### Title

Controlled Evolution

### Requirement

Business changes to this specification SHALL be intentional, documented and reviewed.

### Reason

Domain stability reduces long-term maintenance costs.

### Implication

Frequent behavioural changes SHOULD be avoided.

---

# 16.4 Implementation Guidance

Ši specifikacija sąmoningai neapibrėžia konkrečių technologijų.

Galimi įgyvendinimai:

- Python;
- SQLAlchemy;
- SQLite;
- PostgreSQL;
- REST API;
- Desktop Application.

Visi jie turi įgyvendinti šiame dokumente aprašytą verslo elgseną.

---

## Rule D-256

### Title

Technology Independence

### Requirement

The business rules defined in this specification SHALL remain independent from implementation technology.

### Reason

Allows future replacement of infrastructure without changing the Domain.

### Implication

Technology choices SHALL NOT alter business behaviour.

---

# 16.5 Architectural Principles

Document Domain vadovaujasi šiomis architektūrinėmis nuostatomis:

- Business First
- Clean Architecture
- Domain-Driven Design
- Aggregate Consistency
- Immutable Accounting History
- Explicit Business Rules
- Event-Driven Communication
- Infrastructure Independence

Šie principai buvo taikomi rengiant visą specifikaciją.

---

## Rule D-257

### Title

Architectural Principles

### Requirement

All future extensions of the Document Domain SHALL preserve these architectural principles.

### Reason

Ensures long-term consistency of the system.

### Implication

New functionality SHOULD integrate into the existing model rather than bypass it.

---

# 16.6 Conformance

Document Domain laikomas įgyvendintu tik tada, kai:

- laikomasi visų privalomų (SHALL) taisyklių;
- išlaikomi Aggregate invariantai;
- Repository atitinka kontraktą;
- Domain Events atitinka specifikaciją;
- verslo taisyklės įgyvendintos pilnai.

---

## Rule D-258

### Title

Implementation Conformance

### Requirement

An implementation SHALL conform to all mandatory requirements defined in this specification.

### Reason

Ensures predictable and interoperable behaviour.

### Implication

Partial implementations SHALL explicitly document unsupported features.

---

# 16.7 Final Statement

This document defines the official business specification of the Document Domain for the PTH Fausta project.

It serves as the authoritative reference for:

- software architecture;
- implementation;
- testing;
- documentation;
- future system evolution.

All architectural and implementation decisions concerning the Document Domain SHALL remain consistent with this specification.

---

## Rule D-259

### Title

Authoritative Specification

### Requirement

This document SHALL be considered the authoritative specification of the Document Domain.

### Reason

Provides a single source of truth for business behaviour.

### Implication

Any future implementation SHALL be validated against this specification.
