# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times

# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for
# possible tz variables


import astral
import pyephem
import pandas


name = "Albury"
region = 'Australia'
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
elev = 160

# create the object we'll use to determine rise & set times
location = astral.Location((name, region, lat, lon, timezone, elev))

start_date = "01/01/2018"
end_date = "31/12/2018"
# list of dates in 2018
dates = pandas.date_range(start=start_date, end=end_date, timezone=location.timezone).tolist()
