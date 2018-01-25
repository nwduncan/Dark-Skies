# Classes used to manage the dark skies data
from datetime import datetime, timedelta
import pandas
import ephem
import pytz


class Calendar(object):
    def __init__(self, start_date, end_date, time_adjust, observer, timezone):
        self.start_date = start_date
        self.end_date = end_date
        self.time_adjust = time_adjust
        self.observer = observer
        self.timezone = timezone
        self.dates = None
        self.sun_event_params = { ephem.Sun(): (('civil', 0),
                                                ('naut', 6),
                                                ('astro', 12),
                                                ('night', 18)),
                                  ephem.Moon(): (('moon', 0),) }
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
        return

    def compute_moon(self):
        return

    def rise_and_set(self, body, date, horizon):
        # convert search time (at local) to UTC time
        self.observer.date = date.date - date.utc_offset
        self.observer.horizon = horizon

        # event type
        rising = observer.next_rising(body)
        setting = observer.next_setting(body)

        # utc time of event
        rising_utc = ephem.Date(rising).datetime()
        setting_utc = ephem.Date(setting).datetime()

        # convert to local time (and remove any sub-minute information)
        rising_local = rising_utc + utc_offset
        rising_local = truncate_date(rising_local)
        setting_local = setting_utc + utc_offset
        setting_local = truncate_date(setting_local)

        return rising_local, setting_local


    def above_horizon(self, body, date):
        self.observer.date = date.date - date.utc_offset
        date.body.compute(self.observer)
        if date.body.alt > 0:
            return True
        return False


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
