# Drone Company Index

A research index of organizations that have operated in the drone industry at
any time from 2016 onward. The list includes current, acquired, and closed
organizations, and labels non-business entities separately.

## Data

`companies.csv` is the working company register. Its `industry`,
`country_of_origin`, and `status` fields provide the requested tags. Status is
one of `live`, `gone`, `acquired`, or `unknown`. `entity_type` and
`parent_or_acquirer` distinguish parent companies, business units, and
non-business projects. `period_status` identifies legacy candidates whose
operation since 2016 still needs verification. Domains and evidence links point
to official sites where available; unknown domains and countries are marked
explicitly instead of guessed.

This is a growing research index, not a claim of exhaustive global coverage.
Drone Industry Insights' 2026 market map is a useful breadth benchmark: it
lists 1,413 organizations in 70 countries across hardware, software, and
services, while excluding purely military manufacturers. Its public overview
does not expose the full roster, so the index is being assembled from public
directories and checked against company sources. The map says about 300
organizations were removed since 2022 because of acquisitions, dissolution, or
market exits; this is why historic status matters in the register.

As of 2026-10-13, the register contains 240 unique records. It includes 137
military, munitions, or counter-UAS tagged records; 41 carried-over legacy
candidates still need confirmation that they operated during or after 2016.
Forty-four domains and 33 countries of origin are explicitly unresolved. These
numbers describe the current working register, not the total size of the global
market.

`index.html` is a browser viewer for `companies.csv` with per-column sorting
and filtering. To use it locally, run `python3 -m http.server` in the repo root
and open <http://localhost:8000>. Opening the file directly will not load the CSV.

`scripts/import_ddp_vendors.py` merges the U.S. Drone Dominance Program Phase 1
and Phase 2 rosters from <https://dronedominance.mil/vendors.html>. Rows from
it carry a `DDP:` note describing each company's participation.

Each record should be checked for identity, time period, domain ownership,
business status, acquisition/closure, and whether the organization is a
business, business unit, public body, nonprofit, or research project. Research
sources include [Drone Industry Insights' 2026 map](https://droneii.com/drone-market-map-2026),
[Vertus' delivery-operator tracker](https://vertus.aero/intelligence?from=article-promo),
and [Vertus' company directory](https://vertus.aero/intelligence/companies).
Military entries are expanded from the [U.S. Drone Dominance Program vendor
announcement](https://www.war.gov/News/Releases/Release/Article/4396462/war-department-announces-vendors-invited-to-compete-in-phase-i-of-the-drone-dom/)
and the [EU-Ukraine Drone Alliance roster](https://defence-industry-space.ec.europa.eu/commission-launches-eu-ukraine-drone-alliance-boost-drone-and-counter-drone-technology-2026-07-17_en).
Military and counter-UAS entries also use [Drone & Defense's military drone
directory](https://droneanddefense.com/unmanned-systems/drones/military-drone-companies),
[Drone Intelligence's counter-UAS map](https://droneintelligence.ai/counter-uas-map),
and [Unmanned Airspace's counter-UAS directory](https://unmannedairspace.info/counter-uas-industry-directory).
Hardware and supplier candidates also come from the public [DroneRules.World
manufacturer directory](https://dronerules.world/manufacturers). Organizations
that are not standalone businesses (for example, a nonprofit project, research
organization, subsidiary, business unit, or public program) are identified in
`entity_type` and `parent_or_acquirer`.
