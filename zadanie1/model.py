from logging import Logger
import redis  # for caching
import geocoder
import pandas as pd
from redis.exceptions import ConnectionError, AuthenticationError
from api_communicator import ApiCommunicator, WeatherData
import yaml
from pathlib import Path


class Model:
    def __init__(self, logger: Logger, config_path: str = Path("config.yaml")) -> None:
        self.logger = logger
        self.config = self.__load_config(config_path)
        self.redis_client = self.__set_redis_client()
        self.api_communicator = ApiCommunicator(
            logger=logger, url=self.config["api_url"]
        )

    def __load_config(self, file_path: str) -> dict:
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def __set_redis_client(self) -> redis.client.Redis:
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
        ) as e:
            self.logger.warning(
                f"Failed to connect to redis. Make sure password is correct and redis is running"
                f"on {self.config['redis']['host']}:{self.config['redis']['port']}. Using cache disabled\n{e}"
            )
            return None

    def __save_to_file(self, file: str, weather_data: WeatherData) -> None:
        self.logger.debug(f"Saving data to file: {file}")
        df = pd.DataFrame(weather_data.dict(), index=[0])
        df.to_csv(file, index=False)

    def get_weather(self, date: str, location: str, file: str) -> None:
        cache_key = f"{location}_{date}"
        if self.redis_client and self.redis_client.exists(cache_key):
            self.logger.debug(f"Fetched from cache: {cache_key}")
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
            print(weather_data.json(indent=4))
