# PTH Fausta – Duomenų bazės architektūra

**Dokumentas:** DATABASE.md  
**Versija:** 1.0  
**Būsena:** Patvirtinta kryptis  
**Data:** 2026-07-17

## Paskirtis

Šis dokumentas apibrėžia patvirtintą persistence technologijų ir būsimos
verslo duomenų schemos kryptį. Task 5.1 įgyvendina tik konfigūracijos pagrindą:
DB engine, sesijos, ORM lentelės, migracijos ir tikras DB failas dar nekuriami.

## Technologinė kryptis

Numatyta naudoti SQLite, SQLAlchemy 2.x ir Alembic. Verslo sluoksniai neturi
tiesiogiai priklausyti nuo SQLite ar vykdyti `sqlite3` užklausų. Repository
sluoksnis ateityje naudosis atskirai sukurta persistence infrastruktūra.

Numatytoji failų struktūra:

```text
data/
├── pth_fausta.db
├── documents/
├── exports/
└── backups/
```

`DatabaseConfig` aprašo šiuos kelius, tačiau katalogus sukuria tik aiškiai
iškvietus `ensure_directories()`. Šis metodas DB failo nekuria.

## Pagrindiniai schemos blokai

Patvirtintos būsimos lentelės:

```text
companies
company_bank_accounts
clients
products
documents
document_items
document_status_history
document_files
numbering_sequences
payments
payment_allocations
email_messages
```

Vėliau gali būti pridėtos `ebay_document_details` ir `audit_log` lentelės.

### Įmonės banko sąskaitos

`company_bank_accounts` numatyti laukai: `id`, `company_id`, `bank_name`,
`swift_bic`, `iban`, `account_holder`, `currency`, `is_default`, `status`,
`created_at`, `updated_at`. Gavėjo pavadinimui naudojamas `account_holder`.

### Klientai

`clients` numatyti laukai: `id`, `client_type`, `name`, `company_code`,
`vat_code`, `address`, `city`, `postal_code`, `country_code`, `phone`, `email`,
`notes`, `status`, `search_text`, `created_at`, `updated_at`.

`search_text` generuojamas automatiškai iš pavadinimo, įmonės ir PVM kodų,
telefono, el. pašto bei adreso. Pradiniame etape naudojamas normalizuotas
tekstas; SQLite FTS5 kol kas nėra privaloma technologija.

### Prekės ir paslaugos

`products` numatyti laukai: `id`, `code`, `name`, `description`, `unit`,
`default_quantity`, `unit_price`, `currency`, `vat_rate`, `status`,
`created_at`, `updated_at`.

Istorinė dokumento eilutė saugo produkto duomenų kopiją, todėl vėlesni produkto
pavadinimo ar kainos pakeitimai nekeičia užbaigto dokumento.

### Dokumentai

`documents` apima identifikaciją ir numeravimą, įmonės, kliento bei banko
sąskaitos nuorodas, datas, valiutą, sumas, būseną, paiešką ir pardavėjo bei
pirkėjo duomenų kopijas. Patvirtinti svarbiausi laukai:

```text
id, document_type, document_number, series, sequence_number
company_id, client_id, bank_account_id
external_source, external_order_number
issue_date, due_date, currency
subtotal, discount_total, tax_total, grand_total, paid_total, balance_due
status, language, notes, payment_terms, search_text
seller_name, seller_code, seller_vat_code, seller_address
buyer_name, buyer_code, buyer_vat_code, buyer_address, buyer_email, buyer_phone
created_at, updated_at, finalized_at, cancelled_at
```

SQL raktažodis `order` nenaudojamas kaip lauko pavadinimas. Išorinei sistemai
ir užsakymui naudojami `external_source` bei `external_order_number`.
`search_text` generuojamas iš dokumento ir jo eilučių paieškai svarbių reikšmių.

### eBay duomenys

`ebay_fee` yra reikalingas verslo duomuo. Ilgalaikėje struktūroje eBay specifika
numatoma atskiroje `ebay_document_details` lentelėje su `document_id`,
`ebay_order_number`, `ebay_fee`, `ebay_transaction_id` ir
`ebay_buyer_username`. Task 5.1 šios lentelės nekuria.

### Dokumentų eilutės

`document_items` numatyti laukai: `id`, `document_id`, `position`, `product_id`,
`item_code`, `description`, `quantity`, `unit`, `unit_price`,
`discount_percent`, `discount_amount`, `tax_rate`, `tax_amount`,
`line_subtotal`, `line_total`, `created_at`, `updated_at`.

`product_id` gali būti `NULL`, nes eilutė gali būti įrašyta rankiniu būdu.

### Mokėjimai

Mokėjimams numatytos `payments` ir `payment_allocations` lentelės:

```text
Payment ──< PaymentAllocation >── Document
```

Struktūra turi palaikyti dalinius mokėjimus, avansus, vieno mokėjimo
paskirstymą keliems dokumentams ir dokumento apmokėjimą keliais mokėjimais.

## Duomenų tipų ir gyvavimo ciklo principai

* Pinigai Python kode skaičiuojami su `Decimal`, DB lygyje numatomas `NUMERIC`;
  `float` pinigų skaičiavimams draudžiamas.
* Verslo datos saugomos kaip `DATE`.
* `created_at`, `updated_at`, `finalized_at` ir kiti techniniai laiko žymėjimai
  saugomi kaip UTC datetime.
* Finansiniai dokumentai fiziškai netrinami; naudojami `status` ir
  `cancelled_at`.
* Klientams ir produktams numatoma archyvavimo būsena.

## Įgyvendinimo etapai

SQLAlchemy engine, sesijų fabrikas, ORM modeliai ir Alembic migracijos bus
kuriami atskirose vėlesnėse 5 etapo užduotyse. Jų negalima perkelti į verslo,
Controller ar UI sluoksnius.

## Susiję dokumentai

* `ARCHITECTURE.md` – bendros sluoksnių ir priklausomybių taisyklės.
* `TODO.md` – persistence etapo darbų eiga.
