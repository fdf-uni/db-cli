# DB CLI

A simple CLI to query the API of Deutsche Bahn (DB) for trips, locations, nearby stations and departures.
If one has `fzf` installed, one can also run some subcommands with an interactive menu.

Please note that I wrote most of this program impulsively on a day (alas without any AI assistance) because other solutions didn't fit my requirements.
As such, the code quality might not be the best; but if it works, it works. ;)

## Acknowledgments

The CLI was developed with [schildbach/public-transport-enabler](https://github.com/schildbach/public-transport-enabler) as an occasional reference regarding the API endpoints to use as well as the request and response formats (see [DbProvider.java](https://github.com/schildbach/public-transport-enabler/blob/master/src/de/schildbach/pte/DbProvider.java)).
Thanks a lot to the maintainers of that library for their work! :)

## Usage

```
usage: db-cli [-h] {locations,l,trips,t,nearby,departures} ...

A simple CLI for getting public transport information from DB.

positional arguments:
  {locations,l,trips,t,nearby,departures}
                        Available subcommands

options:
  -h, --help            show this help message and exit

Have a good journey! :)
```

Use `db-cli $subcommand -h` to get more information on a subcommand.
You may also want to use a short script like the following in order to quickly query trips between locations that you regularly travel to and from, e.g. on your daily commute:

```sh
#!/usr/bin/env sh

start="$(echo -e "start1\nstart2\nstart3" | fzf)"
end="$(echo -e "end1\nend2\nend3" | fzf)"

db-cli t -i "$start" "$end"
```
