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

# start_date = "01/01/2018"
# end_date = "31/12/2018"
# # list of dates in 2018
# dates = pandas.date_range(start=start_date, end=end_date, timezone=location.timezone).tolist()

observer = ephem.Observer()
observer.lat = str(lat)
observer.lon = str(lon)

# pyephem uses UTC so we need to find our local offset
# this should take in to account daylight davings when calculating past & future dates
local_now = time.time()
utc_offset = datetime.fromtimestamp(local_now) - datetime.utcfromtimestamp(local_now)

# event_dict = { 'sunset': [ephem.Sun, observer.next_setting],
#               'sunrise': [ephem.Sun, observer.next_rising],
#               'moonset': [ephem.Moon, observer.next_setting],
#               'moonrise': [ephem.Moon, observer.next_rising] }

# body = event_dict[event_type][0]()
# utc_sunset_time = ephem.Date(event_dict[event_type][1](body))

moon = ephem.Moon()
event = observer.next_rising(moon)
event_utc = ephem.Date(event)
event_local = event_utc.datetime() + utc_offset

print event_local
