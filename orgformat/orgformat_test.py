#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2019-11-05 21:36:39 vk>

import unittest
import time
import datetime
import os
from orgformat import OrgFormat, TimestampParseException


class TestOrgFormat(unittest.TestCase):

    def test_orgmode_timestamp_to_datetime(self):
        self.assertEqual(OrgFormat.orgmode_timestamp_to_datetime(
            '<1980-12-31 Wed 23:59>'),
                         datetime.datetime(1980, 12, 31, 23, 59, 0, tzinfo=None))
        self.assertEqual(OrgFormat.orgmode_timestamp_to_datetime(
            '[1980-12-31 Wed 23:59]'),
                         datetime.datetime(1980, 12, 31, 23, 59, 0, tzinfo=None))
        with self.assertRaises(TimestampParseException):
            OrgFormat.orgmode_timestamp_to_datetime('foobar')
        with self.assertRaises(TimestampParseException):
            OrgFormat.orgmode_timestamp_to_datetime('<1980-12-31 23:59>')  # missing day of week

    def test_apply_timedelta_to_org_timestamp(self):
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2019-11-05 Tue 23:59>', 1), '<2019-11-06 Wed 00:59>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2019-11-06 Wed 00:59>', -1), '<2019-11-05 Tue 23:59>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2019-11-05 Tue 23:59>', 2.0), '<2019-11-06 Wed 01:59>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2019-11-06 Wed 00:59>', -2.0), '<2019-11-05 Tue 22:59>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2019-12-31 Tue 23:00>', 2.5), '<2020-01-01 Wed 01:30>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2020-01-01 Wed 01:30>', -2.5), '<2019-12-31 Tue 23:00>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2019-12-31 Tue 23:00>-<2019-12-31 Tue 23:30>', 2.5),
                         '<2020-01-01 Wed 01:30>--<2020-01-01 Wed 02:00>')
        self.assertEqual(OrgFormat.apply_timedelta_to_org_timestamp(
            '<2020-01-01 Wed 01:30>--<2020-01-01 Wed 02:00>', -2.5),
                         '<2019-12-31 Tue 23:00>--<2019-12-31 Tue 23:30>')

    def test_struct_time_to_datetime(self):
        self.assertEqual(OrgFormat.struct_time_to_datetime(
            time.struct_time((2019, 12, 31, 23, 59, 0, 0, 0, 0))),
                         datetime.datetime(2019, 12, 31, 23, 59, 0, tzinfo=None))

    def test_datetime_to_struct_time(self):
        self.assertEqual(OrgFormat.datetime_to_struct_time(
            datetime.datetime(2019, 12, 31, 23, 59, 0, tzinfo=None)),
                         time.strptime("31 Dec 2019 23:59:00", "%d %b %Y %H:%M:%S"))
        # NOTE: the time.strptime() statement returns:
        #                 time.struct_time(tm_year=2019, tm_mon=12, tm_mday=31, tm_hour=23, tm_min=59,
        #                                  tm_sec=0, tm_wday=3, tm_yday=335, tm_isdst=-1))

    def test_fix_struct_time_wday(self):

        self.assertEqual(OrgFormat.fix_struct_time_wday(time.struct_time([2013, 4, 3, 10, 54, 0, 0, 0, 0])),
                         time.struct_time([2013, 4, 3, 10, 54, 0, 2, 0, 0]))

        # same test but a bit more human readable for understanding:

        # define a time-stamp with weekday == 0:
        timestamp = time.struct_time([2013, 4, 3, 10, 54, 0, 0, 0, 0])
        # OrgFormat.date(timestamp)  ## '<2013-04-03 Mon>' -> Mon is wrong for April 3rd 2013

        self.assertEqual(OrgFormat.date(OrgFormat.fix_struct_time_wday(timestamp), show_time=True, inactive=False),
                         '<2013-04-03 Wed 10:54>')

    def test_date(self):

        # NOTE: time.strptime() returns a time.struct_time

        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38:42', '%Y-%m-%dT%H:%M:%S')),
                         '<2011-11-02 Wed>')
        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38', '%Y-%m-%dT%H:%M')),
                         '<2011-11-02 Wed>')

        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38:42', '%Y-%m-%dT%H:%M:%S'), show_time=True),
                         '<2011-11-02 Wed 20:38>')
        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38', '%Y-%m-%dT%H:%M'), show_time=True),
                         '<2011-11-02 Wed 20:38>')

        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38:42', '%Y-%m-%dT%H:%M:%S'), inactive=True),
                         '[2011-11-02 Wed]')
        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38', '%Y-%m-%dT%H:%M'), inactive=True),
                         '[2011-11-02 Wed]')

        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38:42', '%Y-%m-%dT%H:%M:%S'), inactive=True, show_time=True),
                         '[2011-11-02 Wed 20:38]')
        self.assertEqual(OrgFormat.date(time.strptime('2011-11-02T20:38', '%Y-%m-%dT%H:%M'), inactive=True, show_time=True),
                         '[2011-11-02 Wed 20:38]')

    def test_daterange(self):

        # NOTE: time.strptime() returns a time.struct_time

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29', '%Y-%m-%d'),
                time.strptime('2011-11-30', '%Y-%m-%d')),
            '<2011-11-29 Tue>--<2011-11-30 Wed>')

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S')),
            '<2011-11-29 Tue>--<2011-11-30 Wed>')

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S'), show_time=False),
            '<2011-11-29 Tue>--<2011-11-30 Wed>')

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S'), show_time=False, inactive=True),
            '[2011-11-29 Tue]--[2011-11-30 Wed]')

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S'), show_time=True, inactive=True),
            '[2011-11-29 Tue 20:38]--[2011-11-30 Wed 23:59]')

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S'), show_time=False, inactive=False),
            '<2011-11-29 Tue>--<2011-11-30 Wed>')

        self.assertEqual(
            OrgFormat.daterange(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S'), inactive=True),
            '[2011-11-29 Tue]--[2011-11-30 Wed]')

    def test_daterange_autodetect_time(self):

        # NOTE: time.strptime() returns a time.struct_time

        self.assertEqual(
            OrgFormat.daterange_autodetect_time(
                time.strptime('2011-11-29T20:38:42', '%Y-%m-%dT%H:%M:%S'),
                time.strptime('2011-11-30T23:59:58', '%Y-%m-%dT%H:%M:%S'), inactive=True),
            '[2011-11-29 Tue 20:38]--[2011-11-30 Wed 23:59]')

        self.assertEqual(
            OrgFormat.daterange_autodetect_time(
                time.strptime('2011-11-29T20:38', '%Y-%m-%dT%H:%M'),
                time.strptime('2011-11-30T23:59', '%Y-%m-%dT%H:%M'), inactive=True),
            '[2011-11-29 Tue 20:38]--[2011-11-30 Wed 23:59]')

        self.assertEqual(
            OrgFormat.daterange_autodetect_time(
                time.strptime('2011-11-29', '%Y-%m-%d'),
                time.strptime('2011-11-30T23:59', '%Y-%m-%dT%H:%M'), inactive=True),
            '[2011-11-29 Tue 00:00]--[2011-11-30 Wed 23:59]')

        self.assertEqual(
            OrgFormat.daterange_autodetect_time(
                time.strptime('2011-11-29T20:38', '%Y-%m-%dT%H:%M'),
                time.strptime('2011-11-30', '%Y-%m-%d'), inactive=True),
            '[2011-11-29 Tue 20:38]--[2011-11-30 Wed 00:00]')

        self.assertEqual(
            OrgFormat.daterange_autodetect_time(
                time.strptime('2011-11-29', '%Y-%m-%d'),
                time.strptime('2011-11-30', '%Y-%m-%d'), inactive=True),
            '[2011-11-29 Tue]--[2011-11-30 Wed]')

    def test_strdate(self):
        self.assertEqual(OrgFormat.strdate('2011-11-03'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-3'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-1-3'), '<2011-01-03 Mon>')
        with self.assertRaises(TimestampParseException):
            OrgFormat.strdate('11-1-3')
        self.assertEqual(OrgFormat.strdate('2011-11-03', show_time=True), '<2011-11-03 Thu 00:00>')
        self.assertEqual(OrgFormat.strdate('2011-11-03', inactive=True), '[2011-11-03 Thu]')
        self.assertEqual(OrgFormat.strdate('2011-11-03', inactive=True, show_time=True), '[2011-11-03 Thu 00:00]')

        self.assertEqual(OrgFormat.strdate('2011-11-03 23:59'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-03 23:59:00'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-03 23:59', show_time=True), '<2011-11-03 Thu 23:59>')
        self.assertEqual(OrgFormat.strdate('2011-11-03 23:59:00', show_time=True), '<2011-11-03 Thu 23:59>')
        self.assertEqual(OrgFormat.strdate('2011-1-2 3:4:5', show_time=True), '<2011-01-02 Sun 03:04>')
        self.assertEqual(OrgFormat.strdate('2011-11-03 23:59', show_time=False), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-03 23:59', inactive=True, show_time=True), '[2011-11-03 Thu 23:59]')

        self.assertEqual(OrgFormat.strdate('2011-11-03T23:59'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-03T23:59:58'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-03T23.59'), '<2011-11-03 Thu>')
        self.assertEqual(OrgFormat.strdate('2011-11-03T23.59:58'), '<2011-11-03 Thu>')

        with self.assertRaises(TimestampParseException):
            OrgFormat.strdate('foo')

        #######################

        self.assertEqual(OrgFormat.strdate('2011-11-30T21.06', show_time=True),
                         '<2011-11-30 Wed 21:06>')

        self.assertEqual(OrgFormat.strdate('2011-11-30T21.06.00', show_time=True),
                         '<2011-11-30 Wed 21:06>')

        self.assertEqual(OrgFormat.strdate('2011-11-30T21.06.02', show_time=True),
                         '<2011-11-30 Wed 21:06>')

        self.assertEqual(OrgFormat.strdate('1899-12-30T21.06.02', show_time=True),
                         '<1899-12-30 Sat 21:06>')

        self.assertEqual(OrgFormat.strdate('2011-11-30 21.06', show_time=True),
                         '<2011-11-30 Wed 21:06>')

        self.assertEqual(OrgFormat.strdate('2011-11-30 21.06.02', show_time=True),
                         '<2011-11-30 Wed 21:06>')

        self.assertEqual(OrgFormat.strdate('2011-11-30 21:06:02', show_time=True),
                         '<2011-11-30 Wed 21:06>')

        self.assertEqual(OrgFormat.strdate('2011-11-30 21:06', show_time=True),
                         '<2011-11-30 Wed 21:06>')

#    def test_strdatetimeiso8601(self):
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30T21.06'),
#                         '<2011-11-30 Wed 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30T21.06.00'),
#                         '<2011-11-30 Wed 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30T21.06.02'),
#                         '<2011-11-30 Wed 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('1899-12-30T21.06.02'),
#                         '<1899-12-30 Sat 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30 21.06'),
#                         '<2011-11-30 Wed 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30 21.06.02'),
#                         '<2011-11-30 Wed 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30 21:06:02'),
#                         '<2011-11-30 Wed 21:06>')
#
#        self.assertEqual(OrgFormat.strdatetimeiso8601('2011-11-30 21:06'),
#                         '<2011-11-30 Wed 21:06>')

    def test_datetimetupleiso8601(self):

        # NOTE: time.strptime() returns a time.struct_time

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2"),
                         time.strptime('2011-01-02', '%Y-%m-%d'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2T3.4"),
                         time.strptime('2011-01-02 03.04', '%Y-%m-%d %H.%M'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2T3.4.5"),
                         time.strptime('2011-01-02 03.04.05', '%Y-%m-%d %H.%M.%S'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2T3:4"),
                         time.strptime('2011-01-02 03.04', '%Y-%m-%d %H.%M'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2T3:4:5"),
                         time.strptime('2011-01-02 03.04.05', '%Y-%m-%d %H.%M.%S'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2 3:4"),
                         time.strptime('2011-01-02 03.04', '%Y-%m-%d %H.%M'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2 3:4:5"),
                         time.strptime('2011-01-02 03.04.05', '%Y-%m-%d %H.%M.%S'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2 3.4"),
                         time.strptime('2011-01-02 03.04', '%Y-%m-%d %H.%M'))

        self.assertEqual(OrgFormat.datetimetupleiso8601("2011-1-2 3.4.5"),
                         time.strptime('2011-01-02 03.04.05', '%Y-%m-%d %H.%M.%S'))

    def test_datetupleutctimestamp(self):

        os.environ['TZ'] = "Europe/Vienna"
        time.tzset()

        self.assertEqual(
            OrgFormat.date(
                OrgFormat.datetupleutctimestamp('20111219T205510Z'), True
            ),
            '<2011-12-19 Mon 21:55>'
        )

        self.assertEqual(
            OrgFormat.date(
                OrgFormat.datetupleutctimestamp('20111219T205510'),
                True
            ),
            '<2011-12-19 Mon 20:55>')

        self.assertEqual(
            OrgFormat.date(OrgFormat.datetupleutctimestamp('20111219'), False),
            '<2011-12-19 Mon>'
        )

        self.assertEqual(
            OrgFormat.date(OrgFormat.datetupleutctimestamp('18991230'), False),
            '<1899-12-30 Sat>'
        )

        with self.assertRaises(TimestampParseException):
            OrgFormat.datetupleutctimestamp('foobar')
        with self.assertRaises(TimestampParseException):
            OrgFormat.datetupleutctimestamp('20111219x205510Z')
        with self.assertRaises(TimestampParseException):
            OrgFormat.datetupleutctimestamp('20111319')

    def test_link(self):
        self.assertEqual(OrgFormat.link('foo/bar'),
                         '[[foo/bar]]')
        self.assertEqual(OrgFormat.link('foo/bar', 'my description'),
                         '[[foo/bar][my description]]')
        self.assertEqual(OrgFormat.link('file:foo/bar/some file.pdf'),
                         '[[file:foo/bar/some%20file.pdf]]')
        self.assertEqual(OrgFormat.link('file:foo/bar/some file.pdf', 'my description'),
                         '[[file:foo/bar/some%20file.pdf][my description]]')
        self.assertEqual(OrgFormat.link('file:foo/bar/some file.pdf', 'my description', replacespaces=False),
                         '[[file:foo/bar/some file.pdf][my description]]')

    def test_contact_mail_mailto_link(self):

        self.assertEqual(OrgFormat.contact_mail_mailto_link('Bob Bobby <bob.bobby@example.com>'),
                         '[[mailto:bob.bobby@example.com][Bob Bobby]]')
        self.assertEqual(OrgFormat.contact_mail_mailto_link('<Bob@example.com>'),
                         '[[mailto:Bob@example.com][Bob@example.com]]')
        self.assertEqual(OrgFormat.contact_mail_mailto_link('Bob@example.com'),
                         '[[mailto:Bob@example.com][Bob@example.com]]')
        self.assertEqual(OrgFormat.contact_mail_mailto_link('foo bar'),
                         '[[mailto:foo bar][foo bar]]')

    def test_newsgroup_link(self):

        self.assertEqual(OrgFormat.newsgroup_link('foo'),
                         '[[news:foo][foo]]')
        self.assertEqual(OrgFormat.newsgroup_link('comp.emacs'),
                         '[[news:comp.emacs][comp.emacs]]')
        with self.assertRaises(AssertionError):
            OrgFormat.newsgroup_link('')

    def test_get_hms_from_sec(self):

        self.assertEqual(OrgFormat.get_hms_from_sec(123), '0:02:03')
        self.assertEqual(OrgFormat.get_hms_from_sec(9999), '2:46:39')
        self.assertEqual(OrgFormat.get_hms_from_sec(9999999), '2777:46:39')

    def test_get_dhms_from_sec(self):

        self.assertEqual(OrgFormat.get_dhms_from_sec(123), '0:02:03')
        self.assertEqual(OrgFormat.get_dhms_from_sec(9999), '2:46:39')
        self.assertEqual(OrgFormat.get_dhms_from_sec(99999), '1d 3:46:39')
        self.assertEqual(OrgFormat.get_dhms_from_sec(12345678), '142d 21:21:18')

    #def test_(self):
        #self.assertEqual(OrgFormat.

# Local Variables:
# End:
