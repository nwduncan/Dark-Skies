# Classes used to manage the dark skies data
from datetime import datetime, timedelta
import pandas
import ephem
import pytz
from math import degrees


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
                date.sun_events.append([rising, alt, rgb[0]])
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

            # date.sun_events.insert(0, [date.date, date.sun_start, start_phase])

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
        return

    def rise_and_set(self, body, date, horizon, use_center):
        # convert search time (at local) to UTC time
        self.observer.date = date.date - date.utc_offset
        self.observer.horizon = horizon

        # event type
        # consider using previous rise/set times as well
        rising = self.observer.next_rising(body, use_center=use_center)
        setting = self.observer.next_setting(body, use_center=use_center)

        # utc time of event
        rising_utc = ephem.Date(rising).datetime()
        setting_utc = ephem.Date(setting).datetime()

        # convert to local time (and remove any sub-minute information)
        rising_local = rising_utc + date.utc_offset
        rising_local = self.truncate_date(rising_local)
        setting_local = setting_utc + date.utc_offset
        setting_local = self.truncate_date(setting_local)

        return rising_local, setting_local


    def altitude(self, body, date):
        self.observer.date = date.date - date.utc_offset
        self.sun.compute(self.observer)
        return degrees(self.sun.alt)


    def truncate_date(self, date):
        return datetime(date.year, date.month, date.day, date.hour, date.minute)


    class Date(object):
        def __init__(self, date, utc_offset):
            self.date = date
            self.utc_offset = utc_offset
            self.sun_start = None
            self.moon_start = None
            self.moon_phase = None
            self.sun_events = []
            self.sun_instructions = []
            self.moon_events = []






























#
