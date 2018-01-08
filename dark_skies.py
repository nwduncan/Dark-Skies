# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times

# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for
# possible tz variables


import ephem
import pandas
import time
from datetime import datetime


name = "Albury"
region = "Australia"
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
elev = 160

start_date = "01/01/2018"
end_date = "31/12/2018"
# list of dates in 2018
dates = pandas.date_range(start=start_date, end=end_date, timezone=timezone).tolist()

observer = ephem.Observer()
observer.name = name
observer.lat = str(lat)
observer.lon = str(lon)
# set the horizon to 18 degrees below 0 to simulate astronomical twilight
# observer.horizon = "-18"

# pyephem uses UTC so we need to find our local offset
# this should take in to account daylight davings when calculating past & future dates
local_now = time.time()
utc_offset = datetime.fromtimestamp(local_now) - datetime.utcfromtimestamp(local_now)
for date in dates:
    observer.date = date

    # event_dict = { 'sunset': [ephem.Sun, observer.next_setting],
    #               'sunrise': [ephem.Sun, observer.next_rising],
    #               'moonset': [ephem.Moon, observer.next_setting],
    #               'moonrise': [ephem.Moon, observer.next_rising] }

    # body = event_dict[event_type][0]()
    # utc_sunset_time = ephem.Date(event_dict[event_type][1](body))

    moon = ephem.Moon()
    event = observer.next_rising(moon, use_center=True)
    event_utc = ephem.Date(event)
    event_local = event_utc.datetime() + utc_offset
    illum = int(moon.phase/10)
    phase = chr(219)*illum+chr(176)*(10-illum)
    print "Next rising: {} - {} {}".format(date, event_local, phase)


print event_local
print moon.phase
