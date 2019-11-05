#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2019-11-05 13:50:26 vk>

# This file is originally from Memacs: https://github.com/novoid/Memacs
# and was initially written mainly by https://github.com/awieser
# see: https://github.com/novoid/Memacs/blob/master/memacs/lib/orgformat.py
#
# As of 2019-10-31, this file is moved to an independent library since
# multiple projects are using its functions such as:
# https://github.com/novoid/lazyblorg

import time
import datetime
import calendar
import logging
import re
from typing import List, Union, Tuple  # mypy: type checks


class TimestampParseException(Exception):
    """
    Own exception should be raised when
    strptime fails
    """

    def __init__(self, value: Union[ValueError, str]) -> None:
        self.value = value

    def __str__(self) -> str:
        return repr(self.value)


class OrgFormat(object):
    """
    Utility library for providing functions to generate and modify Org mode syntax elements like links, time-stamps, or date-stamps.
    """

    SINGLE_ORGMODE_TIMESTAMP = "([<\[]([12]\d\d\d)-([012345]\d)-([012345]\d) " + \
        "(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Mo|Di|Mi|Do|Fr|Sa|So|Mon|Die|Mit|Don|Fre|Sam|Son) " + \
        "(([01]\d)|(20|21|22|23)):([012345]\d)[>\]])"

    ORGMODE_TIMESTAMP_REGEX = re.compile(SINGLE_ORGMODE_TIMESTAMP + "$")

    ORGMODE_TIMESTAMP_RANGE_REGEX = re.compile(
        SINGLE_ORGMODE_TIMESTAMP + "-(-)?" + SINGLE_ORGMODE_TIMESTAMP + "$")

    @staticmethod
    def orgmode_timestamp_to_datetime(orgtime: str) -> datetime.datetime:
        """
        Returns a datetime object containing the time-stamp of an Org-mode time-stamp:

        OrgFormat.orgmode_timestamp_to_datetime('<1980-12-31 Wed 23:59>')
        -> datetime.datetime(1980, 12, 31, 23, 59, 0, tzinfo=None)

        FIXXME: this function should be modified so that '<1980-12-31 23:59>'
        with a missing day of week is accepted as well.

        @param orgtime: '<YYYY-MM-DD Sun HH:MM>' or an inactive one
        @param return: date time object
        """

        assert isinstance(orgtime, str)

        components = re.match(OrgFormat.ORGMODE_TIMESTAMP_REGEX, orgtime)
        if not components:
            raise TimestampParseException("string could not be parsed as time-stamp of format \"<YYYY-MM-DD Sun " +
                                          "HH:MM>\" (including inactive ones): \"" + orgtime + "\"")

        year = int(components.group(2))    # type: ignore  # FIXXME why
        month = int(components.group(3))   # type: ignore  # FIXXME why
        day = int(components.group(4))     # type: ignore  # FIXXME why
        hour = int(components.group(6))    # type: ignore  # FIXXME why
        minute = int(components.group(9))  # type: ignore  # FIXXME why

        return datetime.datetime(year, month, day, hour, minute, 0)

    @staticmethod
    def apply_timedelta_to_Orgmode_timestamp(orgtime: str, deltahours: Union[int, float]) -> str:
        """
        Returns a string containing an Org-mode time-stamp which has
        delta added in hours. It works also for a time-stamp range
        which uses two strings <YYYY-MM-DD Sun HH:MM> concatenated
        with one or two dashes.

        OrgFormat.apply_timedelta_to_Orgmode_timestamp('<2019-11-05 Tue 23:59>', 1)
        -> '<2019-11-06 Wed 00:59>'

        OrgFormat.apply_timedelta_to_Orgmode_timestamp('<2020-01-01 Wed 01:30>--<2020-01-01 Wed 02:00>', -2.5)
        -> '<2019-12-31 Tue 23:00>--<2019-12-31 Tue 23:30>'

        FIXXME: implement support for inactive date/time ranges

        @param orgtime: '<YYYY-MM-DD Sun HH:MM>'
        @param deltahours: integer/float like, e.g., 3 or -2.5 (in hours)
        @param return: '<YYYY-MM-DD Sun HH:MM>'
        """

        assert isinstance(deltahours, (int, float))
        assert isinstance(orgtime, str)

        range_components = re.match(
            OrgFormat.ORGMODE_TIMESTAMP_RANGE_REGEX, orgtime)

        if range_components:
            return OrgFormat.datetime(
                OrgFormat.orgmode_timestamp_to_datetime(  # type: ignore  # FIXXME why? Argument 1 to "datetime" of "OrgFormat" has incompatible type "datetime"; expected "struct_time"
                    range_components.groups(0)[0]) +  # type: ignore  # FIXXME why
                datetime.timedelta(0, 0, 0, 0, 0, deltahours)) + \
                "--" + \
                OrgFormat.datetime(
                    OrgFormat.orgmode_timestamp_to_datetime(  # type: ignore  # FIXXME why? Argument 1 to "datetime" of "OrgFormat" has incompatible type "datetime"; expected "struct_time"
                        range_components.groups(0)[10]) +  # type: ignore  # FIXXME why
                    datetime.timedelta(0, 0, 0, 0, 0, deltahours))
        else:
            return OrgFormat.datetime(OrgFormat.orgmode_timestamp_to_datetime(orgtime) +  # type: ignore  # FIXXME why? Argument 1 to "datetime" of "OrgFormat" has incompatible type "datetime"; expected "struct_time"
                                      datetime.timedelta(0, 0, 0, 0, 0, deltahours))

    @staticmethod
    def struct_time_to_datetime(tuple_date: time.struct_time) -> datetime.datetime:
        """
        returns a datetime object which was generated from the struct_time parameter
        @param struct_time with possible false day of week
        """

        assert isinstance(tuple_date, time.struct_time)
        return datetime.datetime(tuple_date.tm_year,
                                 tuple_date.tm_mon,
                                 tuple_date.tm_mday,
                                 tuple_date.tm_hour,
                                 tuple_date.tm_min,
                                 tuple_date.tm_sec)

    @staticmethod
    def datetime_to_struct_time(tuple_date: datetime.datetime) -> time.struct_time:
        """
        returns time.struct_time which was generated from the datetime.datetime parameter
        @param datetime object
        """

        assert isinstance(tuple_date, datetime.datetime)
        return tuple_date.timetuple()

    @staticmethod
    def fix_struct_time_wday(tuple_date: time.struct_time) -> time.struct_time:
        """
        returns struct_time timestamp with correct day of week
        @param struct_time with possible false day of week
        """

        assert isinstance(tuple_date, time.struct_time)
        datetimestamp = OrgFormat.struct_time_to_datetime(tuple_date)
        return time.struct_time((datetimestamp.year,
                                 datetimestamp.month,
                                 datetimestamp.day,
                                 datetimestamp.hour,
                                 datetimestamp.minute,
                                 datetimestamp.second,
                                 datetimestamp.weekday(),
                                 0, 0))

    # timestamp = time.struct_time([2013,4,3,10,54,0,0,0,0])  ## wday == 0
    # OrgFormat.date(timestamp)  ## '<2013-04-03 Mon>' -> Mon is wrong for April 3rd 2013
    # OrgFormat.date( OrgFormat.fix_struct_time_wday(timestamp) ) ## '<2013-04-03 Wed>'

    @staticmethod
    def link(link: str, description: str = None, replacespaces: bool = True) -> str:
        """
        returns string of a link in org-format
        @param link: link to i.e. file
        @param description: optional
        @param replacespaces: if True (default), spaces within link are being sanitized
        """

        if replacespaces:
            link = link.replace(" ", "%20")

        if description:
            return "[[" + link + "][" + description + "]]"
        else:
            return "[[" + link + "]]"

    @staticmethod
    def date(tuple_date: Union[time.struct_time, datetime.datetime], show_time: bool = False, inactive: bool = False) -> str:
        """
        returns a date string in org format
        i.e.: * <YYYY-MM-DD Sun>        (for active date-stamps)
              * <YYYY-MM-DD Sun HH:MM>  (for active time-stamps)
        @param tuple_date: has to be of type time.struct_time or datetime
        @param show_time: optional show time also
        @param inactive: (boolean) True: use inactive time-stamp; else use active
        """
        # <YYYY-MM-DD hh:mm>
        assert (tuple_date.__class__ ==
                time.struct_time or tuple_date.__class__ == datetime.datetime)

        local_structtime = None  # : time.struct_time   # Variable annotation syntax is only supported in Python 3.6 and greater

        if isinstance(tuple_date, time.struct_time):
            # fix day of week in struct_time
            local_structtime = OrgFormat.fix_struct_time_wday(tuple_date)
        else:
            # convert datetime to struc_time
            local_structtime = OrgFormat.datetime_to_struct_time(tuple_date)

        if show_time:
            if inactive:
                return time.strftime("[%Y-%m-%d %a %H:%M]", local_structtime)
            else:
                return time.strftime("<%Y-%m-%d %a %H:%M>", local_structtime)
        else:
            if inactive:
                return time.strftime("[%Y-%m-%d %a]", local_structtime)
            else:
                return time.strftime("<%Y-%m-%d %a>", local_structtime)

    @staticmethod
    def inactive_date(tuple_date: Union[time.struct_time, datetime.datetime], show_time: bool = False) -> str:
        """
        returns a date string in org format
        i.e.: * [YYYY-MM-DD Sun]
              * [YYYY-MM-DD Sun HH:MM]
        @param tuple_date: has to be a time.struct_time or datetime
        @param show_time: optional show time also
        """
        # <YYYY-MM-DD hh:mm>
        assert (tuple_date.__class__ ==
                time.struct_time or tuple_date.__class__ == datetime.datetime)

        local_structtime = None  # : time.struct_time   # Variable annotation syntax is only supported in Python 3.6 and greater

        if isinstance(tuple_date, time.struct_time):
            # fix day of week in struct_time
            local_structtime = OrgFormat.fix_struct_time_wday(tuple_date)
        else:
            # convert datetime to struc_time
            local_structtime = OrgFormat.datetime_to_struct_time(tuple_date)

        if show_time:
            return time.strftime(
                "[%Y-%m-%d %a %H:%M]",
                OrgFormat.fix_struct_time_wday(local_structtime))
        else:
            return time.strftime("[%Y-%m-%d %a]", OrgFormat.fix_struct_time_wday(local_structtime))

    @staticmethod
    def datetime(tuple_datetime: time.struct_time, inactive: bool = False) -> str:
        """
        returns a date+time string in org format
        wrapper for OrgFormat.date(show_time=True)

        @param tuple_datetime has to be a time.struct_time
        @param inactive: (boolean) True: use inactive time-stamp; else use active
        """
        return OrgFormat.date(tuple_datetime, show_time=True)

    @staticmethod
    def inactive_datetime(tuple_datetime: time.struct_time) -> str:
        """
        returns a date+time string in org format
        wrapper for OrgFormat.inactive_date(show_time=True)

        @param tuple_datetime has to be a time.struct_time
        """
        return OrgFormat.inactive_date(tuple_datetime, show_time=True)

    @staticmethod
    def daterange(begin: time.struct_time, end: time.struct_time) -> str:
        """
        returns a date range string in org format

        @param begin,end: has to be a time.struct_time
        """
        assert isinstance(begin, time.struct_time)
        assert isinstance(end, time.struct_time)
        return "%s--%s" % (OrgFormat.date(begin, False),
                           OrgFormat.date(end, False))

    @staticmethod
    def datetimerange(begin: time.struct_time, end: time.struct_time) -> str:
        """
        returns a date range string in org format

        @param begin,end: has to be a time.struct_time
        """
        assert isinstance(begin, time.struct_time)
        assert isinstance(end, time.struct_time)
        return "%s--%s" % (OrgFormat.date(begin, True),
                           OrgFormat.date(end, True))

    @staticmethod
    def utcrange(begin_tupel: time.struct_time, end_tupel: time.struct_time) -> str:
        """
        returns a date(time) range string in org format
        if both parameters do not contain time information,
        utcrange is same as daterange, else it is same as datetimerange.

        @param begin,end: has to be a a time.struct_time
        """

        if begin_tupel.tm_sec == 0 and \
                begin_tupel.tm_min == 0 and \
                begin_tupel.tm_hour == 0 and \
                end_tupel.tm_sec == 0 and \
                end_tupel.tm_min == 0 and \
                end_tupel.tm_hour == 0:

            return OrgFormat.daterange(begin_tupel, end_tupel)
        else:
            return OrgFormat.datetimerange(begin_tupel, end_tupel)

    @staticmethod
    def strdate(date_string: str, inactive: bool = False) -> str:
        """
        returns a date string in org format
        i.e.: * <YYYY-MM-DD Sun>
        @param date-string: has to be a str in following format:  YYYY-MM-DD
        @param inactive: (boolean) True: use inactive time-stamp; else use active
        """
        assert isinstance(date_string, str)
        tuple_date = OrgFormat.datetupeliso8601(date_string)
        if inactive:
            return OrgFormat.inactive_date(tuple_date, show_time=False)
        else:
            return OrgFormat.date(tuple_date, show_time=False)

    @staticmethod
    def strdatetime(datetime_string: str, inactive: bool = False) -> str:
        """
        returns a date string in org format
        i.e.: * <YYYY-MM-DD Sun HH:MM>
        @param date-string: has to be a str in
                           following format: YYYY-MM-DD HH:MM
        @param inactive: (boolean) True: use inactive time-stamp; else use active
        """
        assert isinstance(datetime_string, str)
        try:
            tuple_date = time.strptime(datetime_string, "%Y-%m-%d %H:%M")
        except ValueError as e:
            raise TimestampParseException(e)
        if inactive:
            return OrgFormat.inactive_date(tuple_date, show_time=True)
        else:
            return OrgFormat.date(tuple_date, show_time=True)

    @staticmethod
    def strdatetimeiso8601(datetime_string: str) -> str:
        """
        returns a date string in org format
        i.e.: * <YYYY-MM-DD Sun HH:MM>
        @param date-string: has to be a str
                            in following format: YYYY-MM-DDTHH.MM.SS or
                                                 YYYY-MM-DDTHH.MM
        """
        assert isinstance(datetime_string, str)
        tuple_date = OrgFormat.datetimetupeliso8601(datetime_string)
        return OrgFormat.date(tuple_date, show_time=True)

    @staticmethod
    def datetimetupeliso8601(datetime_string: str) -> time.struct_time:
        """
        returns a time_tupel
        @param datetime_string: YYYY-MM-DDTHH.MM.SS or
                                YYYY-MM-DDTHH.MM
        """
        assert isinstance(datetime_string, str)
        # maybe insert assert statement for datetime_string having length of 16 or 19 only
        try:
            if len(datetime_string) == 16:  # YYYY-MM-DDTHH.MM
                return time.strptime(datetime_string, "%Y-%m-%dT%H.%M")
            elif len(datetime_string) == 19:  # YYYY-MM-DDTHH.MM.SS
                return time.strptime(datetime_string, "%Y-%m-%dT%H.%M.%S")
        except ValueError as e:
            raise TimestampParseException(e)
        assert(False)  # dead code for assuring mypy that everything
                       # above is handled by a return or raising
                       # exception statement

    @staticmethod
    def datetupeliso8601(datetime_string: str) -> time.struct_time:
        """
        returns a time_tupel
        @param datetime_string: YYYY-MM-DD
        """
        assert isinstance(datetime_string, str)
        try:
            return time.strptime(datetime_string, "%Y-%m-%d")
        except ValueError as e:
            raise TimestampParseException(e)

    @staticmethod
    def datetupelutctimestamp(datetime_string: str) -> time.struct_time:
        """
        returns a time_tupel
        @param datetime_string: YYYYMMDDTHHMMSSZ or
                                YYYYMMDDTHHMMSS or
                                YYYYMMDD
        """
        assert isinstance(datetime_string, str)
        string_length = len(datetime_string)

        try:
            if string_length == 16:
                # YYYYMMDDTHHMMSSZ
                return time.localtime(
                    calendar.timegm(
                        time.strptime(datetime_string, "%Y%m%dT%H%M%SZ")))
            elif string_length == 15:
                # YYYYMMDDTHHMMSS
                return time.strptime(datetime_string, "%Y%m%dT%H%M%S")
            elif string_length == 8:
                # YYYYMMDD
                return time.strptime(datetime_string, "%Y%m%d")
            elif string_length == 27:
                # 2011-11-02T14:48:54.908371Z
                datetime_string = datetime_string.split(".")[0] + "Z"
                return time.localtime(
                    calendar.timegm(
                        time.strptime(datetime_string,
                                      "%Y-%m-%dT%H:%M:%SZ")))
            else:
                logging.error("string has no correct format: %s",
                              datetime_string)
        except ValueError as e:
            raise TimestampParseException(e)
        assert(False)  # dead code for assuring mypy that everything
                       # above is handled by a return or raising
                       # exception statement

    @staticmethod
    def contact_mail_mailto_link(contact_mail_string: str) -> str:
        """
        @param contact_mailto_string: possibilities:
        - "Bob Bobby <bob.bobby@example.com>" or
        - <Bob@example.com>" or
        - Bob@example.com

        @return:
        - [[mailto:bob.bobby@example.com][Bob Bobby]]
        - [[mailto:bob.bobby@example.com][bob.bobby@excample.com]]
        """
        delimiter = contact_mail_string.find("<")
        if delimiter != -1:
            name = contact_mail_string[:delimiter].strip()
            mail = contact_mail_string[delimiter + 1:][:-1].strip()
            if delimiter == 0:
                return "[[mailto:" + mail + "][" + mail + "]]"
            return "[[mailto:" + mail + "][" + name + "]]"

        else:
            return "[[mailto:" + contact_mail_string + "][" + contact_mail_string + "]]"

    @staticmethod
    def newsgroup_link(newsgroup_string: str) -> str:
        """
        @param newsgroup_string: Usenet name
            i.e: news:comp.emacs
        @param return: [[news:comp.emacs][comp.emacs]]
        """
        return "[[news:" + newsgroup_string + "][" + newsgroup_string + "]]"

    @staticmethod
    def get_hms_from_sec(sec: int) -> str:
        """
        Returns a string of hours:minutes:seconds from the seconds given.

        @param sec: seconds
        @param return: h:mm:ss as string
        """

        assert isinstance(sec, int)

        seconds = sec % 60
        minutes = (sec // 60) % 60
        hours = (sec // (60 * 60))

        return str(hours) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

    @staticmethod
    def get_dhms_from_sec(sec: int) -> str:
        """
        Returns a string of days hours:minutes:seconds (like
        "9d 13:59:59") from the seconds given. If days is zero, omit
        the part of the days (like "13:59:59").

        @param sec: seconds
        @param return: xd h:mm:ss as string
        """

        assert isinstance(sec, int)

        seconds = sec % 60
        minutes = (sec // 60) % 60
        hours = (sec // (60 * 60)) % 24
        days = (sec // (60 * 60 * 24))

        if days > 0:
            daystring = str(days) + "d "
        else:
            daystring = ''
        return daystring + str(hours) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2)


# Local Variables:
# End:
