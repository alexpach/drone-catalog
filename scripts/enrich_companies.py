#!/usr/bin/env python3
"""Normalize and widen companies.csv using the archived register and sources."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "companies.csv"
ARCHIVE_MAKES = ROOT / "archive/legacy/data/make"
DDP_SOURCE = "https://www.war.gov/News/Releases/Release/Article/4396462/war-department-announces-vendors-invited-to-compete-in-phase-i-of-the-drone-dom/"
EU_ALLIANCE_SOURCE = "https://defence-industry-space.ec.europa.eu/commission-launches-eu-ukraine-drone-alliance-boost-drone-and-counter-drone-technology-2026-07-17_en"
MARKET_MAP_SOURCE = "https://droneintelligence.ai/market-map"

# Deliberately conservative: unknown means Keenable sources reviewed so far did
# not establish a reliable current status, even if an official domain exists.
STATUS = {
    "AeroVironment": "live", "American Robotics": "acquired",
    "Asylon Robotics": "live", "Autel Robotics": "live",
    "Baykar": "live", "BetaFPV": "live", "Delair": "live", "DJI": "live",
    "DroneHub": "live", "Easy Aerial": "live", "EHang": "live",
    "Fotokite": "live", "Freefly Systems": "live",
    "General Atomics Aeronautical": "live", "H3 Dynamics": "live",
    "HEISHA": "live", "Hextronics": "live", "Holy Stone": "live",
    "iFlight": "live", "Northrop Grumman": "live", "Parrot": "live",
    "Percepto": "live", "Quantum-Systems": "live", "senseFly": "acquired",
    "Skydio": "live", "Sunflower Labs": "live", "Teledyne FLIR": "acquired",
    "Wingtra": "live", "xCraft": "live",
    "Wingcopter": "live", "NextLeap Aeronautics": "live",
    "Agricision": "live", "Aizy Tech": "live", "Biodrone": "live",
    "Prometheus UAV": "live", "Arcsky": "live", "Rodella Technologies": "live",
    "Aeronica Advance Technologies": "live", "Shark Tech Drone": "live",
    "Briech UAS": "live", "FloFly Technologies": "live", "Bheema Drones": "live",
    "InsideFPV": "live", "Aasma Aerospace": "live", "Skydagger Drones": "live",
    "Dronecode": "unknown", "A2Z Drone Delivery": "live",
    "Amazon Prime Air": "live", "Antwork": "live", "Dronamics": "live",
    "DroneUp": "live", "Elroy Air": "live", "FlyingBasket": "live",
    "Garuda Aerospace": "live", "ideaForge Technology": "live",
    "Matternet": "live", "Meituan": "live", "Natilus": "live",
    "Pyka": "live", "Sabrewing Aircraft Company": "unknown",
    "Skye Air Mobility": "live", "Skyports Drone Services": "live",
    "Speedbird Aero": "live", "TechEagle": "live", "UPS Flight Forward": "live",
    "Wing": "live", "Zipline": "live", "Swoop Aero": "gone", "Volansi": "acquired",
    "Anzu Robotics": "live", "Aero Systems West": "live", "Astral.us": "live",
    "Auterion": "live", "AirMap": "acquired", "Altitude Angel": "unknown",
    "OneSky": "live", "Thales": "live", "Lockheed Martin": "live",
    "D-Fend Solutions": "acquired", "Dedrone": "acquired",
    "Allen Control Systems": "live", "Motorola Solutions": "live", "Axon": "live",
}

PARENTS = {
    "American Robotics": "Ondas Holdings",
    "senseFly": "AgEagle Aerial Systems",
    "Teledyne FLIR": "Teledyne Technologies",
    "Volansi": "Sierra Nevada Corporation",
    "AirMap": "DroneUp",
    "D-Fend Solutions": "Motorola Solutions",
    "Dedrone": "Axon",
    "Auterion Government Solutions": "Auterion",
    "Kratos SRE": "Kratos Defense & Security Solutions",
    "Amazon Prime Air": "Amazon",
    "Meituan": "Meituan",
    "UPS Flight Forward": "UPS",
    "Wing": "Alphabet",
}

OVERRIDES = {
    "SenSys Robotics": {"country_of_origin": "Japan", "industry": "drone-in-a-box and autonomous security"},
    "ArrowTec": {"industry": "drone-in-a-box and autonomous security"},
    "Azur Drones": {"industry": "drone-in-a-box and autonomous security"},
    "FIMI": {"industry": "consumer and hobby drones"},
    "HeroTech8": {"industry": "drone-in-a-box and autonomous security"},
    "Hive Systems": {"industry": "drone-in-a-box and autonomous security"},
    "Hoverseen": {"industry": "drone-in-a-box and autonomous security"},
    "Hubsan": {"industry": "consumer and hobby drones"},
    "Nightingale Security": {"industry": "drone-in-a-box and autonomous security"},
    "PowerVision": {"industry": "consumer and industrial drones"},
    "Skycharge": {"industry": "drone infrastructure and charging systems"},
    "Walkera": {"industry": "consumer, hobby and FPV drones"},
    "Yuneec": {"industry": "consumer and enterprise drones"},
    "Wingcopter": {"country_of_origin": "Germany", "industry": "drone delivery and logistics"},
    "NextLeap Aeronautics": {"country_of_origin": "India", "industry": "agriculture and defense UAS"},
    "Agricision": {"country_of_origin": "United States", "industry": "agriculture UAS and software"},
    "Aizy Tech": {"country_of_origin": "United States", "industry": "public-safety and search-and-rescue UAS"},
    "Biodrone": {"country_of_origin": "Norway", "industry": "environmental monitoring and defense UAS"},
    "Prometheus UAV": {"country_of_origin": "Poland", "industry": "enterprise and defense UAS"},
    "Arcsky": {"country_of_origin": "United States", "industry": "industrial and heavy-lift UAS"},
    "Rodella Technologies": {"country_of_origin": "India", "industry": "military and defense UAS"},
    "AA Robotics": {"industry": "military and enterprise UAS"},
    "Aeronica Advance Technologies": {"country_of_origin": "India", "industry": "agriculture, enterprise and defense UAS"},
    "Shark Tech Drone": {"country_of_origin": "China", "industry": "commercial UAS manufacturing"},
    "Briech UAS": {"country_of_origin": "Nigeria", "industry": "military and defense UAS"},
    "FloFly Technologies": {"country_of_origin": "India", "industry": "agriculture, cargo and defense UAS"},
    "Bheema Drones": {"country_of_origin": "India", "industry": "industrial and agriculture UAS"},
    "InsideFPV": {"country_of_origin": "India", "industry": "military FPV UAS"},
    "Aasma Aerospace": {"country_of_origin": "India", "industry": "public-safety UAS"},
    "A2Z Drone Delivery": {"country_of_origin": "United States", "industry": "drone delivery hardware"},
    "Amazon Prime Air": {"country_of_origin": "United States", "industry": "drone delivery and logistics"},
    "Antwork": {"country_of_origin": "China", "industry": "medical drone delivery"},
    "Dronamics": {"country_of_origin": "Bulgaria", "industry": "cargo drone manufacturing and delivery"},
    "DroneUp": {"country_of_origin": "United States", "industry": "drone services and airspace software"},
    "Elroy Air": {"country_of_origin": "United States", "industry": "cargo UAS manufacturing"},
    "FlyingBasket": {"country_of_origin": "Italy", "industry": "industrial heavy-lift UAS"},
    "Garuda Aerospace": {"country_of_origin": "India", "industry": "agriculture, industrial and delivery UAS"},
    "ideaForge Technology": {"country_of_origin": "India", "industry": "military, public-safety and enterprise UAS"},
    "Matternet": {"country_of_origin": "United States", "industry": "medical drone delivery"},
    "Meituan": {"country_of_origin": "China", "industry": "drone delivery and logistics"},
    "Natilus": {"country_of_origin": "United States", "industry": "cargo UAS manufacturing"},
    "Pyka": {"country_of_origin": "United States", "industry": "agriculture and cargo UAS"},
    "Sabrewing Aircraft Company": {"country_of_origin": "United States", "industry": "cargo UAS manufacturing"},
    "Skye Air Mobility": {"country_of_origin": "India", "industry": "drone delivery and logistics"},
    "Skydagger Drones": {"industry": "military and defense UAS"},
    "Skyports Drone Services": {"country_of_origin": "United Kingdom", "industry": "drone services and logistics"},
    "Speedbird Aero": {"country_of_origin": "Brazil", "industry": "drone delivery and logistics"},
    "TechEagle": {"country_of_origin": "India", "industry": "medical and cargo drone delivery"},
    "UPS Flight Forward": {"country_of_origin": "United States", "industry": "drone delivery and logistics"},
    "Wing": {"country_of_origin": "United States", "industry": "drone delivery and logistics"},
    "Zipline": {"country_of_origin": "United States", "industry": "medical and retail drone delivery"},
    "Swoop Aero": {"country_of_origin": "Australia", "industry": "medical and humanitarian drone delivery"},
    "Volansi": {"country_of_origin": "United States", "industry": "cargo drone delivery"},
}

EXTRA = [
    # Current commercial/dual-use market map and airspace/counter-UAS firms.
    ("Anzu Robotics", "anzurobotics.com", "commercial drone hardware", "United States", "live", "business", "", "https://anzurobotics.com/2024/04/17/press-release-anzu-robotics-enters-the-drone-market-and-launches-two-enterprise-drone-platforms", "US-owned enterprise drone manufacturer; company says its aircraft are manufactured in Malaysia."),
    ("Aero Systems West", "aerosystemswest.com", "enterprise and defense drone hardware", "United States", "live", "business", "Nippon Kayaku", "https://aerosystemswest.com/", "California heavy-lift drone maker; backed by Nippon Kayaku."),
    ("Astral.us", "astral.us", "autonomy software and AI", "United States", "live", "business", "", MARKET_MAP_SOURCE, "Autonomy and fleet software."),
    ("Auterion", "auterion.com", "drone software and autonomy", "United States / Switzerland", "live", "business", "", "https://auterion.com/", "Open-source flight stack and autonomy software."),
    ("AirMap", "droneup.com", "airspace management and UTM software", "United States", "acquired", "business", "DroneUp", MARKET_MAP_SOURCE, "Acquired by DroneUp in 2021; retained here as an acquired company/technology name."),
    ("Altitude Angel", "altitudeangel.com", "airspace management and UTM software", "United Kingdom", "unknown", "business", "", MARKET_MAP_SOURCE, "Reported in administration in October 2025; administration does not by itself confirm that operations ended or the company was dissolved."),
    ("OneSky", "onesky.xyz", "airspace management and UTM software", "United States", "live", "business", "", MARKET_MAP_SOURCE, "Drone traffic deconfliction and route-planning software."),
    ("Thales", "thalesgroup.com", "aerospace, defense and UTM", "France", "live", "business", "", MARKET_MAP_SOURCE, "Large parent group with drone and airspace-management activities."),
    ("Lockheed Martin", "lockheedmartin.com", "military UAS and defense systems", "United States", "live", "business", "", MARKET_MAP_SOURCE, "Defense prime with unmanned-aircraft programs."),
    ("D-Fend Solutions", "d-fendsolutions.com", "counter-UAS", "Israel / United States", "acquired", "business", "Motorola Solutions", MARKET_MAP_SOURCE, "Acquisition by Motorola Solutions closed in August 2026."),
    ("Dedrone", "dedrone.com", "counter-UAS", "United States / Germany", "acquired", "business", "Axon", MARKET_MAP_SOURCE, "Acquired by Axon in October 2024."),
    ("Allen Control Systems", "allencontrolsystems.com", "counter-UAS", "United States", "live", "business", "", MARKET_MAP_SOURCE, "Counter-drone systems."),
    ("Motorola Solutions", "motorolasolutions.com", "counter-UAS and public-safety systems", "United States", "live", "parent_company", "", MARKET_MAP_SOURCE, "Parent of D-Fend Solutions."),
    ("Axon", "axon.com", "counter-UAS and public-safety systems", "United States", "live", "parent_company", "", MARKET_MAP_SOURCE, "Parent of Dedrone."),
    # The EU-Ukraine Drone Alliance adds defense-focused firms absent from civil maps.
    ("ORQA", "orqafpv.com", "military and FPV drone hardware", "Croatia", "live", "business", "", EU_ALLIANCE_SOURCE, "Named as a founding EU-Ukraine Drone Alliance member."),
    ("Indra Group", "indracompany.com", "military UAS and defense systems", "Spain", "live", "business", "", EU_ALLIANCE_SOURCE, "Alliance member; large defense and technology group."),
    ("Fincantieri", "fincantieri.com", "military UAS and naval systems", "Italy", "live", "business", "", EU_ALLIANCE_SOURCE, "Alliance member; large shipbuilding and defense group."),
    ("WB Group", "wbgroup.pl", "military UAS and defense systems", "Poland", "live", "business", "", EU_ALLIANCE_SOURCE, "Alliance member; unmanned systems include FlyEye and Warmate."),
    ("Destinus", "destinus.com", "military and cargo autonomous aircraft", "Netherlands", "live", "business", "", EU_ALLIANCE_SOURCE, "Named as a founding EU-Ukraine Drone Alliance member."),
    ("RSI Europe", "unknown", "defense and counter-UAS", "unknown", "unknown", "business", "", EU_ALLIANCE_SOURCE, "Alliance member; exact legal identity, country, domain, and status need validation."),
    ("TERMA", "terma.com", "defense and counter-UAS", "Denmark", "live", "business", "", EU_ALLIANCE_SOURCE, "Alliance member; defense and aerospace supplier."),
    ("Skyfall Industries", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("Greentech Harvest", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("Tencore", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("Deviro", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("Vyriy Industry", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("Athlon Avia", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("TAF Industries", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Alliance lists legal entity TEHAVTOFART PIVDEN; official domain not yet verified."),
    ("UFORCE", "unknown", "military drone hardware", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    ("F-Drones", "unknown", "military drone hardware and components", "Ukraine", "live", "business", "", EU_ALLIANCE_SOURCE, "Named Ukrainian Alliance member; official domain not yet verified."),
    # International military UAS and counter-UAS providers from Keenable's
    # Drone Intelligence and Drone & Defense directory research (2026).
    ("Anduril Industries", "anduril.com", "military UAS, autonomy and counter-UAS", "United States", "live", "business", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Defense technology company with Altius loitering munitions, Lattice autonomy and counter-UAS systems."),
    ("Shield AI", "shield.ai", "military UAS and autonomy software", "United States", "live", "business", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Defense technology company with V-BAT unmanned aircraft and Hivemind autonomy."),
    ("Boeing", "boeing.com", "military unmanned aircraft", "United States", "live", "parent_company", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Defense and aerospace parent with MQ-25 and MQ-28 programs and Insitu subsidiary."),
    ("Insitu", "insitu.com", "military and commercial UAS", "United States", "live", "business_unit", "Boeing", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Boeing subsidiary; ScanEagle unmanned aircraft family."),
    ("Textron Systems", "textronsystems.com", "military UAS and target aircraft", "United States", "live", "business_unit", "Textron", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Textron business unit with Shadow, Aerosonde and Nightwarden unmanned aircraft."),
    ("Elbit Systems", "elbitsystems.com", "military UAS and counter-UAS", "Israel", "live", "business", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Defense company with Hermes and Skylark unmanned aircraft families."),
    ("Israel Aerospace Industries", "iai.co.il", "military UAS and defense systems", "Israel", "live", "state_owned_company", "State of Israel", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "State-owned aerospace company with Heron unmanned aircraft and loitering munitions."),
    ("Turkish Aerospace Industries", "tusas.com", "military UAS and aerospace", "Turkey", "live", "business", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Manufacturer of ANKA and AKSUNGUR unmanned aircraft."),
    ("STM Defense", "stm.com.tr", "military UAS and loitering munitions", "Turkey", "live", "business", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Defense contractor with KARGU loitering munitions and small unmanned systems."),
    ("Airbus", "airbus.com", "military UAS and aerospace", "Multinational (Europe)", "live", "parent_company", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "European aerospace group with Eurodrone, Zephyr and collaborative combat aircraft programs."),
    ("Leonardo", "leonardo.com", "military UAS and counter-UAS", "Italy", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense and aerospace company with Falco UAS and Falcon Shield counter-UAS."),
    ("BAE Systems", "baesystems.com", "military UAS and defense systems", "United Kingdom", "live", "business", "", "https://droneanddefense.com/unmanned-systems/drones/military-drone-companies", "Defense prime with unmanned-aircraft and autonomous systems programs."),
    ("Saab", "saab.com", "military UAS and counter-UAS", "Sweden", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense company with unmanned systems and Giraffe/Loke counter-UAS capabilities."),
    ("Hensoldt", "hensoldt.net", "military UAS sensors and counter-UAS", "Germany", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense sensor company with Xpeller counter-UAS systems."),
    ("Rheinmetall", "rheinmetall.com", "military UAS and counter-UAS", "Germany", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense group with unmanned systems and air-defense capabilities."),
    ("Diehl Defence", "diehl.com", "military UAS and counter-UAS", "Germany", "live", "business_unit", "Diehl Group", "https://droneintelligence.ai/counter-uas-map", "Diehl business unit; GUARDION modular counter-UAS offering."),
    ("MBDA", "mbda-systems.com", "military UAS and counter-UAS", "Multinational (Europe)", "live", "business", "Airbus / BAE Systems / Leonardo", "https://droneintelligence.ai/counter-uas-map", "European missile and defense joint venture with Sky Warden counter-UAS offering."),
    ("Rafael Advanced Defense Systems", "rafael.co.il", "counter-UAS and defense systems", "Israel", "live", "state_owned_company", "State of Israel", "https://droneintelligence.ai/counter-uas-map", "Israeli state-owned defense company with the Drone Dome counter-UAS family."),
    ("Hanwha Aerospace", "hanwhaaerospace.co.kr", "military UAS and counter-UAS", "South Korea", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense and aerospace group with air-defense systems relevant to counter-UAS."),
    ("LIG Nex1", "lignex1.com", "military UAS and counter-UAS", "South Korea", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense company with missile, radar and counter-UAS systems."),
    ("DroneShield", "droneshield.com", "counter-UAS", "Australia", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Public Australian counter-drone detection and defeat company."),
    ("Epirus", "epirusinc.com", "counter-UAS and directed energy", "United States", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense technology company developing Leonidas high-power microwave systems."),
    ("Fortem Technologies", "fortemtech.com", "counter-UAS and interceptor drones", "United States", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Counter-UAS provider combining radar, command software and interceptor drones."),
    ("Echodyne", "echodyne.com", "counter-UAS radar and sensing", "United States", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Radar manufacturer supplying compact electronically scanned sensors for counter-UAS."),
    ("Sensofusion", "sensofusion.com", "counter-UAS detection and RF sensing", "Finland", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Finnish provider of AIRFENCE RF-based drone detection and signals intelligence."),
    ("Numerica", "numerica.us", "counter-UAS radar and sensing", "United States", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Radar and analytics company with Spyglass short-range counter-UAS radar."),
    ("Robin Radar Systems", "robinradar.com", "counter-UAS radar and sensing", "Netherlands", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Dutch radar company specializing in small-drone detection."),
    ("Aaronia", "aaronia.com", "counter-UAS RF detection", "Germany", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "German RF sensing and direction-finding company with AARTOS counter-UAS systems."),
    ("Liteye Systems", "liteye.com", "counter-UAS", "United States", "acquired", "business", "DZYNE Technologies", "https://droneintelligence.ai/counter-uas-map", "Counter-UAS company identified as a DZYNE Technologies subsidiary."),
    ("SRC, Inc.", "srcinc.com", "counter-UAS and defense research", "United States", "live", "nonprofit", "", "https://droneintelligence.ai/counter-uas-map", "Not-for-profit research and development organization; supplies Silent Archer counter-UAS systems."),
    ("QinetiQ", "qinetiq.com", "military UAS sensors and counter-UAS", "United Kingdom", "live", "business", "", "https://droneintelligence.ai/counter-uas-map", "Defense and technology company with drone detection and counter-UAS capabilities."),
    # Vendors invited by the U.S. Drone Dominance Program in February 2026.
    ("ANNO.AI", "unknown", "military autonomy software and UAS", "unknown", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; country and official domain need validation."),
    ("Ascent AeroSystems", "unknown", "military and public-safety drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Auterion Government Solutions", "auterion.com", "military drone software and autonomy", "United States", "live", "business_unit", "Auterion", DDP_SOURCE, "Government business unit; invited U.S. Drone Dominance Program vendor."),
    ("DZYNE Technologies", "dzyne.com", "military UAS and defense systems", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Ewing Aerospace", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Farage Precision", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Firestorm Labs", "firestormlabs.com", "military UAS hardware and manufacturing", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("General Cherry Corp", "unknown", "military FPV drones", "Ukraine", "live", "business", "", DDP_SOURCE, "Defense reporting identifies the company as Ukraine-based."),
    ("GreenSight", "unknown", "drone hardware and software", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Griffon Aerospace", "griffonaerospace.com", "military UAS and target aircraft", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Halo Aeronautics", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Kratos SRE", "kratosdefense.com", "military UAS and target aircraft", "United States", "live", "business_unit", "Kratos Defense & Security Solutions", DDP_SOURCE, "Kratos subsidiary; invited U.S. Drone Dominance Program vendor."),
    ("ModalAI", "modalai.com", "drone components and autonomy software", "United States", "live", "business", "", DDP_SOURCE, "Flight computers and autonomy; invited U.S. Drone Dominance Program vendor."),
    ("Napatree Technology", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Neros", "neros.tech", "military drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Military drone maker; invited U.S. Drone Dominance Program vendor."),
    ("Nokturnal AI", "unknown", "military drone autonomy", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Paladin Defense Services", "unknown", "military UAS and defense services", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Performance Drone Works", "unknown", "military drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Responsibly Ltd", "unknown", "military UAS hardware", "United Kingdom", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Swarm Defense Technologies", "unknown", "military drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Teal Drones", "tealdrones.com", "military and public-safety drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Ukrainian Defense Drones Tech Corp", "unknown", "military drone hardware", "Ukraine", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Vector Defense", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("W.S. Darley & Co.", "darley.com", "defense supplier and drone systems", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("XTEND", "xtend.me", "military UAS and autonomy", "Israel", "live", "business", "", DDP_SOURCE, "XTEND Reality invited to U.S. Drone Dominance Program."),
    ("ANNO.AI", "unknown", "military autonomy software and UAS", "unknown", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain and country need validation."),
    ("Ascent AeroSystems", "unknown", "military and public-safety drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Auterion Government Solutions", "auterion.com", "military drone software and autonomy", "United States", "live", "business_unit", "Auterion", DDP_SOURCE, "Government business unit; invited U.S. Drone Dominance Program vendor."),
    ("DZYNE Technologies", "dzyne.com", "military UAS and defense systems", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Ewing Aerospace", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Farage Precision", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Firestorm Labs", "firestormlabs.com", "military UAS hardware and manufacturing", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("General Cherry Corp", "unknown", "military FPV drones", "Ukraine", "live", "business", "", DDP_SOURCE, "Defense reporting identifies the company as Ukraine-based."),
    ("GreenSight", "unknown", "drone hardware and software", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Griffon Aerospace", "griffonaerospace.com", "military UAS and target aircraft", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Halo Aeronautics", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Kratos SRE", "kratosdefense.com", "military UAS and target aircraft", "United States", "live", "business_unit", "Kratos Defense & Security Solutions", DDP_SOURCE, "Kratos subsidiary; invited U.S. Drone Dominance Program vendor."),
    ("ModalAI", "modalai.com", "drone components and autonomy software", "United States", "live", "business", "", DDP_SOURCE, "Flight computers and autonomy; invited U.S. Drone Dominance Program vendor."),
    ("Napatree Technology", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Neros", "neros.tech", "military drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Military drone maker; invited U.S. Drone Dominance Program vendor."),
    ("Nokturnal AI", "unknown", "military drone autonomy", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Paladin Defense Services", "unknown", "military UAS and defense services", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Performance Drone Works", "unknown", "military drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Responsibly Ltd", "unknown", "military UAS hardware", "unknown", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain and country need validation."),
    ("Swarm Defense Technologies", "unknown", "military drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("Teal Drones", "tealdrones.com", "military and public-safety drone hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Ukrainian Defense Drones Tech Corp", "unknown", "military drone hardware", "Ukraine", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("Vector Defense", "unknown", "military UAS hardware", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor; official domain needs validation."),
    ("W.S. Darley & Co.", "darley.com", "defense supplier and drone systems", "United States", "live", "business", "", DDP_SOURCE, "Invited U.S. Drone Dominance Program vendor."),
    ("XTEND", "xtend.me", "military UAS and autonomy", "Israel", "live", "business", "", DDP_SOURCE, "XTEND Reality invited to U.S. Drone Dominance Program."),
    # Additional hardware, component, and avionics suppliers from the 2026 catalog.
    ("AgEagle Aerial Systems", "ageagle.com", "mapping, agriculture and enterprise UAS", "United States", "live", "business", "", "https://dronerules.world/manufacturers", "Drone and geospatial systems company; acquired senseFly."),
    ("CNHL (China Hobby Line)", "chinahobbyline.com", "drone batteries and power systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "LiPo batteries for FPV and RC aircraft."),
    ("CaddxFPV", "caddxfpv.com", "FPV cameras and video systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Digital and analog FPV video systems."),
    ("CubePilot", "cubepilot.org", "drone autopilots and flight-control components", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Autopilots and carrier boards for ArduPilot-based systems."),
    ("Diatone", "diatone.us", "FPV drone hardware", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV drone and component maker."),
    ("Dronetag", "dronetag.com", "remote ID and drone avionics", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Network and broadcast Remote ID hardware."),
    ("Flywoo", "flywoo.net", "FPV drone hardware and electronics", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV drones, GPS modules, and electronics."),
    ("Foxeer", "foxeer.com", "FPV cameras and drone electronics", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV cameras, antennas, flight controllers, and accessories."),
    ("GEPRC", "geprc.com", "FPV drone hardware", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV drone maker."),
    ("Gemfan", "gemfanhobby.com", "drone propellers", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Propellers for FPV and multirotor aircraft."),
    ("Gremsy", "gremsy.com", "drone payloads and camera gimbals", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Camera gimbals and visible, thermal, and inspection payloads."),
    ("HOTA", "hota-exp.com", "drone battery chargers and power systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Battery chargers and power supplies."),
    ("HQProp", "hqprop.com", "drone propellers", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV and multirotor propellers."),
    ("Hobbywing", "hobbywingdirect.com", "drone propulsion and ESCs", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Electronic speed controllers and propulsion electronics."),
    ("Holybro", "holybro.com", "drone autopilots and flight-control components", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Pixhawk autopilots, telemetry, GNSS, and development hardware."),
    ("ISDT", "isdt.co", "drone batteries and power systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Battery chargers and battery tools."),
    ("ImmersionRC", "immersionrc.com", "FPV drone electronics", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV systems and equipment."),
    ("Inspired Flight Technologies", "inspiredflight.com", "enterprise and defense UAS", "United States", "live", "business", "", "https://dronerules.world/manufacturers", "Blue UAS and NDAA-compliant medium- and heavy-lift aircraft."),
    ("Matek Systems", "mateksys.com", "drone autopilots and flight-control components", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Flight controllers, GPS modules, and power systems."),
    ("NextVision", "nextvision-sys.com", "drone payloads and imaging systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Stabilized EO/IR payloads for unmanned aircraft."),
    ("Potensic", "potensic.com", "consumer drones", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Consumer camera drones."),
    ("RadioMaster", "radiomasterrc.com", "drone radio-control systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "RC transmitters and receivers."),
    ("RunCam", "runcam.com", "FPV cameras and video systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "FPV and action cameras."),
    ("Ryze Tech", "ryzerobotics.com", "consumer and educational drones", "China", "live", "business_unit", "DJI", "https://dronerules.world/manufacturers", "Tello drone brand; catalog identifies it as a DJI-partnered subsidiary."),
    ("Sony", "pro.sony", "drone imaging components", "Japan", "live", "supplier", "", "https://dronerules.world/manufacturers", "Camera supplier whose products are integrated into aerial mapping systems."),
    ("SpeedyBee", "speedybee.com", "FPV flight controllers and electronics", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Flight controllers, ESC stacks, and configuration tools."),
    ("Swellpro", "swellpro.com", "marine and waterproof drones", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Waterproof drones for marine use."),
    ("T-Motor", "tmotor.com", "drone propulsion components", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Motors, ESCs, and propulsion systems."),
    ("Tattu", "genstattu.com", "drone batteries and power systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "LiPo and smart batteries for FPV and professional drones."),
    ("Walksnail", "walksnail.com", "FPV video systems", "unknown", "live", "business", "", "https://dronerules.world/manufacturers", "Digital FPV video systems and goggles."),
    ("uAvionix", "uavionix.com", "drone avionics and detect-and-avoid systems", "United States", "live", "business", "", "https://dronerules.world/manufacturers", "Avionics, detect-and-avoid, and Remote ID systems."),
]


def load_legacy_metadata():
    master = json.loads((ARCHIVE_MAKES / "manifest.json").read_text())
    by_name = {}
    for make in master.get("makes", []):
        slug = make.get("slug", "")
        manifest_path = ARCHIVE_MAKES / slug / "manifest.json"
        categories = set()
        if manifest_path.exists():
            doc = json.loads(manifest_path.read_text())
            categories = {m.get("category") for m in doc.get("models", []) if m.get("category")}
        by_name[make.get("name", "")] = (make.get("country", "unknown"), categories)
    return by_name


def main():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        old_rows = list(csv.DictReader(f))
    legacy = load_legacy_metadata()
    rows = []
    for old in old_rows:
        name = old["name"]
        if "industry" in old and "country_of_origin" in old and "status" in old:
            override = OVERRIDES.get(old["name"], {})
            rows.append({
                "name": name,
                "domain": old.get("domain") or "unknown",
                "industry": override.get("industry", old.get("industry") or "unknown"),
                "country_of_origin": override.get("country_of_origin", old.get("country_of_origin") or "unknown"),
                "status": old.get("status") if old.get("status") in {"live", "gone", "acquired", "unknown"} else "unknown",
                "entity_type": old.get("entity_type", "business"),
                "parent_or_acquirer": old.get("parent_or_acquirer", ""),
                "founded_year": old.get("founded_year", ""),
                "evidence_url": old.get("evidence_url", ""),
                "status_source": old.get("status_source", ""),
                "period_status": old.get("period_status", "unverified_legacy_candidate" if name in legacy else "verified_active_2016_onward"),
                "notes": old.get("notes", ""),
            })
            continue
        original_status = old.get("business_status", "")
        country, categories = legacy.get(name, ("unknown", set()))
        category_values = sorted(categories)
        industry = "; ".join(category_values) if category_values else "unknown"
        if country == "USA":
            country = "United States"
        # Preserve specific work types recorded in prior research notes.
        notes = old.get("notes", "")
        if name == "Dronecode":
            industry, country = "open-source drone software", "United States"
        elif name in {"Amazon Prime Air", "Wing", "Zipline", "Dronamics", "Matternet", "Manna"}:
            industry = "drone delivery and logistics"
        elif name in {"A2Z Drone Delivery", "Antwork", "Meituan", "Skye Air Mobility", "Speedbird Aero", "TechEagle", "UPS Flight Forward", "Swoop Aero", "Volansi"}:
            industry = "drone delivery and logistics"
        elif name in {"Autel Robotics", "DJI", "FIMI", "Holy Stone", "Hubsan", "Yuneec", "Walkera", "BetaFPV", "iFlight", "PowerVision"}:
            industry = "consumer and hobby drones"
        elif name in {"Skydio", "AeroVironment", "Baykar", "General Atomics Aeronautical", "Northrop Grumman", "Teledyne FLIR", "Quantum-Systems", "InsideFPV", "Rodella Technologies", "Briech UAS", "Skydagger Drones"}:
            industry = "military and defense UAS"
        status = STATUS.get(name, "unknown")
        parent = PARENTS.get(name, "")
        override = OVERRIDES.get(name, {})
        country = override.get("country_of_origin", country or "unknown")
        industry = override.get("industry", industry or "unknown")
        evidence = old.get("evidence_url", "") or ("https://" + old["domain"] if old.get("domain") and old["domain"] != "unknown" else "")
        detail = notes
        if original_status in {"active_delivery_inactive", "defunct_or_liquidated", "acquired_standalone_operations_ceased", "acquired_or_status_needs_review"}:
            detail = (detail + " ").strip() + f"Previous status note: {original_status}."
        rows.append({
            "name": name,
            "domain": old.get("domain") or "unknown",
            "industry": industry,
            "country_of_origin": country or "unknown",
            "status": status,
            "entity_type": old.get("entity_type", "business"),
            "parent_or_acquirer": parent,
            "founded_year": old.get("founded_year", ""),
            "evidence_url": evidence,
            "status_source": "" if status == "unknown" else evidence,
            "period_status": "unverified_legacy_candidate" if name in legacy else "verified_active_2016_onward",
            "notes": detail,
        })

    existing = {r["name"].casefold() for r in rows}
    for name, domain, industry, country, status, entity, parent, source, notes in EXTRA:
        if name.casefold() in existing:
            continue
        rows.append({
            "name": name,
            "domain": domain or "unknown",
            "industry": industry,
            "country_of_origin": country or "unknown",
            "status": status,
            "entity_type": entity,
            "parent_or_acquirer": parent,
            "founded_year": "",
            "evidence_url": "https://" + domain if domain and domain != "unknown" else source,
            "status_source": source,
            "period_status": "verified_active_2016_onward",
            "notes": notes,
        })
        existing.add(name.casefold())

    fields = ["name", "domain", "industry", "country_of_origin", "status", "entity_type", "parent_or_acquirer", "founded_year", "period_status", "evidence_url", "status_source", "notes"]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} unique organizations to {CSV_PATH}")


if __name__ == "__main__":
    main()
