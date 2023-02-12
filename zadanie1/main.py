import argparse
from datetime import date

from miskibin import (
    get_logger,
)  # library created by me that simplifies configuration of logger. Also provides colored logs
from model import Model
from pathlib import Path


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
        type=Path,
        default=None,
        help="File to save weather forecast Eg. weather_data.csv",
    )
    return parser


if __name__ == "__main__":
    arg_parser = _get_parser()
    model = Model(
        logger=get_logger(
            lvl="DEBUG",
            format=f"%(asctime)-9s:: %(levelname)-6s:: %(message)s (%(filename)s:%(lineno)d)",
        )
    )
    try:
        args = arg_parser.parse_args()
    except SystemExit as err:
        arg_parser.print_help()
        raise err
    model.get_weather(date=args.date, location=args.location, file_path=args.file)
