import datetime as dt
import regex
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone


class DateParser:
    el_name_relative = ('years', 'months', 'days', 'hours', 'minutes', 'seconds')
    el_name = ('year', 'month', 'day', 'hour', 'minute', 'second')

    @staticmethod
    def _resolve_stop_date(till, through):
        if till is None and through is None:
            raise AssertionError('Both till date and through date are not supplied. '
                                 'Supply one of these')
        if till is not None and through is not None:
            raise AssertionError('Both till date and through date are supplied. '
                                 'Supply only one of these')
        if through is None:
            stop = till
            func = lambda start, stop: start < stop
        else:
            stop = through
            func = lambda start, stop: start <= stop
        return func, stop

    @staticmethod
    def _get_unit(unit, options, linked_options):
        if unit not in options:
            try:
                unit = next(o for o, l in zip(options, linked_options) if unit == l)
            except StopIteration:
                raise TypeError('Unit "{un}" is not a valid time unit (use one of: "{opts}").'
                                .format(un=unit, opts='", "'.join(options)))
        return unit

    @staticmethod
    def _extract_timezone(date_li):
        tz = get_localzone()
        iter_date_li = tuple(date_li)
        for dtc in iter_date_li:
            try:
                int(dtc)
            except ValueError:
                tz = pytz.timezone(dtc)
                date_li.remove(dtc)
                break
        return tz, date_li

    def _resolve_relatives(self, date_li):
        now = dt.datetime.now()
        for dtc, el in zip(date_li, self.el_name_relative):
            if regex.search('[-]|[+]', dtc):
                now += relativedelta(**{el: int(dtc)})
        new_date_li = []
        for dtc, el in zip(date_li, self.el_name):
            if regex.search('[-]|[+]', dtc):
                new_date_li.append(getattr(now, el))
            else:
                new_date_li.append(dtc)
        return new_date_li

    def make_date(self, date_str, tz_out='UTC'):
        date_li = regex.split(',|:|[ ]|/', date_str)
        tz, date_li = self._extract_timezone(date_li)
        if len(date_li) < 3:
            raise SyntaxError('The provided string was not a valid date nor datetime. '
                              'At least a year, month and day should have'
                              'been provided.')
        try:
            date_dt = parser.parse(date_str)
        except ValueError:
            if '-' in date_str or '+' in date_str:
                date_li = self._resolve_relatives(date_li)
            date_dt = dt.datetime(*map(int, date_li))
        if date_dt.tzinfo is None:
            date_dt = tz.localize(date_dt)
        tz_out = pytz.timezone(tz_out)
        return date_dt.astimezone(tz_out)

    def make_date_or_return(self, date_str, tz_out='UTC'):
        try:
            return self.make_date(date_str, tz_out=tz_out)
        except:
            return date_str

    def make_date_range(self, from_date, till_date=None, through_date=None, size=1, unit='minutes', tz_out='UTC'):
        func, stop_date = self._resolve_stop_date(till_date, through_date)
        unit = self._get_unit(unit, self.el_name_relative, self.el_name)

        if not isinstance(from_date, dt.datetime):
            from_date = self.make_date(from_date, tz_out)
        if not isinstance(stop_date, dt.datetime):
            stop_date = self.make_date(stop_date, tz_out)

        date_range = []
        delta = relativedelta(**{unit: int(size)})
        while func(from_date, stop_date):
            date_range.append(from_date)
            from_date += delta
        return date_range
