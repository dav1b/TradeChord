"""Display metadata for the reporter universe."""

COUNTRY_NAMES: dict[str, str] = {
    "ARE": "United Arab Emirates",
    "AUS": "Australia",
    "AUT": "Austria",
    "BEL": "Belgium",
    "BRA": "Brazil",
    "CAN": "Canada",
    "CHE": "Switzerland",
    "CHN": "China",
    "CZE": "Czechia",
    "DEU": "Germany",
    "ESP": "Spain",
    "FRA": "France",
    "GBR": "United Kingdom",
    "HKG": "Hong Kong",
    "IDN": "Indonesia",
    "IND": "India",
    "IRL": "Ireland",
    "ITA": "Italy",
    "JPN": "Japan",
    "KOR": "South Korea",
    "MEX": "Mexico",
    "MYS": "Malaysia",
    "NLD": "Netherlands",
    "NOR": "Norway",
    "POL": "Poland",
    "SAU": "Saudi Arabia",
    "SGP": "Singapore",
    "THA": "Thailand",
    "TUR": "Türkiye",
    "USA": "United States",
}


def country_name(code: str) -> str:
    return COUNTRY_NAMES.get(code, code)
