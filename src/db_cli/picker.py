import subprocess
import json

from . import fetch
from . import format


def pick(items: list[str]) -> int:
    input = []
    for i in range(len(items)):
        input.append(f"{i}\n" + items[i])
    result = subprocess.run(
        [
            "fzf",
            "--read0",
            "--ansi",
            "--delimiter",
            "\n",
            "--with-nth",
            "2..",
            "--accept-nth",
            "1",
            "--layout=reverse-list",
            "--gap",
        ],
        capture_output=True,
        text=True,
        input="\0".join(input),
    )
    try:
        return int(result.stdout)
    except ValueError:
        return -1


def pick_trip(
    trips: str,
    trip_list: list,
    params: dict,
    earlier_ctx: str | None = None,
    later_ctx: str | None = None,
) -> dict:
    items = [format.format_trip_short(t) for t in trip_list]
    items.insert(0, "Earlier connections")
    items.append("Later connections")
    result = pick(items)
    if earlier_ctx is None:
        earlier_ctx = json.loads(trips)["frueherContext"]
    if later_ctx is None:
        later_ctx = json.loads(trips)["spaeterContext"]
    if result == 0:
        # Load earlier results
        params["context"] = earlier_ctx
        trips_new = fetch.trips(**{k: v for k, v in params.items() if v is not None})
        trip_list_new = json.loads(trips_new)["verbindungen"] + trip_list
        earlier_ctx_new = json.loads(trips_new)["frueherContext"]
        return pick_trip(trips_new, trip_list_new, params, earlier_ctx_new, later_ctx)
    elif result > len(trip_list):
        # Load later results
        params["context"] = later_ctx
        trips_new = fetch.trips(**{k: v for k, v in params.items() if v is not None})
        trip_list_new = trip_list + json.loads(trips_new)["verbindungen"]
        later_ctx_new = json.loads(trips_new)["spaeterContext"]
        return pick_trip(trips_new, trip_list_new, params, earlier_ctx, later_ctx_new)
    else:
        return trip_list[abs(result) - 1]
