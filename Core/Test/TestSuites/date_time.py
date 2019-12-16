import unittest as ut
import datetime as dt
import Fw.Core.date_time as fw_dt
import pytz


class MakeDateTests(ut.TestCase):
    def setUp(self):
        self.dp = fw_dt.DateParser()

    def assert_dt_abs(self, date_dt, year=None, month=None, day=None, hour=None,
                      minute=None, second=None, tz_text=None):
        if year is not None:
            self.assertEqual(year, date_dt.year, 'Year should have been {year}'.format(year=year))
        if month is not None:
            self.assertEqual(month, date_dt.month, 'Month should have been {month}'.format(month=month))
        if day is not None:
            self.assertEqual(day, date_dt.day, 'Day should have been {day}'.format(day=day))
        if hour is not None:
            self.assertEqual(hour, date_dt.hour, 'Hour should have been {hour}'.format(hour=hour))
        if minute is not None:
            self.assertEqual(minute, date_dt.minute, 'Minute should have been {min}'.format(min=minute))
        if second is not None:
            self.assertEqual(second, date_dt.second, 'Second should have been {sec}'.format(sec=second))
        if tz_text is not None:
            self.assertEqual(tz_text, str(date_dt.tzinfo), 'Timezone should be {tz}'.format(tz=tz_text))

    def assert_dt_rel(self, date_dt, start, stop, year=False, month=False, day=False, hour=False,
                      minute=False, second=False, tz_text=None):
        if year:
            self.assertTrue(start.year <= date_dt.year <= stop.year,
                            'Year should have been between {t1} and {t2}'.format(t1=start.year, t2=stop.year))
        if month:
            self.assertTrue(start.month <= date_dt.month <= stop.month,
                            'Month should have been between {t1} and {t2}'.format(t1=start.month, t2=stop.month))
        if day:
            self.assertTrue(start.day <= date_dt.day <= stop.day,
                            'Day should have been between {t1} and {t2}'.format(t1=start.day, t2=stop.day))
        if hour:
            self.assertTrue(start.hour <= date_dt.hour <= stop.hour,
                            'Hour should have been between {t1} and {t2}'.format(t1=start.hour, t2=stop.hour))
        if minute:
            self.assertTrue(start.minute <= date_dt.minute <= stop.minute,
                            'Minute should have been between {t1} and {t2}'.format(t1=start.minute, t2=stop.minute))
        if second:
            self.assertTrue(start.second <= date_dt.second <= stop.second,
                            'Second should have been between {t1} and {t2}'.format(t1=start.second, t2=stop.second))
        if tz_text is not None:
            self.assertEqual(str(date_dt.tzinfo), tz_text, 'Timezone should be {tz}'.format(tz=tz_text))

    def test_all_absolute(self):
        date_dt = self.dp.make_date('UTC 2019/01/01 00:00:00')
        self.assert_dt_abs(date_dt, year=2019, month=1, day=1, hour=0, minute=0, second=0, tz_text='UTC')

    def test_all_relative(self):
        tz = pytz.timezone('UTC')
        start = tz.localize(dt.datetime.now().replace(microsecond=0))
        date_dt = self.dp.make_date('UTC +0/+0/+0 +0:+0:+0')
        stop = tz.localize(dt.datetime.now().replace(microsecond=0))
        self.assert_dt_rel(date_dt, start, stop, year=True, month=True, day=True, hour=True, minute=True, second=True,
                           tz_text='UTC')

    def test_combi(self):
        tz = pytz.timezone('UTC')
        start = tz.localize(dt.datetime.now().replace(microsecond=0))
        date_dt = self.dp.make_date('UTC +0/2/+0 2:+0:2')
        stop = tz.localize(dt.datetime.now().replace(microsecond=0))
        self.assert_dt_rel(date_dt, start, stop, year=True, day=True, minute=True, tz_text='UTC')
        self.assert_dt_abs(date_dt, month=2, hour=2, second=2)

    def test_tzincl(self):
        date_dt = fw_dt.DateParser().make_date('CET 2019/2/1 00:00:00')
        self.assert_dt_abs(date_dt, year=2019, month=1, day=31, hour=23, minute=0, second=0, tz_text='UTC')

    def test_set_tz_out(self):
        date_dt = self.dp.make_date('UTC 2019/01/01 00:00:00', tz_out='CET')
        self.assert_dt_abs(date_dt, year=2019, month=1, day=1, hour=1, minute=0, second=0, tz_text='CET')

    def test_not_enough_positions(self):
        with self.assertRaises(SyntaxError):
            self.dp.make_date('2019/01', tz_out='CET')


class MakeDateOrReturnTests(ut.TestCase):
    def setUp(self):
        self.dp = fw_dt.DateParser()

    assert_dt_abs = MakeDateTests.assert_dt_abs
    assert_dt_rel = MakeDateTests.assert_dt_rel

    def test_positive(self):
        date_dt = self.dp.make_date_or_return('UTC 2019/01/01 00:00:00')
        self.assert_dt_abs(date_dt, year=2019, month=1, day=1, hour=0, minute=0, second=0, tz_text='UTC')

    def test_negative(self):
        date_dt = self.dp.make_date_or_return('invalid_date')
        self.assertEqual('invalid_date', date_dt, 'The input should have been returned')


class MakeDateRangeTests(ut.TestCase):
    def setUp(self):
        self.dp = fw_dt.DateParser()

    assert_dt_abs = MakeDateTests.assert_dt_abs
    assert_dt_rel = MakeDateTests.assert_dt_rel

    def test_positive_till(self):
        rng = self.dp.make_date_range('UTC 2019/01/01', till_date='UTC 2029/01/01', size=1, unit='year')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=0, minute=0, second=0)
        self.assert_dt_abs(rng[-1], year=2028, month=1, day=1, hour=0, minute=0, second=0)
        self.assertEqual(10, len(rng), 'The range should consist of 10 items.')

    def test_positive_through(self):
        rng = self.dp.make_date_range('UTC 2019/01/01', through_date='UTC 2029/01/01', size=1, unit='year')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=0, minute=0, second=0)
        self.assert_dt_abs(rng[-1], year=2029, month=1, day=1, hour=0, minute=0, second=0)
        self.assertEqual(11, len(rng), 'The range should consist of 11 items.')

    def test_month(self):
        rng = self.dp.make_date_range('UTC 2019/01/01', through_date='UTC 2019/05/01', size=1, unit='month')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=0, minute=0, second=0)
        self.assert_dt_abs(rng[-1], year=2019, month=5, day=1, hour=0, minute=0, second=0)
        self.assertEqual(5, len(rng), 'The range should consist of 5 items.')

    def test_day(self):
        rng = self.dp.make_date_range('UTC 2019/01/01', through_date='UTC 2019/01/05', size=1, unit='day')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=0, minute=0, second=0)
        self.assert_dt_abs(rng[-1], year=2019, month=1, day=5, hour=0, minute=0, second=0)
        self.assertEqual(5, len(rng), 'The range should consist of 5 items.')

    def test_hour(self):
        rng = self.dp.make_date_range('UTC 2019/01/01 1', through_date='UTC 2019/01/01 5', size=1, unit='hour')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=1, minute=0, second=0)
        self.assert_dt_abs(rng[-1], year=2019, month=1, day=1, hour=5, minute=0, second=0)
        self.assertEqual(5, len(rng), 'The range should consist of 5 items.')

    def test_minute(self):
        rng = self.dp.make_date_range('UTC 2019/01/01 1:1', through_date='UTC 2019/01/01 1:5', size=1,
                                      unit='minute')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=1, minute=1, second=0)
        self.assert_dt_abs(rng[-1], year=2019, month=1, day=1, hour=1, minute=5, second=0)
        self.assertEqual(5, len(rng), 'The range should consist of 5 items.')

    def test_second(self):
        rng = self.dp.make_date_range('UTC 2019/01/01 1:1:1', through_date='UTC 2019/01/01 1:1:5', size=1,
                                      unit='second')
        self.assert_dt_abs(rng[0], year=2019, month=1, day=1, hour=1, minute=1, second=1)
        self.assert_dt_abs(rng[-1], year=2019, month=1, day=1, hour=1, minute=1, second=5)
        self.assertEqual(5, len(rng), 'The range should consist of 5 items.')

    def test_different_units_positive(self):
        units = tuple(['year', 'month', 'day', 'hour', 'minute', 'second'])
        time = tuple([12, 31, 24, 60, 60, 1])
        size = 1
        for t, unit in zip(time, units):
            self.dp.make_date_range('UTC 2019/01/01', through_date='UTC 2021/01/01', size=size, unit=unit)
            size *= t
        units = tuple([u + 's' for u in units])
        size = 1
        for t, unit in zip(time, units):
            self.dp.make_date_range('UTC 2019/01/01', through_date='UTC 2021/01/01', size=size, unit=unit)
            size *= t

    def test_negative_false_unit(self):
        with self.assertRaises(TypeError):
            self.dp.make_date_range('UTC 2019/01/01', through_date='UTC 2021/01/01', unit='false_unit')

    def test_negative_both_till_and_through(self):
        with self.assertRaises(AssertionError):
            self.dp.make_date_range('UTC 2019/01/01',
                                    through_date='UTC 2021/01/01',
                                    till_date='UTC 2021/01/01')

    def test_negative_no_till_nor_through(self):
        with self.assertRaises(AssertionError):
            self.dp.make_date_range('UTC 2019/01/01')
