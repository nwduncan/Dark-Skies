# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times

# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for
# possible tz variables


import ephem
import pandas
import time
from datetime import datetime
from datetime import timedelta
import pytz


name = "Albury"
# region = "Australia"
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
# elev = 160

start_date = "01/01/2018"
end_date = "31/12/2018"
# list of dates in 2018
# p_dates = pandas.date_range(start=start_date, end=end_date, timezone=timezone).tolist()

# each night should be attributed to a single date
# possibly change each day to the 24 hour period between noon?

def date_range(start_date=start_date, end_date=end_date):

    p_dates = pandas.date_range(start=start_date, end=end_date).tolist()
    dates = []

    for utc_date in p_dates:
        local = pytz.timezone(timezone)
        localtime = local.localize(utc_date.to_datetime())
        utc_offset = localtime.utcoffset()

        date_data = (utc_date, utc_offset)

        dates.append(date_data)

    return dates


def moon_phases(dates=date_range()):

    # define location parameters
    observer = ephem.Observer()
    observer.name = name
    observer.lat = str(lat)
    observer.lon = str(lon)
    # set the horizon to 18 degrees below 0 to simulate astronomical twilight
    # observer.horizon = "-18"

    for date in dates:

        observer.date = date[0]
        moon = ephem.Moon()
        event = observer.next_rising(moon, use_center=False)
        event_utc = ephem.Date(event)
        event_local = event_utc.datetime() + date[1]
        illum = int(round(moon.phase/5.0))
        phase = chr(219)*illum+chr(176)*(20-illum)
        day = date[0].strftime("%Y-%m-%d")
        diff = event_local-date[0]
        next_rising = event_local.strftime("%Y-%m-%d %H:%M:%S")+" +1" if diff.days == 1 else event_local.strftime("%Y-%m-%d %H:%M:%S")+"   "
        print "{} Next rising: {} {} {}%".format(day, next_rising, phase, int(round(moon.phase)))


def moon_transit(dates=date_range()):

    # define location parameters
    observer = ephem.Observer()
    observer.name = name
    observer.lat = str(lat)
    observer.lon = str(lon)

    dates_order = [ date[0].to_datetime() for date in dates ]
    transit = { date.to_datetime(): [utc_offset, []] for date, utc_offset in dates }

    observer = ephem.Observer()
    observer.name = name
    observer.lat = str(lat)
    observer.lon = str(lon)

    for d in dates_order:
        observer.date = d
        moon = ephem.Moon()

        # event type
        rising = observer.next_rising(moon, use_center=False)
        setting = observer.next_setting(moon, use_center=False)
        # utc time of event
        rising_utc = ephem.Date(rising)
        setting_utc = ephem.Date(setting)

        # local time of event (round minutes)
        # rising_local = rising_utc.datetime() + transit[d][0]
        # setting_local = setting_utc.datetime() + transit[d][0]
        rising_local = rising_utc.datetime() + transit[d][0]
        rising_local = datetime(rising_local.year, rising_local.month, rising_local.day, rising_local.hour, rising_local.minute)
        setting_local = setting_utc.datetime() + transit[d][0]
        setting_local = datetime(setting_local.year, setting_local.month, setting_local.day, setting_local.hour, setting_local.minute)
        # local date of event (used to find correct value in transit dict)
        rising_date = datetime(rising_local.year, rising_local.month, rising_local.day)
        setting_date = datetime(setting_local.year, setting_local.month, setting_local.day)

        if rising_date <= dates_order[-1] and [rising_local, 'rising'] not in transit[rising_date][1]:
            transit[rising_date][1].append([rising_local, 'rising'])

        if setting_date <= dates_order[-1] and [setting_local, 'setting'] not in transit[setting_date][1]:
            transit[setting_date][1].append([setting_local, 'setting'])

    for t in transit:
        transit[t][1].sort()

    # for d in dates_order:
    #     events = len(transit[d])
    #
    # up = chr(219)
    # dn = chr(176)

    return dates_order, transit

















#
