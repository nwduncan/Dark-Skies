# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times
import ephem
import pandas
from datetime import datetime
from datetime import timedelta
import pytz
from PIL import Image, ImageDraw
from os.path import join

# location parameters
name = "Albury"
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
# elev = 160

# observer initialisation
observer = ephem.Observer()
observer.name = name
observer.lat = str(lat)
observer.lon = str(lon)
start_date = datetime(2018,8,1)
end_date = datetime(2018,8,31)


# return a date range including UTC offset for each date
def date_range(start_date=start_date, end_date=end_date, time_adjust=0):

    if not type(time_adjust) == timedelta:
        time_adjust = timedelta(hours=time_adjust)

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


def dark_skies(start_date=start_date, end_date=end_date, time_adjust=12, horizon=0):

    output = open('page.html', 'w')

    # get the date range
    dates = date_range(start_date, end_date, time_adjust)
    # establish bodies
    bodies = { 'sun': ephem.Sun(), 'moon': ephem.Moon() }

    # # define location parameters
    # observer = ephem.Observer()
    # observer.name = name
    # observer.lat = str(lat)
    # observer.lon = str(lon)

    # use the list of keys (dates) so we can call the transit_details items in order
    dates_order = [ date[0] for date in dates ]
    # create transit_details structure and fill with what we know
    transit_details = { date: [utc_offset, {'sun': None, 'moon': None }, []] for date, utc_offset in dates }

    for d in dates_order:
        for body in bodies:

            # get the next rise & set times
            rising_local, setting_local = rise_and_set(bodies[body], d, transit_details[d][0])
            # current date +1 day
            d_next = d + timedelta(days=1)

            # check whether body is above the horizon at start of day
            start_above = above_horizon(bodies[body], d, transit_details[d][0])
            transit_details[d][1][body] = start_above

            # figure out which day our event falls within and apply it to the corresponding transit_details value
            # rising
            if d <= rising_local < d_next:
                transit_details[d][2].append([rising_local, True, bodies[body].name])
            elif d_next in dates_order:
                transit_details[d_next][2].append([rising_local, True, bodies[body].name])

            # setting
            if d <= setting_local < d_next:
                transit_details[d][2].append([setting_local, False, bodies[body].name])
            elif d_next in dates_order:
                transit_details[d_next][2].append([setting_local, False, bodies[body].name])

    # order the dates within each transit_details entry
    for t in transit_details:
        transit_details[t][2].sort()

    # determine which character to return to symbolise current sun & moon position
    def return_chr(state):
        sun_pos, moon_pos = state
        if sun_pos and moon_pos:
            # return chr(219)
            return (255,255,255)
        elif sun_pos and not moon_pos:
            # return chr(178)
            return (255,255,0)
        elif not sun_pos and moon_pos:
            # return chr(176)
            return (0,0,102)
        else:
            # return " "
            return (0,0,0)

    # change the current state based on what's above the horizon
    def change_state(current_state, change, body):
        if body == 'Sun':
            current_state[0] = change
            return current_state
        else:
            current_state[1] = change
            return current_state

    # print variables
    day_length = 86400
    print_length = 900
    #
    # # header details
    # header = "Dark Skies: {} >> {}".format(dates_order[0].date(), dates_order[-1].date())
    # header = "-"*(print_length/2-18)+header+"-"*(print_length/2-18)
    # print header
    # # time markers
    # times = [ str(x) if len(str(x)) == 2 else '0'+str(x) for x in range(12,25)+range(1,12) ]
    # time_markers = ""
    # for t in times:
    #     time_markers += "|"+t+" "*((print_length/24)-3)
    # print time_markers

    # go through each date
    for d in dates_order:
        # to_print = ""
        filename = str(d.date())+'.png'
        path = join('images', str(d.date())+'.png')
        image = Image.new('RGB', (900, 20), (255,255,255))
        draw = ImageDraw.Draw(image)

        # get current sun & moon positions
        sun_pos = transit_details[d][1]['sun']
        moon_pos = transit_details[d][1]['moon']

        # current state and time
        c_state = [sun_pos, moon_pos]
        c_chr = return_chr(c_state)
        c_time = d
        length_count = 0

        # iterate over events for the day
        for event in transit_details[d][2]:
            # next event time
            n_time = event[0]
            # next event state
            n_state = change_state(c_state, event[1], event[2])
            # time between previous event and next event
            length = n_time - c_time
            # length of string to add to to_print
            length = int(round(length.total_seconds()/day_length*print_length, 0))
            # to_print += c_chr*length
            draw.rectangle((length_count, 0, length, 20), c_chr)

            # apply next variables to current variables to prepare for next iteration
            c_state = n_state
            c_chr = return_chr(c_state)
            c_time = n_time
            length_count += length

        # finalise to_print and print it
        # to_print += c_chr*(print_length-len(to_print))+" >> "+str(d.date())
        image.save(path)
        output.write('<img src="images\{}">'.format(filename))
        # print to_print


# return the next rise and set times
def rise_and_set(body, date, utc_offset):

    # convert search time (at local) to UTC time
    observer.date = date - utc_offset

    # event type
    rising = observer.next_rising(body, use_center=False)
    setting = observer.next_setting(body, use_center=False)

    # utc time of event
    rising_utc = ephem.Date(rising).datetime()
    setting_utc = ephem.Date(setting).datetime()

    # convert to local time (and remove any sub-second information)
    rising_local = rising_utc + utc_offset
    rising_local = datetime(rising_local.year, rising_local.month, rising_local.day, rising_local.hour, rising_local.minute)
    setting_local = setting_utc + utc_offset
    setting_local = datetime(setting_local.year, setting_local.month, setting_local.day, setting_local.hour, setting_local.minute)

    return rising_local, setting_local

# check to see whether a body is above the horizon
def above_horizon(body, date, utc_offset):

    observer.date = date - utc_offset
    body.compute(observer)

    if body.alt > 0:
        return True

    return False




## notes
# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for possible tz variables
# moon_phase method instead of phase method when returning current moon illumination
# body.separation method provides angle between two positions on sphere
# from ephem import cities >> albury = cities.lookup('Albury, Australia') returns lat lon for Albury
# when sun/moon(?) never rise/set at the poles an ephem.CircumpolarError error will be thrown for next_xxx() methods which needs to be taken in to account


## resources
# Moon illumination and resulting skyglow relationship
# http://www.skyandtelescope.com/astronomy-resources/astronomy-questions-answers/how-does-the-moons-phase-affect-the-skyglow-of-any-given-location-and-how-many-days-before-or-after-a-new-moon-is-a-dark-site-not-compromised/
