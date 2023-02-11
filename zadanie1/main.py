"""
Proszę napisać w Pythonie 3.x działający w konsoli skrypt, 
który dla określonej parametrami wejściowymi lokalizacji 
(domyślnie: Wrocław) oraz daty (domyślnie: aktualny dzień)
pobierze z jednego z ogólnodostępnych API pogodowych dane odnośnie 
temperatury powietrza oraz opadów. Dla optymalizacji pod kątem zmniejszenia 
liczby requestów warto wykorzystać np. bazę danych jako pamięć podręczną (cache) skryptu.
W przypadku braku lub wprowadzenia nieprawidłowych parametrów skrypt powinien informować,
w jaki sposób użyć go poprawnie. Jeżeli parametry są prawidłowe, 
to efektem działania programu powinno być wypisanie wspomnianych
danych pogodowych w czytelnej formie na standardowe wyjście,
chyba że wprowadzono w parametrze nazwę pliku docelowego -
w takim wypadku należy zapisać te dane w tym pliku w formacie CSV.
"""
import argparse
from datetime import date

from miskibin import get_logger
from pydantic import BaseModel

from model import Model


class InputArgs(BaseModel):
    location: str
    date: date
    file: str


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
        args = parser.parse_args(namespace=InputArgs)
    except SystemExit as e:
        parser.print_help()
        exit(e.code)
    model.get_weather(date=args.date, location=args.location, file=args.file)
