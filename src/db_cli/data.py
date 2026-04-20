PRODUCTS = [
    "HOCHGESCHWINDIGKEITSZUEGE",
    "INTERCITYUNDEUROCITYZUEGE",
    "INTERREGIOUNDSCHNELLZUEGE",
    "NAHVERKEHRSONSTIGEZUEGE",
    "SBAHNEN",
    "BUSSE",
    "SCHIFFE",
    "UBAHN",
    "STRASSENBAHN",
    "ANRUFPFLICHTIGEVERKEHRE",
]

LOCATION_TYPES = {
    "ALL": "all",
    "ST": "stations",
    "POI": "points of interest",
    "ADR": "addresses",
}


def products() -> str:
    return "\n  " + "\n  ".join(PRODUCTS)


def location_types() -> str:
    location_type_list = [f"{k} ({LOCATION_TYPES[k]})" for k in LOCATION_TYPES]
    return "\n  " + "\n  ".join(location_type_list)
