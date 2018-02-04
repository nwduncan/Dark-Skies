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
        twilight = { 'day':          (0, False),
                     'civil':        (-6, True),
                     'nautical':     (-12, True),
                     'astronomical': (-18, True) }
        for date in self.dates:
            for phase in twilight:
                alt = twilight[phase][0]
                use_center = twilight[phase][1]
                rising, setting = self.rise_and_set(self.sun, date, str(alt), use_center)
                date.sun_events.append([rising, alt])
                date.sun_events.append([setting, alt])
            date.sun_events.sort()
            self.observer.horizon = '0'
            date.sun_start = self.altitude(self.sun, date)

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
            self.moon_events = []






























#
