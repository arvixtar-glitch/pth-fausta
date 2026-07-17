# PTH Fausta – Darbų planas

## 1 etapas – Projekto pagrindas ✅

* [x] Sukurti projekto karkasą.
* [x] Sutvarkyti projekto struktūrą.
* [x] Sukurti Core architektūrą.
* [x] Sukurti projektų kelių (Paths) valdymo modulį.
* [x] Sukurti žurnalavimo (Logging) sistemą.
* [x] Sukurti nustatymų (Settings) valdymo sistemą.
* [x] Sukurti konfigūracijos (Config) modulį.
* [x] Sukurti versijos (Version) modulį.
* [x] Sukurti programos gyvavimo ciklo (Application) modulį.
* [x] Sukurti pagrindinį programos paleidimo tašką (Main).
* [x] Sukurti ir patvirtinti Core dokumentaciją.
* [x] Atlikti Core architektūros auditą.
* [x] Sukurti Core vienetinius testus.

---

## 2 etapas – MVC pagrindas ⏳

* [x] Sukurti MVC architektūros pagrindą.
* [x] Sukurti bazines Controller klases.
* [x] Sukurti bazinę `BaseService` klasę.
* [x] Sukurti bazines Repository klases.
* [x] Sukurti bazines Model klases.
* [x] Sukurti View infrastruktūrą.
* [x] Sukurti EventBus.
* [x] Sukurti AppController.
* [x] Sukurti NavigationService.
* [x] Sukurti ServiceContainer.
* [x] Sukurti AppState.
* [x] Composition Root planas parengtas (dokumentavimas).
* [x] Sukurti `src/app/bootstrap.py` – Composition Root įgyvendinimas.

---

## 3 etapas – Duomenų sluoksnis

* [ ] Sukurti SQLAlchemy infrastruktūrą.
* [ ] Sukurti duomenų bazės modelius.
* [ ] Sukurti migracijų sistemą.

---

## 4 etapas – Business Layer Foundation 🔄

* [x] Task 4.1 – sukurti bazinę `BaseService` klasę.
* [x] Task 4.2 – sukurti bazinę `BaseRepository` klasę.
* [x] Task 4.3 – formalizuoti architektūros priklausomybių taisykles ir testus.

---

## 5 etapas – Persistence Foundation 🔄

* [x] Task 5.1 – sukurti persistence konfigūracijos pagrindą.
* [x] Task 5.2 – sukurti SQLAlchemy engine ir sesijų fabriką.
* [ ] Task 5.3 – sukurti ORM Base ir metadata pagrindą.
* [ ] Sukurti ORM modelius.
* [ ] Sukurti Alembic migracijų infrastruktūrą.

---

## 6 etapas – Verslo moduliai

* [ ] Klientai.
* [ ] Pardavėjas.
* [ ] Sąskaitos.
* [ ] PDF generavimas.
* [ ] QR kodų generavimas.
* [ ] El. pašto modulis.
* [ ] Statistika.
* [ ] Atsarginių kopijų modulis.

---

## Pastabos

* Kiekvienas etapas laikomas užbaigtu tik po:

  * kodo parašymo;
  * testų;
  * kodo peržiūros;
  * architektūros audito;
  * dokumentacijos atnaujinimo.
