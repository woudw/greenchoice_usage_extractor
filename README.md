# Extractor for usage data from Greenchoice

I really hate the fact that it is not possible to get the data from Greenchoice
(dutch energy firm) in a format ready for analysis (e.g. CSV, Json). That's why 
I wrote this thing.


## Usage
```python
# Set your credentials
username = "my_username"
password = "my_password"

# Set the period you want the data from
year = 2022
month = 1

with GreenchoiceAPI(username, password) as api:
    data = api.get_wind_productie_request(year, month)
    # From here you can do whatever you want with the data
```

## Todo
For now this can only export 'wind productie'. Usage needs to be added and the costs.
- Get usage of electricity in day and hourly;
- Get costs.

In ```docs/analysis.txt``` some example post-request bodies are stored.