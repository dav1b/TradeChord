"""
Configuration settings for the World Bank Trade Data Pipeline.
"""

# API Configuration
WITS_BASE_URL = "https://wits.worldbank.org/API/V1"
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 0.1  # seconds between requests (reduced from 0.5)

# Data Collection Parameters
REPORTER = "IRL" # Use Ireland for testing
PARTNER = "wld"  # Use 'wld' for World
START_YEAR = 2002
END_YEAR = 2022
INDICATOR = "XPRT-TRD-VL"  # Export trade value

# Product codes for all sectors (from WITS API) - excluding "Total" as it's calculated
SECTOR_PRODUCTS = [
    "01-05_Animal",      # Animal
    "06-15_Vegetable",   # Vegetable
    "16-24_FoodProd",    # Food Products
    "25-26_Minerals",    # Minerals
    "27-27_Fuels",       # Fuels
    "28-38_Chemicals",   # Chemicals
    "39-40_PlastiRub",   # Plastic or Rubber
    "41-43_HidesSkin",   # Hides and Skins
    "44-49_Wood",        # Wood
    "50-63_TextCloth",   # Textiles and Clothing
    "64-67_Footwear",    # Footwear
    "68-71_StoneGlas",   # Stone and Glass
    "72-83_Metals",      # Metals
    "84-85_MachElec",    # Mach and Elec
    "86-89_Transport",   # Transportation
    "90-99_Miscellan",   # Miscellaneous
]

# Test countries for initial testing
TEST_COUNTRIES = ["IRL"]  # Ireland only for this test

# Top 50 exporters by trade volume (approximate ranking)
TOP_50_EXPORTERS = [
    "CHN",  # China
    "USA",  # United States
    "DEU",  # Germany
    "NLD",  # Netherlands
    "JPN",  # Japan
    "KOR",  # Korea, Rep.
    "HKG",  # Hong Kong, China
    "FRA",  # France
    "ITA",  # Italy
    "GBR",  # United Kingdom
    "CAN",  # Canada
    "MEX",  # Mexico
    "SGP",  # Singapore
    "RUS",  # Russian Federation
    "ESP",  # Spain
    "BEL",  # Belgium
    "CHE",  # Switzerland
    "TWN",  # Taiwan
    "IND",  # India
    "BRA",  # Brazil
    "AUS",  # Australia
    "THA",  # Thailand
    "POL",  # Poland
    "AUT",  # Austria
    "SWE",  # Sweden
    "CZE",  # Czech Republic
    "TUR",  # Turkey
    "HUN",  # Hungary
    "DNK",  # Denmark
    "NOR",  # Norway
    "IRL",  # Ireland
    "MYS",  # Malaysia
    "IDN",  # Indonesia
    "FIN",  # Finland
    "SAU",  # Saudi Arabia
    "ARE",  # United Arab Emirates
    "PHL",  # Philippines
    "CHL",  # Chile
    "ZAF",  # South Africa
    "ISR",  # Israel
    "ROU",  # Romania
    "BGR",  # Bulgaria
    "HRV",  # Croatia
    "SVK",  # Slovak Republic
    "SVN",  # Slovenia
    "LTU",  # Lithuania
    "LVA",  # Latvia
    "EST",  # Estonia
    "LUX",  # Luxembourg
    "CYP",  # Cyprus
    "MLT",  # Malta
]

# Top 50 importers by trade volume (approximate ranking)
TOP_50_IMPORTERS = [
    "USA",  # United States
    "CHN",  # China
    "DEU",  # Germany
    "NLD",  # Netherlands
    "GBR",  # United Kingdom
    "FRA",  # France
    "JPN",  # Japan
    "ITA",  # Italy
    "HKG",  # Hong Kong, China
    "KOR",  # Korea, Rep.
    "CAN",  # Canada
    "ESP",  # Spain
    "BEL",  # Belgium
    "MEX",  # Mexico
    "SGP",  # Singapore
    "IND",  # India
    "CHE",  # Switzerland
    "AUS",  # Australia
    "BRA",  # Brazil
    "RUS",  # Russian Federation
    "TWN",  # Taiwan
    "THA",  # Thailand
    "TUR",  # Turkey
    "POL",  # Poland
    "AUT",  # Austria
    "SWE",  # Sweden
    "CZE",  # Czech Republic
    "HUN",  # Hungary
    "DNK",  # Denmark
    "NOR",  # Norway
    "IRL",  # Ireland
    "MYS",  # Malaysia
    "IDN",  # Indonesia
    "FIN",  # Finland
    "SAU",  # Saudi Arabia
    "ARE",  # United Arab Emirates
    "PHL",  # Philippines
    "CHL",  # Chile
    "ZAF",  # South Africa
    "ISR",  # Israel
    "ROU",  # Romania
    "BGR",  # Bulgaria
    "HRV",  # Croatia
    "SVK",  # Slovak Republic
    "SVN",  # Slovenia
    "LTU",  # Lithuania
    "LVA",  # Latvia
    "EST",  # Estonia
    "LUX",  # Luxembourg
    "CYP",  # Cyprus
    "MLT",  # Malta
]

# Individual country partners (from WITS API)
INDIVIDUAL_PARTNERS = [
    "AFG",  # Afghanistan
    "ALB",  # Albania
    "DZA",  # Algeria
    "ASM",  # American Samoa
    "AND",  # Andorra
    "AGO",  # Angola
    "AIA",  # Anguila
    "ATA",  # Antarctica
    "ATG",  # Antigua and Barbuda
    "ARG",  # Argentina
    "ARM",  # Armenia
    "ABW",  # Aruba
    "AUS",  # Australia
    "AUT",  # Austria
    "AZE",  # Azerbaijan
    "BHS",  # Bahamas, The
    "BHR",  # Bahrain
    "BGD",  # Bangladesh
    "BRB",  # Barbados
    "BLR",  # Belarus
    "BEL",  # Belgium
    "BLX",  # Belgium-Luxembourg
    "BLZ",  # Belize
    "BEN",  # Benin
    "BMU",  # Bermuda
    "BTN",  # Bhutan
    "BOL",  # Bolivia
    "BES",  # Bonaire
    "BIH",  # Bosnia and Herzegovina
    "BWA",  # Botswana
    "BVT",  # Bouvet Island
    "BAT",  # Br. Antr. Terr
    "BRA",  # Brazil
    "IOT",  # British Indian Ocean Ter.
    "VGB",  # British Virgin Islands
    "BRN",  # Brunei
    "BGR",  # Bulgaria
    "BUN",  # Bunkers
    "BFA",  # Burkina Faso
    "BDI",  # Burundi
    "KHM",  # Cambodia
    "CMR",  # Cameroon
    "CAN",  # Canada
    "CPV",  # Cape Verde
    "CYM",  # Cayman Islands
    "CAF",  # Central African Republic
    "TCD",  # Chad
    "CHL",  # Chile
    "CHN",  # China
    "CXR",  # Christmas Island
    "CCK",  # Cocos (Keeling) Islands
    "COL",  # Colombia
    "COM",  # Comoros
    "ZAR",  # Congo, Dem. Rep.
    "COG",  # Congo, Rep.
    "COK",  # Cook Islands
    "CRI",  # Costa Rica
    "CIV",  # Cote d'Ivoire
    "HRV",  # Croatia
    "CUB",  # Cuba
    "CUW",  # Curaçao
    "CYP",  # Cyprus
    "CZE",  # Czech Republic
    "CSK",  # Czechoslovakia
    "DNK",  # Denmark
    "DJI",  # Djibouti
    "DMA",  # Dominica
    "DOM",  # Dominican Republic
    "EAS",  # East Asia & Pacific
    "TMP",  # East Timor
    "ECU",  # Ecuador
    "EGY",  # Egypt, Arab Rep.
    "SLV",  # El Salvador
    "GNQ",  # Equatorial Guinea
    "ERI",  # Eritrea
    "EST",  # Estonia
    "SWZ",  # Eswatini
    "ETH",  # Ethiopia(excludes Eritrea)
    "ETF",  # Ethiopia(includes Eritrea)
    "ECS",  # Europe & Central Asia
    "FRO",  # Faeroe Islands
    "FLK",  # Falkland Island
    "FJI",  # Fiji
    "FIN",  # Finland
    "SDN",  # Fm Sudan
    "ATF",  # Fr. So. Ant. Tr
    "FRA",  # France
    "FRE",  # Free Zones
    "GUF",  # French Guiana
    "PYF",  # French Polynesia
    "GAB",  # Gabon
    "GMB",  # Gambia, The
    "GEO",  # Georgia
    "DDR",  # German Democratic Republic
    "DEU",  # Germany
    "GHA",  # Ghana
    "GIB",  # Gibraltar
    "GRC",  # Greece
    "GRL",  # Greenland
    "GRD",  # Grenada
    "GLP",  # Guadeloupe
    "GUM",  # Guam
    "GTM",  # Guatemala
    "GIN",  # Guinea
    "GNB",  # Guinea-Bissau
    "GUY",  # Guyana
    "HTI",  # Haiti
    "HMD",  # Heard Island and McDonald Isla
    "VAT",  # Holy See
    "HND",  # Honduras
    "HKG",  # Hong Kong, China
    "HUN",  # Hungary
    "ISL",  # Iceland
    "IND",  # India
    "IDN",  # Indonesia
    "IRN",  # Iran, Islamic Rep.
    "IRQ",  # Iraq
    "IRL",  # Ireland
    "ISR",  # Israel
    "ITA",  # Italy
    "JAM",  # Jamaica
    "JPN",  # Japan
    "JOR",  # Jordan
    "KAZ",  # Kazakhstan
    "KEN",  # Kenya
    "KIR",  # Kiribati
    "PRK",  # Korea, Dem. Rep.
    "KOR",  # Korea, Rep.
    "KWT",  # Kuwait
    "KGZ",  # Kyrgyz Republic
    "LAO",  # Lao PDR
    "LCN",  # Latin America & Caribbean
    "LVA",  # Latvia
    "LBN",  # Lebanon
    "LSO",  # Lesotho
    "LBR",  # Liberia
    "LBY",  # Libya
    "LTU",  # Lithuania
    "LUX",  # Luxembourg
    "MAC",  # Macao
    "MDG",  # Madagascar
    "MWI",  # Malawi
    "MYS",  # Malaysia
    "MDV",  # Maldives
    "MLI",  # Mali
    "MLT",  # Malta
    "MHL",  # Marshall Islands
    "MTQ",  # Martinique
    "MRT",  # Mauritania
    "MUS",  # Mauritius
    "MYT",  # Mayotte
    "MEX",  # Mexico
    "FSM",  # Micronesia, Fed. Sts.
    "MEA",  # Middle East & North Africa
    "MDA",  # Moldova
    "MCO",  # Monaco
    "MNG",  # Mongolia
    "MNT",  # Montenegro
    "MSR",  # Montserrat
    "MAR",  # Morocco
    "MOZ",  # Mozambique
    "MMR",  # Myanmar
    "NAM",  # Namibia
    "NRU",  # Nauru
    "NPL",  # Nepal
    "NLD",  # Netherlands
    "ANT",  # Netherlands Antilles
    "NZE",  # Neutral Zone
    "NCL",  # New Caledonia
    "NZL",  # New Zealand
    "NIC",  # Nicaragua
    "NER",  # Niger
    "NGA",  # Nigeria
    "NIU",  # Niue
    "NFK",  # Norfolk Island
    "NAC",  # North America
    "MKD",  # North Macedonia
    "MNP",  # Northern Mariana Islands
    "NOR",  # Norway
    "999",  # Not Applicable
    "PSE",  # Occ.Pal.Terr
    "OMN",  # Oman
    "OAS",  # Other Asia, nes
    "PCE",  # Pacific Islands
    "PAK",  # Pakistan
    "PLW",  # Palau
    "PAN",  # Panama
    "PNG",  # Papua New Guinea
    "PRY",  # Paraguay
    "PER",  # Peru
    "PHL",  # Philippines
    "PCN",  # Pitcairn
    "POL",  # Poland
    "PRT",  # Portugal
    "QAT",  # Qatar
    "REU",  # Reunion
    "ROM",  # Romania
    "RUS",  # Russian Federation
    "RWA",  # Rwanda
    "BLM",  # Saint Barthélemy
    "SHN",  # Saint Helena
    "SXM",  # Saint Maarten (Dutch part)
    "SPM",  # Saint Pierre and Miquelon
    "WSM",  # Samoa
    "SMR",  # San Marino
    "STP",  # Sao Tome and Principe
    "SAU",  # Saudi Arabia
    "SEN",  # Senegal
    "SER",  # Serbia, FR(Serbia/Montenegro)
    "SYC",  # Seychelles
    "SLE",  # Sierra Leone
    "SGP",  # Singapore
    "SVK",  # Slovak Republic
    "SVN",  # Slovenia
    "SLB",  # Solomon Islands
    "SOM",  # Somalia
    "ZAF",  # South Africa
    "SAS",  # South Asia
    "SGS",  # South Georgia and the South Sa
    "SSD",  # South Sudan
    "SVU",  # Soviet Union
    "ESP",  # Spain
    "SPE",  # Special Categories
    "LKA",  # Sri Lanka
    "KNA",  # St. Kitts and Nevis
    "LCA",  # St. Lucia
    "VCT",  # St. Vincent and the Grenadines
    "SSF",  # Sub-Saharan Africa
    "SUD",  # Sudan
    "SUR",  # Suriname
    "SWE",  # Sweden
    "CHE",  # Switzerland
    "SYR",  # Syrian Arab Republic
    "TJK",  # Tajikistan
    "TZA",  # Tanzania
    "THA",  # Thailand
    "TGO",  # Togo
    "TKL",  # Tokelau
    "TON",  # Tonga
    "TTO",  # Trinidad and Tobago
    "TUN",  # Tunisia
    "TUR",  # Turkey
    "TKM",  # Turkmenistan
    "TCA",  # Turks and Caicos Isl.
    "TUV",  # Tuvalu
    "UGA",  # Uganda
    "UKR",  # Ukraine
    "ARE",  # United Arab Emirates
    "GBR",  # United Kingdom
    "USA",  # United States
    "UMI",  # United States Minor Outlying I
    "UNS",  # Unspecified
    "URY",  # Uruguay
    "USP",  # Us Msc.Pac.I
    "UZB",  # Uzbekistan
    "VUT",  # Vanuatu
    "VEN",  # Venezuela
    "VNM",  # Vietnam
    "WLF",  # Wallis and Futura Isl.
    "ESH",  # Western Sahara
    "YEM",  # Yemen
    "YDR",  # Yemen Democratic
    "YUG",  # Yugoslavia,FR(Serbia/Montenegr
    "ZMB",  # Zambia
    "ZWE",  # Zimbabwe
]

# Default product (for backward compatibility)
PRODUCT = "Total"

# WITS partner-code corrections. The TOP_50 lists carry a few codes WITS does not
# recognize as partners (they 404). Verified against the live API (2026-07):
#   ROU -> ROM  (Romania)
#   TWN -> OAS  (Taiwan, reported as "Other Asia, nes")
# Applied only to the partner universe, not to reporters.
WITS_PARTNER_CODE_FIXES = {
    "ROU": "ROM",
    "TWN": "OAS",
}

# Output Configuration
OUTPUT_DIR = "data"
OUTPUT_FILENAME_TEMPLATE = "trade_exports_{reporter}_to_{partner}_{product}_{start_year}-{end_year}.csv"

# Available Indicators (for reference)
INDICATORS = {
    "XPRT-TRD-VL": "Export trade value",
    "MPRT-TRD-VL": "Import trade value",
    "XPRT-TRD-WG": "Export trade weight",
    "MPRT-TRD-WG": "Import trade weight",
}

# Available Years (typical range for WITS data)
MIN_YEAR = 1988
MAX_YEAR = 2023 

# -----------------------------------------------------------------------------
# Optimization knobs (collection strategy)
# -----------------------------------------------------------------------------
# Limit number of bilateral partners per reporter after pruning (None = unlimited)
TOP_K_PARTNERS = None

# Year to target for single-year optimized builds (falls back to START/END)
SINGLE_YEAR = 2021

# Concurrency and rate limiting
# Global target max requests per second; actual concurrency will adapt to avoid 429s
MAX_REQS_PER_SEC = 4
# Number of concurrent workers (network-bound); keep moderate to respect service
CONCURRENCY = 8

# Enable lightweight on-disk caching of raw responses and parsed zero-results
USE_CACHE = True
# Cache directory (created if missing)
CACHE_DIR = "data/.cache"

# Checkpoint manifest path to resume runs safely
CHECKPOINT_PATH = "data/.checkpoint_optimized.jsonl"

# Enable/disable API batching attempts (probe will auto-detect per run)
ALLOW_PARTNER_ALL = True
ALLOW_PRODUCT_ALL = True

# Coverage-based collection
# Target fraction of each product's WLD total to capture via explicit partner pulls
COVERAGE_TARGET = 0.90
# Add synthetic ROW remainder rows to reconcile to WLD total per product
INCLUDE_ROW_REMAINDER = True
# When testing, expand partner universe to all known partners instead of top-50
EXPAND_ALL_PARTNERS_FOR_TEST = True