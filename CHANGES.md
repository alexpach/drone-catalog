# Changes

## 2026-10-13 — Remove `archive/` from the repo and its history

- Rewrote both commits to drop `archive/`. That folder held the legacy
  catalog's product images, screenshots and scripts, including a hard-coded
  logo.dev key. The local pack shrank from about 58 MB to 36 KB.
- `scripts/enrich_companies.py` now skips the legacy manifest lookup when the
  archive is absent. Every current row already has the fields it backfilled.
- Test: `python3 scripts/enrich_companies.py` followed by
  `python3 scripts/import_ddp_vendors.py` leaves `companies.csv` unchanged, and
  `git log --all -- archive` is empty.

## 2026-10-13 — Company register viewer

- Added `index.html`, which loads `companies.csv` and shows every column. You
  can sort by clicking a column title (ascending, descending, original order),
  filter per column (dropdowns for columns with few values, text for the
  rest), and search across all columns. Blank and `unknown` values sort last.
- Test: run `python3 -m http.server` in the repo root and open
  <http://localhost:8000>. The browser check showed 240 rows, status =
  acquired gives 8, notes contains "DDP:" gives 65, and year and name sorting
  both work.

## 2026-10-13 — Import Drone Dominance Program vendors (Phase 1 and Phase 2)

- Added `scripts/import_ddp_vendors.py`, which merges the vendor rosters from
  [dronedominance.mil/vendors.html](https://dronedominance.mil/vendors.html)
  (data in `js/vendor-data.js`) into `companies.csv`.
- Covers the 26 Phase 1 (Gauntlet I) vendors, the 49 Phase 2 Qualifier
  invitees, and the 8 Phase 2 lethality vendors. Team entries are split into
  member companies.
- 40 new organizations were added; 25 existing rows got a `DDP:` participation
  note. Six of those also got domains or parents from the DDP vendor directory
  (Ascent → Robinson Helicopter, Halo Aeronautics → By Light). The register
  now has 240 records.
- Test: run `python3 scripts/import_ddp_vendors.py` twice. The second run
  reports `Added 0, updated 0`. Running `python3 scripts/enrich_companies.py`
  afterwards leaves `companies.csv` byte-identical.
