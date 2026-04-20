"""db-cli -  A simple CLI for getting public transport information from DB."""


def main():
    from . import cli

    p = cli.create_parser()
    args = p.parse_args()
    args.func(args)
