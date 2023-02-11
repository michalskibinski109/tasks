from datetime import date
from logging import Logger
from pathlib import Path

import pandas as pd
import redis  # for caching
import yaml
from api_communicator import ApiCommunicator, WeatherData
from redis.exceptions import AuthenticationError, ConnectionError


class Model:
    def __init__(self, logger: Logger, config_path: Path = Path("config.yaml")) -> None:
        """
        Summary:
            Class for storing and processing data from API. Uses redis for caching data.
        Args:
            logger: Logger object
            config_path: Path to config file
        Note:
            If redis is not available, caching is disabled.
        """
        self.logger = logger
        self.config = self.__load_config(config_path)
        self.redis_client = self.__set_redis_client()
        self.api_communicator = ApiCommunicator(
            logger=logger, url=self.config["api_url"]
        )

    def __load_config(self, file_path: Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config

    def __set_redis_client(self) -> redis.client.Redis | None:
        try:
            client = redis.Redis(  # should be stored in config file
                host=self.config["redis"]["host"],
                port=self.config["redis"]["port"],
                password=self.config["redis"]["password"],
                decode_responses=True,
            )
            if client.ping() is True:
                return client
        except (
            AuthenticationError,
            ConnectionError,
        ) as err:
            self.logger.warning(
                f"Failed to connect to redis. Make sure password is correct and redis is running"
                f"on {self.config['redis']['host']}:{self.config['redis']['port']}."
                f"Using cache disabled\n{err}"
            )
            return None

    def __save_to_file(self, file: str, weather_data: WeatherData) -> None:
        self.logger.debug(f"Saving data to file: {file}")
        df = pd.DataFrame(weather_data.dict(), index=[0])
        df.to_csv(file, index=False)

    def get_weather(self, date: date, location: str, file: str) -> None:
        """
        Summary:
            Get weather data from API or cache and save to file or print to console.
        Args:
            date (str): Date in format YYYY-MM-DD
            location (str): City name
            file (str): File path to save data to. If None, data will be printed to console.
        Returns:
            None
        Raises:
            ValueError: If API returns incorrect response
        """
        cache_key = f"{location}_{date}"
        if self.redis_client and self.redis_client.exists(cache_key):
            self.logger.debug(f"Fetched {cache_key} from cache")
            dict_data = self.redis_client.hgetall(cache_key)
            weather_data = WeatherData(**dict_data)
        else:
            weather_data = self.api_communicator.get_weather(
                city=location, date=date, timezone=self.config["timezone"]
            )
            if self.redis_client:
                self.logger.debug(f"Saving to cache: {cache_key}")
                self.redis_client.hmset(cache_key, weather_data.dict())
        if file:
            self.__save_to_file(file=file, weather_data=weather_data)
        else:
            print(weather_data)
