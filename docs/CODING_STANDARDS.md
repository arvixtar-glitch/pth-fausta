# CODING_STANDARDS.md

**Projektas:** PTH Fausta
**Dokumentas:** CODING_STANDARDS.md
**Versija:** 1.0
**Būsena:** Aktyvus
**Autorius:** Produkto savininkas ir DI komanda
**Sukūrimo data:** 2026-07-14
**Paskutinis atnaujinimas:** 2026-07-14

---

# PTH Fausta – Programavimo standartai

---

# 1. Paskirtis

Šis dokumentas apibrėžia Python programavimo standartus, kurių privaloma laikytis kuriant projektą **PTH Fausta**.

Tikslai:

* užtikrinti vieningą programavimo stilių;
* pagerinti kodo skaitomumą;
* palengvinti priežiūrą;
* sumažinti klaidų tikimybę;
* užtikrinti ilgalaikį projekto vystymą.

---

# 2. Bendrieji principai

Projektas kuriamas vadovaujantis principais:

* aiškumas svarbiau už trumpumą;
* paprastumas svarbiau už gudrumą;
* skaitomumas svarbiau už optimizavimą;
* architektūra svarbiau už pavienį funkcionalumą;
* kiekviena klasė turi vieną aiškią atsakomybę (Single Responsibility Principle).

---

# 3. Python standartai

Projektas laikosi:

* PEP 8
* PEP 257
* Type Hints

Visas naujai kuriamas kodas turi atitikti šiuos standartus.

---

# 4. Failų pavadinimai

Naudojami tik mažosios raidės.

Pavyzdžiai:

```text
invoice_service.py
customer_model.py
pdf_generator.py
database_manager.py
```

Nenaudojami:

```text
InvoiceService.py
InvoiceSERVICE.py
```

---

# 5. Klasių pavadinimai

Naudojamas PascalCase.

Pavyzdžiai:

```python
Invoice
InvoiceService
CustomerRepository
PdfGenerator
```

---

# 6. Funkcijų ir metodų pavadinimai

Naudojamas snake_case.

Pavyzdžiai:

```python
create_invoice()
load_customer()
save_pdf()
calculate_total()
```

---

# 7. Kintamųjų pavadinimai

Naudojami aiškūs pavadinimai.

Leidžiama:

```python
customer
invoice
invoice_total
payment_date
```

Vengiama:

```python
a
b
tmp
x1
```

Išimtis – trumpi ciklo kintamieji.

---

# 8. Konstantos

Konstantos rašomos didžiosiomis raidėmis.

Pavyzdys:

```python
DEFAULT_LANGUAGE
MAX_ITEMS
PDF_MARGIN
```

---

# 9. Type Hints

Privalomi visuose naujuose metoduose.

Pavyzdys:

```python
def calculate_total(items: list[InvoiceItem]) -> Decimal:
```

---

# 10. Docstring

Visos viešos klasės ir vieši metodai turi turėti docstring.

Naudojamas Google stilius.

Pavyzdys:

```python
def save_invoice(invoice: Invoice) -> None:
    """
    Išsaugo sąskaitą duomenų bazėje.

    Args:
        invoice: Sąskaitos objektas.
    """
```

---

# 11. Komentarai

Komentarai naudojami tik tada, kai negalima aiškiai išreikšti minties pačiu kodu.

Nekomentuojamas akivaizdus kodas.

Blogai:

```python
# Padidiname i
i += 1
```

Gerai:

```python
# eBay numeracija prasideda nuo 100000.
```

---

# 12. Importai

Importai grupuojami tokia tvarka:

1. Python standartinė biblioteka.
2. Trečiųjų šalių bibliotekos.
3. Projekto moduliai.

Importų grupės atskiriamos tuščia eilute.

---

# 13. Klaidų valdymas

Nenaudojamas:

```python
except:
```

Naudojamas:

```python
except ValueError:
```

arba

```python
except Exception as exc:
```

Klaidos neturi būti nutylimos.

---

# 14. Logging

Projektas naudoja Python `logging`.

`print()` naudojamas tik laikinam derinimui.

Galutinėje programoje diagnostinė informacija registruojama naudojant `logging`.

---

# 15. Magic Numbers

Programoje nenaudojami „magiški skaičiai“.

Vietoj:

```python
if count > 17:
```

naudojama:

```python
MAX_CUSTOMERS = 17

if count > MAX_CUSTOMERS:
```

---

# 16. Funkcijų dydis

Funkcijos turi būti trumpos.

Jeigu metodas tampa sunkiai suprantamas, jis skaidomas į mažesnius metodus.

---

# 17. Klasių atsakomybė

Kiekviena klasė turi vieną aiškią paskirtį.

Jeigu klasė pradeda atlikti kelias skirtingas funkcijas, ji skaidoma.

---

# 18. Testuojamumas

Kodas turi būti kuriamas taip, kad jį būtų galima testuoti.

Verslo logika neturi būti priklausoma nuo grafinės sąsajos.

---

# 19. Refaktoringas

Refaktoringas negali keisti programos veikimo.

Jo tikslas:

* pagerinti skaitomumą;
* sumažinti sudėtingumą;
* pagerinti architektūrą.

---

# 20. Codeium darbo taisyklės

Programuotojas (Codeium):

* nekeičia architektūros;
* nekeičia katalogų struktūros;
* nekeičia viešų API be užduoties;
* nevykdo didelių refaktoringų savo iniciatyva;
* kiekvieną užduotį įgyvendina tik pagal pateiktą techninę specifikaciją.

---

# 21. Kokybės principas

Prieš laikant darbą užbaigtu turi būti užtikrinta:

* kodas veikia;
* nėra akivaizdžių įspėjimų;
* laikomasi šio dokumento reikalavimų;
* nepažeidžiama projekto architektūra.

---

# 22. Versijų istorija

| Versija | Data       | Pakeitimai                                           |
| ------- | ---------- | ---------------------------------------------------- |
| 1.0     | 2026-07-14 | Sukurtas pradinis programavimo standartų dokumentas. |
