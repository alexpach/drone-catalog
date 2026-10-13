#!/usr/bin/env python3
"""Merge Drone Dominance Program (DDP) vendors into companies.csv.

Source: https://dronedominance.mil/vendors.html, whose rosters live in
https://dronedominance.mil/js/vendor-data.js (snapshot 2026-10-13). Phase 1 is
the 26 Gauntlet I competitors; Phase 2 is the 49 Phase 2 Qualifier invitees
plus the lethality (munitions and warhead) vendors teamed with them.

Each roster entry maps to one or more register names (team entries such as
"ADS + LUMENIER" are split into their member companies). Existing rows get a
"DDP:" note and missing domains filled from the DDP vendor directory; new rows
are appended. Re-running is idempotent.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "companies.csv"
SOURCE = "https://dronedominance.mil/vendors.html"

# Roster name as written on the DDP site -> register name(s).
PHASE1 = {
    "ANNO.AI, INC.": ["ANNO.AI"],
    "ASCENT AEROSYSTEMS INC.": ["Ascent AeroSystems"],
    "AUTERION GOVERNMENT SOLUTIONS INC.": ["Auterion Government Solutions"],
    "DRAGANFLY, INC.": ["Draganfly"],
    "DZYNE TECHNOLOGIES, LLC": ["DZYNE Technologies"],
    "EWING AEROSPACE LLC": ["Ewing Aerospace"],
    "FARAGE PRECISION, LLC": ["Farage Precision"],
    "FIRESTORM LABS, INC.": ["Firestorm Labs"],
    "GENERAL CHERRY CORP": ["General Cherry Corp"],
    "GREENSIGHT INC.": ["GreenSight"],
    "GRIFFON AEROSPACE, INC.": ["Griffon Aerospace"],
    "HALO AERONAUTICS, LLC": ["Halo Aeronautics"],
    "MODALAI, INC.": ["ModalAI"],
    "NEROS, INC.": ["Neros"],
    "NOKTURNAL AI": ["Nokturnal AI"],
    "PALADIN DEFENSE SERVICES LLC": ["Paladin Defense Services"],
    "PERENNIAL AUTONOMY": ["Perennial Autonomy"],
    "PERFORMANCE DRONE WORKS LLC": ["Performance Drone Works"],
    "SKYCUTTER": ["Skycutter"],
    "SWARM DEFENSE TECHNOLOGIES, LLC": ["Swarm Defense Technologies"],
    "TEAL DRONES INC.": ["Teal Drones"],
    "TITAN DYNAMICS, INC.": ["Titan Dynamics"],
    "UKRAINIAN DEFENSE DRONES TECH CORP": ["Ukrainian Defense Drones Tech Corp"],
    "VECTOR DEFENSE, INC.": ["Vector Defense"],
    "W S DARLEY & CO": ["W.S. Darley & Co."],
    "XTEND REALITY INC.": ["XTEND"],
}
GAUNTLET1_TOP11 = {
    "Skycutter", "Neros", "Perennial Autonomy", "ModalAI", "Auterion Government Solutions",
    "Ukrainian Defense Drones Tech Corp", "Griffon Aerospace", "Nokturnal AI",
    "Halo Aeronautics", "Ascent AeroSystems", "Farage Precision",
}

PHASE2 = {
    "Adler Aerospace LLC": ["Adler Aerospace"],
    "ADS + LUMENIER": ["ADS Inc.", "Lumenier"],
    "AeroVironment (AV) Inc.": ["AeroVironment"],
    "Agilis Air Inc.": ["Agilis Air"],
    "Ascent Aerosystems Inc.": ["Ascent AeroSystems"],
    "Auterion Government Solutions": ["Auterion Government Solutions"],
    "Chase Defense Partners/Advanced Aircraft Company": ["Chase Defense Partners", "Advanced Aircraft Company"],
    "Chey-Tac Inc.": ["Chey-Tac"],
    "Cyclops Defense LLC": ["Cyclops Defense"],
    "DefendEye USA Inc.": ["DefendEye USA"],
    "Envision Technology, LLC": ["Envision Technology"],
    "Ewing Aerospace": ["Ewing Aerospace"],
    "Farage Precision": ["Farage Precision"],
    "Griffon Aerospace": ["Griffon Aerospace"],
    "Grim Tech": ["Grim Tech"],
    "Halo Aeronautics, LLC": ["Halo Aeronautics"],
    "Hyperscale": ["Hyperscale"],
    "Kratos": ["Kratos SRE"],
    "LTMiltech USA": ["LTMiltech USA"],
    "Mithril Defense": ["Mithril Defense"],
    "ModalAI Inc.": ["ModalAI"],
    "Mountain Horse Solutions + AG3Labs": ["Mountain Horse Solutions", "AG3 Labs"],
    "Mountain Horse Solutions + Draganfly": ["Mountain Horse Solutions", "Draganfly"],
    "Neros": ["Neros"],
    "ORQA US LLC": ["ORQA US"],
    "Perennial Autonomy": ["Perennial Autonomy"],
    "Performance Drone Works (PDW)": ["Performance Drone Works"],
    "Planned Systems International": ["Planned Systems International"],
    "Powerus": ["Powerus"],
    "Rajant Corporation": ["Rajant"],
    "Renegade UxS": ["Renegade UxS"],
    "Skycutter": ["Skycutter"],
    "SOF Landing": ["SOF Landing"],
    "Stellarion": ["Stellarion"],
    "Swarm Defense": ["Swarm Defense Technologies"],
    "T3i Inc.": ["T3i"],
    "Teal Drones Inc.": ["Teal Drones"],
    "Tesseract Ventures": ["Tesseract Ventures"],
    "UAS Nexus": ["UAS Nexus"],
    "UDD (Ukrainian Defense Drones) Tech Corp.": ["Ukrainian Defense Drones Tech Corp"],
    "Vantor Inc.": ["Vantor"],
    "Vector": ["Vector Defense"],
    "Viter Systems Inc.": ["Viter Systems"],
    "Volatus Aerospace USA": ["Volatus Aerospace USA"],
    "W.S. Darley & Co.": ["W.S. Darley & Co."],
    "WGS Systems, LLC": ["WGS Systems"],
    "Wilcox Cherry Defense LLC": ["Wilcox Cherry Defense"],
    "XTEND Reality Inc.": ["XTEND"],
    "Zaruba": ["Zaruba"],
}
GAUNTLET2_ADVANCED = {
    "Ascent AeroSystems", "Auterion Government Solutions", "Griffon Aerospace", "Grim Tech",
    "Hyperscale", "ModalAI", "Mountain Horse Solutions", "AG3 Labs", "Neros", "ORQA US",
    "Perennial Autonomy", "Renegade UxS", "Skycutter", "Stellarion",
    "Swarm Defense Technologies", "Teal Drones", "Ukrainian Defense Drones Tech Corp",
    "Vector Defense", "Wilcox Cherry Defense", "XTEND",
}
PHASE2_NO_SHOW = {
    "Chase Defense Partners", "Advanced Aircraft Company", "Chey-Tac", "Cyclops Defense",
    "Planned Systems International", "Tesseract Ventures",
}

# Lethality vendors: register name -> Lethality Prize Challenge winner?
LETHALITY = {
    "Bravo Ordnance": True, "Kela Defense US": True, "Kraken Kinetics": True,
    "Mountain Horse Solutions": True, "Northrop Grumman": True,
    "Perennial Autonomy": False, "Vector Defense": False, "Nammo": False, "XTEND": False,
}

# New rows: name -> (domain, industry, country, entity_type, parent, note).
# Domains come from the DDP vendor directory or the company's own site;
# anything not established from those is left "unknown".
NEW = {
    "Draganfly": ("draganfly.com", "military and public-safety UAS", "Canada", "business", "", ""),
    "Perennial Autonomy": ("perennialautonomy.com", "military drone hardware", "United States", "business", "", ""),
    "Skycutter": ("skycutteruas.co.uk", "military drone hardware", "United Kingdom", "business", "", ""),
    "Titan Dynamics": ("unknown", "military UAS hardware", "unknown", "business", "", "Official domain and country need validation."),
    "Adler Aerospace": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "ADS Inc.": ("unknown", "defense supplier and systems integration", "United States", "business", "", "Competed as team ADS + Lumenier; identity as ADS Inc. is inferred."),
    "Lumenier": ("lumenier.com", "FPV and military drone hardware", "United States", "business", "", "Competed as team ADS + Lumenier."),
    "Agilis Air": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Chase Defense Partners": ("unknown", "defense supplier", "United States", "business", "", "Competed as team with Advanced Aircraft Company; official domain needs validation."),
    "Advanced Aircraft Company": ("unknown", "military UAS hardware", "United States", "business", "", "Competed as team with Chase Defense Partners; official domain needs validation."),
    "Chey-Tac": ("unknown", "defense supplier", "United States", "business", "", "Official domain needs validation."),
    "Cyclops Defense": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "DefendEye USA": ("unknown", "military UAS hardware", "United States", "business_unit", "", "U.S. entity; parent company needs validation."),
    "Envision Technology": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Grim Tech": ("grim.info", "military drone hardware", "Ukraine", "business", "", "Site is a Ukrainian military drone maker (Grim)."),
    "Hyperscale": ("hyperscale.us", "military drone hardware", "United States", "business", "", ""),
    "LTMiltech USA": ("unknown", "military UAS hardware", "United States", "business_unit", "", "U.S. entity; parent company needs validation."),
    "Mithril Defense": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Mountain Horse Solutions": ("mtnhorse.com", "military drones and munitions", "United States", "business", "", "Competed in Phase 2 teamed with AG3 Labs and with Draganfly."),
    "AG3 Labs": ("unknown", "military UAS hardware", "unknown", "business", "", "Competed as team Mountain Horse Solutions + AG3 Labs; official domain and country need validation."),
    "ORQA US": ("orqaus.com", "military and FPV drone hardware", "United States", "business_unit", "ORQA", "U.S. arm of Croatian FPV maker ORQA."),
    "Planned Systems International": ("unknown", "defense IT and services", "United States", "business", "", "Official domain needs validation."),
    "Powerus": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Rajant": ("rajant.com", "mesh networking for unmanned systems", "United States", "supplier", "", ""),
    "Renegade UxS": ("renegadeuxs.com", "military drone hardware", "United States", "business", "", ""),
    "SOF Landing": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Stellarion": ("stellarion.group", "military FPV drones", "Ukraine", "business", "", "Site describes Ukrainian military FPV drones."),
    "T3i": ("unknown", "defense supplier", "United States", "business", "", "Official domain needs validation."),
    "Tesseract Ventures": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "UAS Nexus": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Vantor": ("unknown", "geospatial intelligence and defense systems", "United States", "business", "", "Official domain needs validation."),
    "Viter Systems": ("unknown", "military UAS hardware", "United States", "business", "", "Official domain needs validation."),
    "Volatus Aerospace USA": ("unknown", "drone services and military UAS", "United States", "business_unit", "Volatus Aerospace", "U.S. arm of Volatus Aerospace."),
    "WGS Systems": ("unknown", "defense supplier", "United States", "business", "", "Official domain needs validation."),
    "Wilcox Cherry Defense": ("gencherry.com", "military FPV drones", "United States", "business", "", "DDP contacts are from Wilcox Industries and General Cherry; joint-venture structure needs validation."),
    "Zaruba": ("unknown", "military UAS hardware", "unknown", "business", "", "Official domain and country need validation."),
    "Bravo Ordnance": ("warhead.co", "drone munitions and warheads", "United States", "business", "", ""),
    "Kela Defense US": ("keladefense.com", "drone munitions and warheads", "United States", "business_unit", "Kela Defense", "U.S. entity of Kela Defense."),
    "Kraken Kinetics": ("krakenkinetics.com", "drone munitions and warheads", "United States", "business", "", ""),
    "Nammo": ("unknown", "munitions and warheads", "Norway", "business", "", "Warhead provider teamed with Vector."),
}

# Domains and relationships the DDP vendor directory adds to existing rows.
EXISTING_FIXES = {
    "Ascent AeroSystems": {"domain": "robinsonheli.com", "parent_or_acquirer": "Robinson Helicopter",
                           "note": "DDP directory lists a Robinson Helicopter (robinsonheli.com/unmanned) site and contacts."},
    "Farage Precision": {"domain": "farageprecision.com"},
    "Halo Aeronautics": {"domain": "bylight.com", "parent_or_acquirer": "By Light",
                         "note": "DDP directory lists a By Light (bylight.com/halo-aeronautics) site."},
    "Nokturnal AI": {"domain": "nokturnal.ai"},
    "Swarm Defense Technologies": {"domain": "swarmdefense.com"},
    "Vector Defense": {"domain": "tfvector.com",
                       "note": "Phase 1 'Vector Defense, Inc.' and Phase 2 'Vector' (tfvector.com) are treated as one company; match is inferred."},
}


def participation():
    """Return register name -> list of DDP participation phrases."""
    parts = {}
    for names in PHASE1.values():
        for name in names:
            label = "Phase 1 Gauntlet I top 11" if name in GAUNTLET1_TOP11 else "Phase 1 Gauntlet I"
            parts.setdefault(name, []).append(label)
    for roster, names in PHASE2.items():
        team = f" (as '{roster}')" if len(names) > 1 else ""
        for name in names:
            if name in GAUNTLET2_ADVANCED:
                label = "Phase 2 Qualifier, advanced to Gauntlet II"
            elif name in PHASE2_NO_SHOW:
                label = "Phase 2 Qualifier invitee, did not participate"
            else:
                label = "Phase 2 Qualifier"
            parts.setdefault(name, []).append(label + team)
    for name, winner in LETHALITY.items():
        label = "Phase 2 lethality vendor" + (" (Lethality Prize Challenge winner)" if winner else "")
        parts.setdefault(name, []).append(label)
    return {name: list(dict.fromkeys(labels)) for name, labels in parts.items()}


def add_note(notes, extra):
    return extra if not notes else notes if extra in notes else f"{notes} {extra}"


def main():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    by_name = {row["name"].casefold(): row for row in rows}
    added = updated = 0

    for name, labels in sorted(participation().items()):
        ddp_note = "DDP: " + "; ".join(labels) + "."
        row = by_name.get(name.casefold())
        if row is None:
            if name not in NEW:
                raise SystemExit(f"No register row or NEW entry for {name!r}")
            domain, industry, country, entity, parent, note = NEW[name]
            row = {
                "name": name, "domain": domain, "industry": industry,
                "country_of_origin": country, "status": "live", "entity_type": entity,
                "parent_or_acquirer": parent, "founded_year": "",
                "period_status": "verified_active_2016_onward",
                "evidence_url": f"https://{domain}" if domain != "unknown" else SOURCE,
                "status_source": SOURCE, "notes": add_note(note, ddp_note),
            }
            rows.append(row)
            by_name[name.casefold()] = row
            added += 1
            continue
        before = dict(row)
        fix = EXISTING_FIXES.get(name, {})
        if row["domain"] in ("", "unknown") and fix.get("domain"):
            row["domain"] = fix["domain"]
            row["notes"] = row["notes"].replace("; official domain needs validation.", ".")
            if row["evidence_url"] == row["status_source"]:
                row["evidence_url"] = f"https://{fix['domain']}"
        if fix.get("parent_or_acquirer") and not row["parent_or_acquirer"]:
            row["parent_or_acquirer"] = fix["parent_or_acquirer"]
        if fix.get("note"):
            row["notes"] = add_note(row["notes"], fix["note"])
        # Replace any earlier DDP note so re-runs reflect the current roster.
        kept = row["notes"].split(" DDP: ")[0] if " DDP: " in row["notes"] else (
            "" if row["notes"].startswith("DDP: ") else row["notes"])
        row["notes"] = add_note(kept, ddp_note)
        updated += row != before

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Added {added}, updated {updated}; {len(rows)} organizations in {CSV_PATH.name}")


if __name__ == "__main__":
    main()
