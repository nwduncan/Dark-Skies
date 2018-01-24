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
            date = Date(adjusted_time, utc_offset)
            self.dates.append(date)

    def compute(self):


    def above_horizon(self, body, date):
        self.observer.date = date.date - date.utc_offset
        date.body.compute(self.observer)
        if date.body.alt > 0:
            return True
        return False


    class Date(object):
        def __init__(self, date, utc_offset):
            self.date = date
            self.utc_offset = utc_offset
            self.sun = ephem.Sun()
            self.moon = ephem.Moon()
            self.sun_start = None
            self.moon_start = None
            self.events = []

        def compute(self, observer):

            return





























#
