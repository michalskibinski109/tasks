import argparse
from datetime import date

from miskibin import get_logger

from model import Model


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Weather forecast")
    parser.add_argument(
        "-l",
        "--location",
        type=str,
        default="Wroclaw",
        help="City Location for weather forecast Eg. Wroclaw",
    )
    parser.add_argument(
        "-d",
        "--date",
        type=date.fromisoformat,
        default=date.today(),
        help="Date for weather forecast. (yyyy-mm-dd)  Eg. 2020-01-01",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default=None,
        help="File to save weather forecast Eg. weather_data.csv",
    )
    return parser


if __name__ == "__main__":
    logger = get_logger(lvl="DEBUG")  # Logger from my own library
    parser = _get_parser()
    model = Model(logger=logger)
    try:
        args = parser.parse_args()
    except SystemExit as e:
        parser.print_help()
        exit(e.code)
    model.get_weather(date=args.date, location=args.location, file=args.file)
