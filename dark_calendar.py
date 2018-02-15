# Classes used to manage the dark skies data
from datetime import datetime, timedelta
import pandas
import ephem
import pytz
from math import degrees


def testing():
    name = "Albury"
    lat = -36.07
    lon = 146.91
    timezone = "Australia/Sydney"
    observer = ephem.Observer()
    observer.name = name
    observer.lat = str(lat)
    observer.lon = str(lon)
    start_date = datetime(2018,1,1)
    end_date = datetime(2018,12,31)
    test_obj = Calendar(start_date, end_date, timedelta(hours=12), observer, timezone)
    test_obj.build_range()
    test_obj.compute_sun()
    test_obj.compute_moon()
    return test_obj


class Calendar(object):
    def __init__(self, start_date, end_date, time_adjust, observer, timezone):
        self.start_date = start_date
        self.end_date = end_date
        self.time_adjust = time_adjust
        self.observer = observer
        self.timezone = timezone
        self.dates = None
        self.sun = ephem.Sun()
        self.moon = ephem.Moon()


    def build_range(self):
        p_dates = pandas.date_range(self.start_date, self.end_date).tolist()
        self.dates = []

        for utc_date in p_dates:
            # convert pandas date to datetime
            utc_date = utc_date.to_pydatetime()
            # set local parameters
            local = pytz.timezone(self.timezone)
            localtime = local.localize(utc_date)
            # calculate difference between UTC & local
            utc_offset = localtime.utcoffset()
            # adjust time as specified
            adjusted_time = utc_date + self.time_adjust
            # create data tuple and store it
            date = Calendar.Date(adjusted_time, utc_offset)
            self.dates.append(date)

    def compute_sun(self):
        # twilghit calcs use centre of sun. day calcs uses upper edge
        day = 'day'
        civil = 'civil'
        nautical = 'nautical'
        astronomical = 'astronomical'
        night = 'night'
        twilight = { 'day':          (0, False, (day, civil)),
                     'civil':        (-6, True, (civil, nautical)),
                     'nautical':     (-12, True, (nautical, astronomical)),
                     'astronomical': (-18, True, (astronomical, night)) }

        for date in self.dates:
            for phase in twilight:
                alt = twilight[phase][0]
                use_center = twilight[phase][1]
                rgb = twilight[phase][2]
                rising, setting = self.rise_and_set(self.sun, date, str(alt), use_center)
                if rising:
                    date.sun_events.append([rising, alt, rgb[0]])
                if setting:
                    date.sun_events.append([setting, alt, rgb[1]])

            date.sun_events.sort()
            self.observer.horizon = '0'
            date.sun_start = self.altitude(self.sun, date)

            if date.sun_start >= 0:
                start_phase = 'day'
            elif 0 > date.sun_start >= -6:
                start_phase = 'civil'
            elif -6 > date.sun_start >= -12:
                start_phase = 'nautical'
            elif -12 > date.sun_start >= -18:
                start_phase = 'astronomical'
            else:
                start_phase = 'night'

            start_time = date.date
            count = 0
            for event in date.sun_events:
                seconds = (event[0]-start_time).total_seconds()
                count += seconds
                date.sun_instructions.append([seconds, start_phase])
                start_time = event[0]
                start_phase = event[2]

            time_left = 86400 - count
            date.sun_instructions.append([time_left, start_phase])


    def compute_moon(self):
        for date in self.dates:
            # moon phase & illumination
            self.observer.date = date.date - date.utc_offset
            self.moon.compute(self.observer)
            date.moon_illum = self.moon.moon_phase

            # get the next new moon and the previous new moon
            next_nm = ephem.next_new_moon(self.observer.date)
            prev_nm = ephem.previous_new_moon(self.observer.date)
            lunation = (self.observer.date-prev_nm)/(next_nm-prev_nm)
            lunation = lunation*100

            phase_range = 49.0/3

            if lunation <= 2:
                date.moon_phase = 'new moon'
            elif 2 < lunation <= phase_range:
                date.moon_phase = 'waxing crescent'
            elif phase_range < lunation <= phase_range*2:
                date.moon_phase = 'waxing half'
            elif phase_range*2 < lunation <= (phase_range*3)-2:
                date.moon_phase = 'waxing gibbous'
            elif (phase_range*3)-2 < lunation <= (phase_range*3)+2:
                date.moon_phase = 'full moon'
            elif (phase_range*3)+2 < lunation <= phase_range*4:
                date.moon_phase = 'waning gibbous'
            elif phase_range*4 < lunation <= phase_range*5:
                date.moon_phase = 'waning half'
            elif phase_range*5 < lunation <= 98:
                date.moon_phase = 'waning crescent'
            elif 98 < lunation <= 100:
                date.moon_phase = 'new moon'

            date.moon_phase += " - " + str(round(lunation, 2)) + " - " + str(round(date.moon_illum*100, 1))

            # moon rise and set
            rising, setting = self.rise_and_set(self.moon, date, use_center=True)
            plus_24 = date.date + timedelta(hours=24)
            if rising and date.date <= rising < plus_24:
                date.moon_events.append([rising, 'rising'])
            if setting and date.date <= setting < plus_24:
                date.moon_events.append([setting, 'setting'])
            date.moon_events.sort()

            # moon draw instructions
            count = 0
            start_time = date.date
            date.moon_start = self.altitude(self.moon, date)
            moon_status = True if date.moon_start > 0 else False
            for event in date.moon_events:
                seconds = (event[0]-start_time).total_seconds()
                count += seconds
                date.moon_instructions.append([seconds, moon_status])
                start_time = event[0]
                moon_status = not moon_status

            time_left = 86400 - count
            date.moon_instructions.append([time_left, moon_status])



    def rise_and_set(self, body, date, horizon='0', use_center=False):
        # convert search time (at local) to UTC time
        self.observer.date = date.date - date.utc_offset
        self.observer.horizon = horizon

        # rising
        # consider using previous rise/set times as well
        try:
            rising = self.observer.next_rising(body, use_center=use_center)
            # utc time of event
            rising_utc = ephem.Date(rising).datetime()
            # convert to local time (and remove any sub-minute information)
            rising_local = rising_utc + date.utc_offset
            rising_local = self.truncate_date(rising_local)

        except ephem.CircumpolarError:
            rising_local = False

        # setting
        # consider using previous rise/set times as well
        try:
            setting = self.observer.next_setting(body, use_center=use_center)
            # utc time of event
            setting_utc = ephem.Date(setting).datetime()
            # convert to local time (and remove any sub-minute information)
            setting_local = setting_utc + date.utc_offset
            setting_local = self.truncate_date(setting_local)
        except ephem.CircumpolarError:
            setting_local = False

        return rising_local, setting_local


    def altitude(self, body, date):
        self.observer.date = date.date - date.utc_offset
        body.compute(self.observer)
        return degrees(body.alt)


    def truncate_date(self, date):
        return datetime(date.year, date.month, date.day, date.hour, date.minute)


    class Date(object):
        def __init__(self, date, utc_offset):
            self.date = date
            self.utc_offset = utc_offset
            self.sun_start = None
            self.sun_events = []
            self.sun_instructions = []
            self.moon_start = None
            self.moon_phase = None
            self.moon_illum = None
            self.moon_events = []
            self.moon_instructions = []
