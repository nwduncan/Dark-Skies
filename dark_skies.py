# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times



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
observer = ephem.Observer()
observer.name = name
observer.lat = str(lat)
observer.lon = str(lon)
start_date = datetime(2018,8,1)
end_date = datetime(2018,8,31)
# list of dates in 2018
# p_dates = pandas.date_range(start=start_date, end=end_date, timezone=timezone).tolist()

# each night should be attributed to a single date
# possibly change each day to the 24 hour period between noon?

def date_range(start_date=start_date, end_date=end_date, time_adjust=0):

    p_dates = pandas.date_range(start=start_date, end=end_date).tolist()
    dates = []

    for utc_date in p_dates:
        utc_date = utc_date.to_pydatetime()
        local = pytz.timezone(timezone)
        localtime = local.localize(utc_date)
        utc_offset = localtime.utcoffset()
        adjusted_time = utc_date + time_adjust
        date_data = (adjusted_time, utc_offset)
        dates.append(date_data)

    return dates


def moon_phases(dates):

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


def transit(bodies=[ephem.Sun(), ephem.Moon()], start_date=start_date, end_date=end_date, time_adjust=timedelta(hours=12)):

    dates = date_range(start_date, end_date, time_adjust)

    # define location parameters
    observer = ephem.Observer()
    observer.name = name
    observer.lat = str(lat)
    observer.lon = str(lon)

    dates_order = [ date[0] for date in dates ]
    transit_details = { date: [utc_offset, []] for date, utc_offset in dates }

    for d in dates_order:

        for body in bodies:
            # get the next rise & set times
            rising_local, setting_local = rise_and_set(observer, body, d, transit_details[d][0])
            # current date +1 day
            d_next = d + timedelta(days=1)

            # make sure not out of our date range and attempting to assign a value to a non-existant key
            if d <= rising_local < d_next:
                transit_details[d][1].append([rising_local, 'rising', body.name])
            elif d_next in dates_order:
                transit_details[d_next][1].append([rising_local, 'rising', body.name])

            if d <= setting_local < d_next:
                transit_details[d][1].append([setting_local, 'setting', body.name])
            elif d_next in dates_order:
                transit_details[d_next][1].append([setting_local, 'setting', body.name])

    for t in transit_details:
        transit_details[t][1].sort()


    for d in dates_order:
        to_print = ""
        to_print+=str(d)+"  "
        for event in transit_details[d][1]:
            to_print+=str(event[0])+"  "
        print to_print

    # return transit_details

    # print " 1 1 1 1 1 1 1 2 2 2 2 2 0 0 0 0 0 0 0 0 0 1 1 1"
    # print " 3 4 5 6 7 8 9 0 1 2 3 4 1 2 3 4 5 6 7 8 9 0 1 2"
    # for d in dates_order:
    #     events = transit_details[d][1]
    #     events_count = len(events)
    #     dn = chr(176)
    #     up = chr(219)
    #     result = ""
    #     start = d
    #
    #     # start_len = transit[d][1][0][0] - d
    #     # start_len = int(start_len.total_seconds())/1800
    #     #
    #     # if transit[d][1][0][1] == 'rising':
    #     #     result = result + dn * start_len
    #     # else:
    #     #     result = result + up * start_len
    #     for event in events:
    #         before = up if event[1] == 'setting' else dn
    #         length = event[0] - start
    #         length = int(length.total_seconds())
    #         result += before*(length/450)
    #         start = event[0]
    #
    #     # tomorrow = d + timedelta(days=1)
    #     # remaining = tomorrow - event[0]
    #     # remaining = int(remaining.total_seconds())
    #     # result += before*(remaining/1800)
    #     before = up if before == dn else dn
    #     result += before*(192-len(result))
    #     result += " "+d.strftime("%Y-%m-%d")


        # print result

        # transit = { date.to_pydatetime(): [utc_offset, []] for date, utc_offset in dates }
        # for event in transit[d]:
        #     if event[1] == 'rising':
        #         result = result +

    return dates, transit_details


def rise_and_set(observer, body, date, utc_offset):

    # convert search time (at local) to UTC time
    observer.date = date - utc_offset

    # event type
    rising = observer.next_rising(body, use_center=False)
    setting = observer.next_setting(body, use_center=False)

    # utc time of event
    rising_utc = ephem.Date(rising).datetime()
    setting_utc = ephem.Date(setting).datetime()
    # print "utc rise: "+str(rising_utc)
    # print "utc  set: "+str(setting_utc)

    #convert to local time (and remove any time values < second)
    rising_local = rising_utc + utc_offset
    rising_local = datetime(rising_local.year, rising_local.month, rising_local.day, rising_local.hour, rising_local.minute)
    setting_local = setting_utc + utc_offset
    setting_local = datetime(setting_local.year, setting_local.month, setting_local.day, setting_local.hour, setting_local.minute)


    # print date, rising_local, setting_local

    return rising_local, setting_local



















#
# def event_times(observer, event, date):
#
#     return
#
#
#
# def dark_skies(dates=date_range(), horizon=0):
#
#     return
#

## notes
# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for possible tz variables
# moon_phase method instead of phase method when returning current moon illumination
# body.separation method provides angle between two positions on sphere
# from ephem import cities >> albury = cities.lookup('Albury, Australia') returns lat lon for Albury
# when sun/moon(?) never rise/set at the poles an ephem.CircumpolarError error will be thrown for next_xxx() methods which needs to be taken in to account


## resources
# Moon illumination and resulting skyglow relationship
# http://www.skyandtelescope.com/astronomy-resources/astronomy-questions-answers/how-does-the-moons-phase-affect-the-skyglow-of-any-given-location-and-how-many-days-before-or-after-a-new-moon-is-a-dark-site-not-compromised/
