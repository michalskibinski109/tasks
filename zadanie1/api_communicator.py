from datetime import date
from logging import Logger

import geocoder
import requests
from pydantic import BaseModel


class WeatherData(BaseModel):
    """
    Class for storing weather data
    """

    city: str
    date: str
    max_temperature: float
    min_temperature: float
    rain_sum: float
    max_wind_speed: float

    def __str__(self) -> str:
        data = "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        return data


class ApiCommunicator:
    def __init__(self, logger: Logger, url: str) -> None:
        self.logger = logger
        self.url = url

    def get_weather(self, city: str, date: date, timezone: str) -> WeatherData:
        lat, lng = self.__get_coordinates(city)
        params = {
            "latitude": lat,
            "longitude": lng,
            "start_date": date,
            "end_date": date,
            "timezone": timezone,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "rain_sum",
                "windspeed_10m_max",
            ],
        }
        response = requests.get(url=self.url, params=params)
        if response.status_code != 200:
            msg = f"Request error: {response.json()}"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.debug(f"Response code from {self.url}: {response.status_code}")
        weather_data = self.__parse_response(response.json(), city, date)
        return weather_data

    def __parse_response(self, json_data: dict, city: str, date: date) -> WeatherData:
        try:
            max_temperature = json_data["daily"]["temperature_2m_max"][0]
            min_temperature = json_data["daily"]["temperature_2m_min"][0]
            rain_sum = json_data["daily"]["rain_sum"][0]
            max_wind_speed = json_data["daily"]["windspeed_10m_max"][0]
        except KeyError as err:
            msg = f"Incorrect response from API: {err}"
            self.logger.error(msg)
            raise err

        return WeatherData(
            city=city,
            date=str(date),
            max_temperature=max_temperature,
            min_temperature=min_temperature,
            rain_sum=rain_sum,
            max_wind_speed=max_wind_speed,
        )

    def __get_coordinates(self, city: str) -> tuple:
        g = geocoder.osm(city)
        if not g.ok:
            msg = f'Coordinates for city "{city}" not found. Msg returned: {g.status}'
            self.logger.error(msg)
            raise ValueError(msg)
        lat, lng = g.json["lat"], g.json["lng"]
        return lat, lng
