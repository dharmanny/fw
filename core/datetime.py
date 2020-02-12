import datetime as dt
import regex
import pytz
import logging
from dateutil import parser
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone
from .utilities import Util


class DateParser:
    def __init__(self, *args):
        order = Util().settings().DEFAULT_DATE_TIME_ORDER
        order = [x.lower() for x in order]
        assert len(order) == 6, 'The given order of datetime elements is incomplete (!= 6)'

        el_name = ('year', 'month', 'day', 'hour', 'minute', 'second')
        assert len(set(el_name) & set(order)) == 6, 'The arguments passed as datetime order are invalid ' \
                                                    '(should contain "{}"'.format('", "'.join(el_name))

        self._el_name = tuple(order)
        self._el_name_relative = tuple([x + 's' for x in order])
        logging.debug('The date element order is: "{}"'.format('", "'.join(self._el_name)))

    @staticmethod
    def _resolve_stop_date(till, through):
        if till is None and through is None:
            raise AssertionError('Both till date and through date are not supplied. '
                                 'Supply one of these')
        if till is not None and through is not None:
            raise AssertionError('Both till date and through date are supplied. '
                                 'Supply only one of these')
        if through is None:
            logging.log('Using till as stopdtime.')
            stop = till
            func = lambda start, stop: start < stop
        else:
            logging.log('Using through as stopdtime.')
            stop = through
            func = lambda start, stop: start <= stop
        return func, stop

    @staticmethod
    def _get_unit(unit, options, linked_options):
        """
        Small helper function to get the right unit type
        """
        if unit not in options:
            try:
                unit = next(o for o, l in zip(options, linked_options) if unit == l)
            except StopIteration:
                raise TypeError('Unit "{un}" is not a valid time unit (use one of: "{opts}").'
                                .format(un=unit, opts='", "'.join(options)))
        logging.debug('Unit is {}'.format(unit))
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
        logging.debug('Extraxted time zone is: {}'.format(tz))
        return tz, date_li

    def _resolve_relatives(self, date_li):
        now = dt.datetime.now()
        for dtc, el in zip(date_li, self._el_name_relative):
            if regex.search('[-]|[+]', dtc):
                now += relativedelta(**{el: int(dtc)})
        new_date_li = []
        for dtc, el in zip(date_li, self._el_name):
            if regex.search('[-]|[+]', dtc):
                new_date_li.append(getattr(now, el))
            else:
                new_date_li.append(dtc)
        logging.debug('Found (absolute) date list: "{}"'.format('", "'.join(map(str,new_date_li))))
        return new_date_li

    def make_date(self, date_str: str, tz_out: str = 'UTC'):
        logging.debug('Given datestring is: {}'.format(date_str))
        date_li = regex.split('[.]|,|:|[ ]|/', date_str)
        tz, date_li = self._extract_timezone(date_li)
        if len(date_li) < 3:
            raise SyntaxError('The provided string was not a valid date nor datetime. '
                              'At least a year, month and day should have'
                              'been provided.')
        try:
            date_dt = parser.parse(date_str)
            logging.debug('Parser package is used for parsing the date string.')
        except ValueError:
            if '-' in date_str or '+' in date_str:
                date_li = self._resolve_relatives(date_li)
            date_dt = dt.datetime(*map(int, date_li))
            logging.debug('Parser package is not used for parsing the date string.')
        if date_dt.tzinfo is None:
            date_dt = tz.localize(date_dt)
        tz_out = pytz.timezone(tz_out)
        result = date_dt.astimezone(tz_out)
        logging.info('Datestring: "{ds}", returned date: "{dt}"'.format(ds=date_str, dt=result))
        return result

    def make_date_or_return(self, date_str, tz_out='UTC'):
        try:
            return self.make_date(date_str, tz_out=tz_out)
        except:
            logging.info('Passed date string ("{}") could not be converted to a date.'.format(date_str))
            return date_str

    def make_date_range(self, from_date, till_date=None, through_date=None, size=1, unit='minutes', tz_out='UTC'):
        func, stop_date = self._resolve_stop_date(till_date, through_date)
        unit = self._get_unit(unit, self._el_name_relative, self._el_name)

        if not isinstance(from_date, dt.datetime):
            from_date = self.make_date(from_date, tz_out)
        if not isinstance(stop_date, dt.datetime):
            stop_date = self.make_date(stop_date, tz_out)

        date_range = []
        delta = relativedelta(**{unit: int(size)})
        while func(from_date, stop_date):
            date_range.append(from_date)
            from_date += delta
        logging.info('Created a date range between {start} and {stop} with a total of {nr} values.'
                     .format(start=from_date, stop=stop_date, nr=len(date_range)))
        return date_range
