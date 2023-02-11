from pydantic import BaseModel


class WeatherData(BaseModel):
    city: str = "Wroclaw"
    date: str = "2020-01-01"

    def __str__(self) -> str:
        return f"{self.city} \n{self.date}"


print(WeatherData())
