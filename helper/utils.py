from datetime import datetime
from prettytable import PrettyTable
import re
import os


class Printer:
    """
    verbose does overwrite quiet parameter!
    date can be used to add the date (generated with date_format) as prefix to the content
    """
    verbose = False
    quiet = False
    date = False
    date_format = "[%Y-%m-%d %H:%M:%S] "

    @staticmethod
    def print(content, importance=1):
        """
        importance 0: only on verbose
        importance 1: normal (not verbose, not quiet)
        importance 2: high, content will be shown even if quiet flag is set
        """
        prefix = datetime.now().strftime(Printer.date_format) if Printer.date else ''
        if Printer.verbose:
            print(prefix + content)
        elif importance == 1 and not Printer.quiet:
            print(prefix + content)
        elif importance == 2:
            print(prefix + content)


class Result:
    header: list = []
    data: list = list()
    table: PrettyTable = PrettyTable()
    title: str = ''
    alignments: list = []

    def print(self):
        if self.data:
            self.table.title = self.title
            self.table.field_names = self.header
            for row in self.data:
                self.table.add_row(row)
            for alignment in self.alignments:
                self.table.align[alignment[0]] = alignment[1]
            print(self.table)


class FileResult(Result):
    header: list = ["Path", "Source Size", "Destination Size", "Status"]
    data: list = list()
    table: PrettyTable = PrettyTable()
    title: str = "File Backup Status"
    alignments: list = [('Path', 'l'), ('Source Size', 'r'), ('Destination Size', 'r')]


class DatabaseResult(Result):
    header: list = ["Type", "Container", "Database", "Size", "Status"]
    data: list = list()
    table: PrettyTable = PrettyTable()
    title: str = "Database Backup Status"
    alignments: list = [('Type', 'l'), ('Container', 'l'), ('Database', 'l'), ('Size', 'r')]


def secure(content):
    """
    :param content which should be secured
    :return: content without password
    """
    return re.compile(r"--password=.*? ").sub(r"--password=REDACTED ", content)


def remove_timestamp(content):
    """
    :param content which the timestamp should be removed from (mostly mongodb error messages)
    :return: content without timestamp
    """
    return content.split("\t")[1]


# convert bytes to next unit
def convert_size(num):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB'):
        if abs(num) < 1000.0:
            # return "%3.2f %s" % (num, unit)
            return '{:3.2f} {}'.format(num, unit)
        num /= 1000.0
    # return "%.2f YiB" % (num)
    return '{:3.2f} YiB'.format(num)


def convert_time(seconds: int) -> str:
    """
    convert seconds to format sting
    @param seconds: seconds
    @return: format_time_string: formated string
    """
    timeunits = [
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    format_time_string_list = []
    for timeunit, timeunit_seconds in timeunits:
        if seconds >= timeunit_seconds:
            timeunit_value, seconds = divmod(seconds, timeunit_seconds)
            has_s = 's' if is_plural_time(timeunit_value) else ''
            format_time_string_list.append('%s %s%s' % (timeunit_value, timeunit, has_s))

    if len(format_time_string_list) >= 2:
        format_time_string = 'elapsed time: ' + ', '.join(format_time_string_list[:-1]) + ' and ' + str(format_time_string_list[-1])
    else:
        format_time_string = 'elapsed time: ' + str(format_time_string_list[0])

    return format_time_string


def is_plural_time(timeunit_value: int) -> bool:
    """
    Check ich timeunit_value needs plural timeunit format.
    @param timeunit_value: value timeunite
    @return: True or False
    """
    if timeunit_value > 1:
        return True
    else:
        return False


# size of a specific path including all subdirectories
def sizeof(start):
    if os.path.isfile(start):
        return convert_size(os.path.getsize(start))
    size = 0
    for path, folder, files in os.walk(start):
        for file in files:
            file = os.path.join(path, file)
            if not os.path.islink(file):
                size += os.path.getsize(file)
    return convert_size(size) if size else 'empty'
