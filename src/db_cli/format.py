import re
import json
from datetime import datetime, timedelta


def cursive(text: str) -> str:
    return "\x1b[3m" + text + "\x1b[0m"


def color_text(text: str, color: str, background: bool = False) -> str:
    colors = ["grey", "red", "green", "yellow", "blue", "purple", "cyan"]
    result = f"\x1b[1;{colors.index(
        color) + 30 + 10 * background}m{text}\x1b[0m"
    if background:
        result = f"\x1b[1;30m{result}\x1b[0m"
    return result


def read_time(time: str) -> datetime:
    d = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")
    return d


def format_time(time1: datetime, time2: datetime | None) -> tuple[str, str]:
    if time2 is not None:
        color = "green" if (time2 - time1) < timedelta(minutes=5) else "red"
    else:
        time2 = time1
        color = "grey"
    return time1.strftime("%H:%M"), color_text(time2.strftime("%H:%M"), color)


def get_load(info: dict) -> str:
    for i in info:
        if i["klasse"] == "KLASSE_2":
            return i["stufe"]
    return "0"


def format_load(load: str) -> str | None:
    try:
        load_index = int(load)
    except ValueError:
        return None
    load_colors = ["grey", "green", "yellow", "red"]
    return color_text("", load_colors[load_index])


def color_section_text(text: str) -> str:
    if re.match(r"S\d+", text):
        color = "green"
    elif re.match(r"U\d+", text):
        color = "blue"
    elif re.match(r"STR", text):
        color = "red"
    elif re.match(r"R[BE]", text):
        color = "yellow"
    elif re.match(r"Bus", text):
        color = "cyan"
    else:
        return text

    return color_text(text, color)


def format_section(section: dict, plain: bool = False) -> str:
    if section["typ"] == "FUSSWEG":
        return ""
    else:
        result = f"{section["mitteltext"]} {section["richtung"]}"
        if not plain:
            result = color_section_text(result)
        return result


def get_connection_times_and_place(
    connection: dict, start: bool = True
) -> tuple[str, str, str]:
    if start:
        s_p = cursive(connection["abgangsOrt"]["name"])
        try:
            s_p += f" (Gleis {connection['halte'][0]['gleis']})"
        except (KeyError, IndexError):
            pass
        start_t = read_time(connection["abgangsDatum"])
        try:
            start_rt = read_time(connection["ezAbgangsDatum"])
        except KeyError:
            start_rt = None
        s_t, s_rt = format_time(start_t, start_rt)
        return s_p, s_t, s_rt
    else:
        e_p = cursive(connection["ankunftsOrt"]["name"])
        try:
            e_p += f" (Gleis {connection['halte'][-1]['gleis']})"
        except (KeyError, IndexError):
            pass
        end_t = read_time(connection["ankunftsDatum"])
        try:
            end_rt = read_time(connection["ezAnkunftsDatum"])
        except KeyError:
            end_rt = None
        e_t, e_rt = format_time(end_t, end_rt)
        return e_p, e_t, e_rt


def format_connection(
    s_p: str, s_t: str, s_rt: str, e_p: str, e_t: str, e_rt: str, load: str, routes: str
) -> str:
    result = f"{s_t} • {s_rt} {s_p}\n"
    result += 6 * " " + f"{format_load(load)}" + 7 * " " + routes + "\n"
    result += f"{e_t} • {e_rt} {e_p}\n"
    return result


def format_trip_short(trip: dict) -> str:
    t = trip["verbindung"]

    s_p, s_t, s_rt = get_connection_times_and_place(
        t["verbindungsAbschnitte"][0])

    e_p, e_t, e_rt = get_connection_times_and_place(
        t["verbindungsAbschnitte"][-1], start=False
    )

    routes = " ".join([format_section(s) for s in t["verbindungsAbschnitte"]])
    load = get_load(t["auslastungsInfos"])

    result = format_connection(s_p, s_t, s_rt, e_p, e_t, e_rt, load, routes)
    return result


def format_trip_long(trip: dict) -> str:
    t = trip["verbindung"]
    sections = t["verbindungsAbschnitte"]
    result = "\n"
    notes = {
        "Allgemein": [h["text"] for h in t["himNotizen"]]
        + [e["text"] for e in t["echtzeitNotizen"]]
    }
    for i in range(len(sections)):
        s_p, s_t, s_rt = get_connection_times_and_place(sections[i])
        e_p, e_t, e_rt = get_connection_times_and_place(
            sections[i], start=False)

        stop_count = len(sections[i]["halte"]) - 2
        routes = format_section(sections[i])
        if stop_count > 0:
            routes += f" ({stop_count} stops)"
        load = get_load(sections[i]["auslastungsInfos"])

        result += format_connection(s_p, s_t, s_rt,
                                    e_p, e_t, e_rt, load, routes)
        if i < len(sections) - 1:
            result += "─" * 13
        result += "\n"

        notes[format_section(sections[i], True)] = [h["text"] for h in sections[i]["himNotizen"]] + [
            e["text"] for e in sections[i]["echtzeitNotizen"]
        ]

    note_text = ""
    for k in notes.keys():
        if len(notes[k]) > 0:
            note_text += color_text(f"## {k}", "yellow") + "\n"
            for n in notes[k]:
                note_text += color_text("• ", "blue") + n + "\n"
    if len(note_text) > 0:
        result += color_text("# Notizen", "yellow") + "\n" + note_text + "\n"

    return result


def format_trips(trips: str, max_trips: int | None = None) -> str:
    trip_list = json.loads(trips)["verbindungen"]
    if max_trips is not None:
        trip_list = trip_list[0:max_trips]
    formatted_list = [format_trip_short(t) for t in trip_list]
    return "\n".join(formatted_list)


def format_departures(departures: str, max_departures: int | None = None) -> str:
    formatted_list = []
    for d in json.loads(departures)["bahnhofstafelAbfahrtPositionen"]:
        s_p = d["abfrageOrt"]["name"]
        try:
            s_p += f" (Gleis {d['gleis']})"
        except KeyError:
            pass
        start_t = read_time(d["abgangsDatum"])
        try:
            start_rt = read_time(d["ezAbgangsDatum"])
        except KeyError:
            start_rt = None
        s_t, s_rt = format_time(start_t, start_rt)
        formatted_list.append(
            f"{s_t} • {s_rt} {s_p}\n" + 14 * " " +
            color_section_text(d["mitteltext"])[0]
        )
    if max_departures is not None:
        formatted_list = formatted_list[0:max_departures]
    return "\n".join(formatted_list)
