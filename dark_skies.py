# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times

# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for
# possible tz variables


import ephem
import pandas
import time
from datetime import datetime
import pytz


name = "Albury"
# region = "Australia"
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
# elev = 160

start_date = "01/02/2018"
end_date = "31/12/2018"
# list of dates in 2018
# p_dates = pandas.date_range(start=start_date, end=end_date, timezone=timezone).tolist()
p_dates = pandas.date_range(start=start_date, end=end_date).tolist()
dates = []

for utc_date in p_dates:
    local = pytz.timezone(timezone)
    localtime = local.localize(utc_date.to_datetime())
    utc_offset = localtime.utcoffset()

    date_data = (utc_date, utc_offset)

    dates.append(date_data)


observer = ephem.Observer()
observer.name = name
observer.lat = str(lat)
observer.lon = str(lon)
# set the horizon to 18 degrees below 0 to simulate astronomical twilight
# observer.horizon = "-18"

for date in dates:

    observer.date = date[0]

    # event_dict = { 'sunset': [ephem.Sun, observer.next_setting],
    #               'sunrise': [ephem.Sun, observer.next_rising],
    #               'moonset': [ephem.Moon, observer.next_setting],
    #               'moonrise': [ephem.Moon, observer.next_rising] }

    # body = event_dict[event_type][0]()
    # utc_sunset_time = ephem.Date(event_dict[event_type][1](body))

    moon = ephem.Moon()
    event = observer.next_rising(moon, use_center=False)
    event_utc = ephem.Date(event)
    event_local = event_utc.datetime() + date[1]
    illum = int(round(moon.phase/5.0))
    phase = chr(219)*illum+chr(176)*(20-illum)
    print "Next rising: {} - {} {} {}%".format(date[0], event_local, phase, int(round(moon.phase)))
