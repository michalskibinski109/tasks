# description
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


## Help
To get help on the command line, run the following command:

```bash
main.py -h
```
## example usage
### input
```bash
main.py -d 2023-02-02 -l krakow
```
### output
```bash
11:02:03 :: DEBUG :: Connected to redis (model.py:42)
11:02:04 :: DEBUG :: Response code from https://api.open-meteo.com/v1/forecast: 200 (api_communicator.py:51)
11:02:04 :: DEBUG :: Saving to cache: krakow_2023-02-02 (model.py:89)
city: krakow
date: 2023-02-02
max_temperature: 3.6
min_temperature: 0.8
rain_sum: 4.4
max_wind_speed: 21.5
```
## Notes
1. If Redis is not running, caching will be automatically disabled.
2. Program is lacking tests, but it is easy to add them. (Just use mock to mock requests and redis)
