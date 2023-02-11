## Help
To get help on the command line, run the following command:

```bash
main.py -h
```
## example usage
### input
```bash
main.py -d 2023-01-01
```
### output
```bash
City: Wroclaw
date: 2023-01-01
temperature: 16.2 Celsius
```
## Notes
1. If Redis is not running, caching will be automatically disabled.
2. Program is lacking tests, but it is easy to add them. (Just use mock to mock requests and redis)