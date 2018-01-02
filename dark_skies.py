# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times

# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for
# possible tz variables


import astral
import pandas

a = astral.Astral()
a.solar_depression = 'civil'

start_date = "01/01/2018"
end_date = "31/12/2018"

name = "Albury"
region = 'Australia'
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
elev = 160

location = astral.Location((name, region, lat, lon, timezone, elev))

dates = pandas.date_range(start=start_date, end=end_date, timezone=location.timezone).tolist()
