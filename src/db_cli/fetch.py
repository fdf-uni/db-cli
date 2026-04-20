import uuid
from urllib.parse import urljoin
import urllib.request
from datetime import datetime, timezone, timedelta

API_BASE = "https://app.vendo.noncd.db.de/mob/"

DEFAULT_MAX_DISTANCE = 10000
DEFAULT_MAX_LOCATIONS = 50


def do_request(url: str, request: str, content_type: str) -> str:
    headers = {
        "X-Correlation-ID": str(uuid.uuid4()) + "_" + str(uuid.uuid4()),
        "Accept": content_type,
        "Content-Type": content_type,
    }

    data = request.encode("utf-8")
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req) as response:
        page = response.read()
    return page.decode()


def format_products(products: list | None) -> str:
    if products is not None:
        return '"' + '", "'.join(products) + '"'
    else:
        return '"ALL"'


def format_iso8601_with_offset(time: datetime) -> str:
    if time is not None:
        return time.strftime("%Y-%m-%dT%H:%M:%S%:z")
    else:
        return "null"


def format_location_types(types: list | None) -> str:
    if types is None or "ALL" in types:
        return '"ALL"'
    else:
        return '"' + '", "'.join(types) + '"'


def now(offset: float = 2) -> datetime:
    tzinfo = timezone(timedelta(hours=offset))
    d = datetime.now(tzinfo)
    return d


def nearby(
    longtitude: float,
    latitude: float,
    max_distance: int = DEFAULT_MAX_DISTANCE,
    max_locations: int = DEFAULT_MAX_LOCATIONS,
) -> str:
    url = urljoin(API_BASE, "location/nearby")
    request = (
        '{"area":{"coordinates":{"longitude":'
        + str(longtitude)
        + ',"latitude":'
        + str(latitude)
        + '},"radius":'
        + str(max_distance)
        + '},"maxResults":'
        + str(max_locations)
        + ',"products":["ALL"]}'
    )
    content_type = "application/x.db.vendo.mob.location.v3+json"
    return do_request(url, request, content_type)


def trips(
    start: str,
    end: str,
    time: datetime,
    dep: bool,
    via: str | None = None,
    products: list | None = None,
    bike: bool | None = False,
    context: str | None = None,
) -> str:
    deparr = "ABFAHRT" if dep else "ANKUNFT"
    products_str = '"verkehrsmittel":[' + format_products(products) + "]"
    via_locations = (
        '"viaLocations":[{"locationId": "' + via + '",' + products_str + "}],"
        if via
        else ""
    )
    bike_str = '"fahrradmitnahme":true,' if bike else ""
    ctx_str = '"context": "' + context + '",' if context else ""
    request = (
        '{"autonomeReservierung":false,"einstiegsTypList":["STANDARD"],"klasse":"KLASSE_2",'
        + '"reiseHin":{"wunsch":{"abgangsLocationId": "'
        + start
        + '",'
        + products_str
        + ","
        + via_locations
        + bike_str
        + ctx_str
        + '"zeitWunsch":{"reiseDatum":"'
        + format_iso8601_with_offset(time)
        + '","zeitPunktArt":"'
        + deparr
        + '"},'
        + '"zielLocationId": "'
        + end
        + '"}},'
        + '"reisendenProfil":{"reisende":[{"ermaessigungen":["KEINE_ERMAESSIGUNG KLASSENLOS"],"reisendenTyp":"ERWACHSENER"}]},'
        + '"reservierungsKontingenteVorhanden":false}'
    )
    url = urljoin(API_BASE, "angebote/fahrplan")
    content_type = "application/x.db.vendo.mob.verbindungssuche.v9+json"
    return do_request(url, request, content_type)


def locations(
    search_term: str,
    types: list | None = None,
    max_locations: int = DEFAULT_MAX_LOCATIONS,
) -> str:
    request = (
        '{"searchTerm": "'
        + search_term
        + '",'
        + '"locationTypes":['
        + format_location_types(types)
        + "],"
        + '"maxResults":'
        + str(max_locations)
        + "}"
    )
    url = urljoin(API_BASE, "location/search")
    content_type = "application/x.db.vendo.mob.location.v3+json"
    return do_request(url, request, content_type)


def departures(station: str, time: datetime = now()) -> str:
    request = (
        '{"anfragezeit": "'
        + time.strftime("%H:%M")
        + '",'
        + '"datum": "'
        + time.strftime("%Y-%m-%d")
        + '",'
        + '"ursprungsBahnhofId": "'
        + station
        + '",'
        + '"verkehrsmittel":["ALL"]}'
    )
    url = urljoin(API_BASE, "bahnhofstafel/abfahrt")
    content_type = "application/x.db.vendo.mob.bahnhofstafeln.v2+json"
    return do_request(url, request, content_type)
