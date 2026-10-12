# Research notes

## 2026-10-12 — Global drone company index, initial Keenable pass

### Scope

Include organizations that operated in the drone ecosystem at any time from
2016 onward, including companies founded earlier, acquired or closed companies,
and relevant business units. Record non-business entities separately instead
of treating a project or nonprofit as a company. The register has `status` for
live/gone/acquired/unknown and `entity_type` for businesses, business units,
suppliers, parent companies, and non-business organizations.

### Coverage and limits

Drone Industry Insights' 2026 Drone Market Map says it covers 1,413 companies
from 70 countries across hardware, software, and services, and reports that
about 300 entries were removed since 2022 due to acquisitions, dissolution, or
market exits. Its public overview says purely military manufacturers are
excluded and does not expose the full company roster. It is a coverage
benchmark, not a downloadable free list. Therefore this register is a public
source-built index and is not yet exhaustive.

Vertus' 2026 delivery tracker provided additional operators and status leads,
including inactive delivery activity at DroneUp and acquired/dormant or
liquidated cases Swoop Aero and Volansi. Follow-up reporting says Swoop Aero's
operating company entered liquidation in November 2024 and its assets were sold
to a new entity in 2025; Swoop is therefore marked `gone`, with the asset buyer
noted separately. Company sites were used to check names, official domains,
and self-reported founding years where available.

Military coverage now includes selected prime contractors, specialist UAS
makers, and counter-UAS detection and defeat vendors in addition to current
procurement rosters. Keenable surfaced a public military-company directory and
a 2026 counter-UAS map; these help broaden the roster but are not complete
company registries. Unmanned Airspace describes its paid counter-UAS directory
as containing 654 companies and over 1,000 system descriptions in the September
2026 edition. Large defense groups are included where they have identifiable
drone programs; the index labels parent groups and business units to avoid
implying each is a standalone drone manufacturer.

### Sources

- Drone Industry Insights, [Drone Market Map 2026](https://droneii.com/drone-market-map-2026)
- Drone Industry Insights, [2026 map overview](https://droneii.com/project/the-drone-market-environment-map-2026)
- Vertus, [delivery operator tracker](https://vertus.aero/intelligence?from=article-promo)
- Vertus, [company directory](https://vertus.aero/intelligence/companies)
- Vertus, [delivery world map and status snapshot](https://vertus.aero/intelligence/drone-delivery?from=article-promo)
- Companies' official websites linked in `companies.csv`
- U.S. War Department, [Drone Dominance Program Phase I vendor list](https://www.war.gov/News/Releases/Release/Article/4396462/war-department-announces-vendors-invited-to-compete-in-phase-i-of-the-drone-dom/)
- European Commission, [EU-Ukraine Drone Alliance founding members](https://defence-industry-space.ec.europa.eu/commission-launches-eu-ukraine-drone-alliance-boost-drone-and-counter-drone-technology-2026-07-17_en)
- Drone Intelligence, [company map by segment](https://droneintelligence.ai/market-map)
- DroneRules.World, [public manufacturer and component directory](https://dronerules.world/manufacturers)
- Drone & Defense, [military drone company directory](https://droneanddefense.com/unmanned-systems/drones/military-drone-companies)
- Drone Intelligence, [counter-UAS capability map](https://droneintelligence.ai/counter-uas-map)
- Unmanned Airspace, [global counter-UAS industry directory](https://unmannedairspace.info/counter-uas-industry-directory)
- Business News Australia, [Swoop Aero administrators accept offer following liquidation vote](https://businessnewsaustralia.com/articles/swoop-aero-administrators--accept-offer--to-salvage-company-with-re-employment-plans.html)
- Vertus, [Swoop Aero status and asset-sale summary](https://vertus.aero/intelligence/companies/swoop-aero)

### Next research pass

1. Verify the 41 candidates carried over from the archived catalog against
   sources confirming activity during or after 2016.
2. Expand beyond delivery to global commercial manufacturers, services,
   software, components, counter-UAS, and purely military manufacturers. The
   current pass includes selected multinational defense primes and counter-UAS
   firms as well as EU-Ukraine Alliance members and U.S. Drone Dominance Program
   vendors; entries without independent current evidence should remain `unknown`.
   A public manufacturer directory adds component suppliers and consumer/FPV
   brands, though it exposes only a subset of the 221 companies it says its
   catalog represents.
3. Resolve current, acquired, dormant, and legally dissolved status, with
   separate fields for parent/acquirer and status evidence.
4. Add country, segment, first/last known active years, and a source per claim.
