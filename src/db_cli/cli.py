"""A simple CLI for getting public transport information from DB."""

import argparse
import dateutil.parser
import datetime
import re
import json
from . import fetch
from . import format
from . import picker
from . import data


def split_to_list(s: str | None) -> list | None:
    if s is None:
        return s
    return re.split(r"[;,\s]", s)


def parse_locations(response: str) -> list:
    locations = json.loads(response)
    keys = {"locationId", "locationType", "name"}
    cleaned_locations = []
    for loc in locations:
        cleaned_locations.append({k: loc[k] for k in keys})
    return cleaned_locations


def locations(args: argparse.Namespace) -> None:
    params = {
        "search_term": args.search_term,
        "types": split_to_list(args.types),
        "max_locations": args.max_locations,
    }
    locations = fetch.locations(**{k: v for k, v in params.items() if v is not None})
    if args.raw:
        print(locations)
    else:
        print([loc["name"] for loc in parse_locations(locations)])


def verify_location(loc: str | None) -> str | None:
    if loc is None:
        return loc
    elif loc.startswith("A="):
        return loc
    else:
        return parse_locations(fetch.locations(loc, max_locations=1))[0]["locationId"]


def verify_time(t) -> datetime.datetime:
    if type(t) is datetime.datetime:
        return t
    return dateutil.parser.parse(t)


def trips(args: argparse.Namespace) -> None:
    start = verify_location(args.start)
    end = verify_location(args.end)
    via = verify_location(args.via)

    t = verify_time(args.time)

    params = {
        "start": start,
        "end": end,
        "time": t,
        "dep": args.arrival_time,
        "via": via,
        "products": split_to_list(args.products),
        "bike": args.bike,
    }
    trips = fetch.trips(**{k: v for k, v in params.items() if v is not None})
    if args.raw:
        print(trips)
    elif args.interactive:
        trip = picker.pick_trip(trips, json.loads(trips)["verbindungen"], params)
        print(format.format_trip_long(trip), end="")
    else:
        print(format.format_trips(trips, args.max_trips))


def nearby(args: argparse.Namespace) -> None:
    params = {
        "longtitude": args.longtitude,
        "latitude": args.latitude,
        "max_distance": args.max_distance,
        "max_locations": args.max_locations,
    }
    locations = fetch.nearby(**{k: v for k, v in params.items() if v is not None})
    if args.raw:
        print(locations)
    else:
        print([loc["name"] for loc in parse_locations(locations)])


def departures(args: argparse.Namespace) -> None:
    station = verify_location(args.station)
    t = verify_time(args.time)
    if station is None:
        raise ValueError("`station` may not be `None` when querying for departures.")
    departures = fetch.departures(station, t)
    if args.raw:
        print(departures)
    else:
        print(format.format_departures(departures, args.max_departures))


def create_parser() -> argparse.ArgumentParser:
    epilog = "Have a good journey! :)"

    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.set_defaults(func=lambda x: parser.print_help())

    subparsers = parser.add_subparsers(help="Available subcommands")

    locations_parser = subparsers.add_parser(
        "locations",
        aliases=["l"],
        epilog="available location types:" + data.location_types(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Search for locations matching `search_term`.",
    )
    locations_parser.set_defaults(func=locations)
    locations_parser.add_argument(
        "search_term",
        action="store",
        help="The search term for the respective location.",
    )
    locations_parser.add_argument(
        "--types",
        action="store",
        help="The kind of locations to search for, separated by space, comma or semicolon. See below for all available choices.",
    )
    locations_parser.add_argument(
        "--max-locations",
        action="store",
        help="The maximum number of locations to search for.",
    )
    locations_parser.add_argument(
        "--raw",
        action="store_true",
        help="Whether to output the raw JSON response.",
    )

    trips_parser = subparsers.add_parser(
        "trips",
        aliases=["t"],
        epilog="available products:" + data.products(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Query available trips from `start` to `end`.",
    )
    trips_parser.set_defaults(func=trips)
    trips_parser.add_argument("start", action="store", help="The place of departure.")
    trips_parser.add_argument("end", action="store", help="The destination place.")
    trips_parser.add_argument(
        "--time",
        action="store",
        default=fetch.now(),
        help="Departure or arrival time (see also `--arival-time`).",
    )
    trips_parser.add_argument(
        "--arrival-time",
        action="store_false",
        help="Use the specified time as an arrival time instead of the departure time.",
    )
    trips_parser.add_argument(
        "--bike",
        action="store_true",
        help="Whether to require trips to allow bikes.",
    )
    trips_parser.add_argument(
        "--products",
        action="store",
        help="Which products to use for the trip, separated by space, comma or semicolon. See below for all available choices.",
    )
    trips_parser.add_argument("--via", action="store", default=None)
    trips_parser.add_argument(
        "--max-trips",
        action="store",
        default=None,
        type=int,
        help="Limit the number of trips to be shown (ignored in interactive mode).",
    )
    trips_parser.add_argument(
        "--raw",
        action="store_true",
        help="Whether to output the raw JSON response.",
    )
    trips_parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Whether to choose a trip interactively.",
    )

    nearby_parser = subparsers.add_parser(
        "nearby",
        description="Search for locations near to the specified location.",
    )
    nearby_parser.set_defaults(func=nearby)
    nearby_parser.add_argument("longtitude", action="store", type=float)
    nearby_parser.add_argument("latitude", action="store", type=float)
    nearby_parser.add_argument(
        "--max-distance",
        action="store",
        type=int,
        default=None,
        help="Only search for locations within this distance to the specified position (in meters).",
    )
    nearby_parser.add_argument(
        "--max-locations",
        action="store",
        type=int,
        default=None,
        help="Limit the number of locations to be shown.",
    )
    nearby_parser.add_argument(
        "--raw",
        action="store_true",
        help="Whether to output the raw JSON response.",
    )

    departures_parser = subparsers.add_parser(
        "departures",
        description="List departures from a single station.",
    )
    departures_parser.set_defaults(func=departures)
    departures_parser.add_argument(
        "station", action="store", help="The place of departure."
    )
    departures_parser.add_argument(
        "--time",
        action="store",
        default=fetch.now(),
        help="Specify another time than the current one.",
    )
    departures_parser.add_argument(
        "--raw",
        action="store_true",
        help="Whether to output the raw JSON response.",
    )
    departures_parser.add_argument(
        "--max-departures",
        action="store",
        type=int,
        default=None,
        help="Limit the number of departures to be shown.",
    )

    return parser
