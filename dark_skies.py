# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times

# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for
# possible tz variables


import ephem
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


def event(event_type, lat, lon):

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)

    local_now = time.time()
    utc_offset = datetime.fromtimestamp(local_now) - datetime.utcfromtimestamp(local_now)

    event_dict = { 'sunset': [ephem.Sun, observer.next_setting],
                  'sunrise': [ephem.Sun, observer.next_rising],
                  'moonset': [ephem.Moon, observer.next_setting],
                  'moonrise': [ephem.Moon, observer.next_rising] }

    body = event_dict[event_type][0]()
    utc_sunset_time = ephem.Date(event_dict[event_type][1](body))

    event_time = utc_sunset_time.datetime() + utc_offset
    # print "Today the sun will set @ {}".format(datetime.strftime(now, "%Y/%m/%d %H:%M:%S"))
    return event_time
