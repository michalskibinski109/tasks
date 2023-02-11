from datetime import date
from logging import Logger

import requests


class ApiCommunicator:
    def __init__(
        self, logger: Logger, url: str = "https://api.open-meteo.com/v1/forecast"
    ) -> None:
        self.logger = logger
        self.url = url

    def get_temperature(self, lat: float, lng: float, date: date, timezone: str) -> str:
        params = {
            "latitude": lat,
            "longitude": lng,
            "start_date": date,
            "end_date": date,
            "timezone": timezone,
            "daily": "temperature_2m_max",
        }
        response = requests.get(url=self.url, params=params)
        if response.status_code != 200:
            msg = f"Request error: {response.json()}"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.debug(f"Response code from {self.url}: {response.status_code}")
        json_data = response.json()
        try:
            temperature = json_data["daily"]["temperature_2m_max"][0]
        except KeyError as e:
            msg = f"Incorrect response from API: {e}"
            self.logger.error(msg)
            raise ValueError(msg)
        return temperature
