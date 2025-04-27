"""
provides helpful functions for date handling.

provided functions:
get_start_of_day()
get_start_of_week()
is_same_date()
is_today()
count_days_between_dates()
count_weeks_between_dates()
count_days_till_today()
count_weeks_till_today()
get_last_month()
parse_string_to_datetime()
"""
import logging
from datetime import datetime, timedelta
from helper import const_handler

const = const_handler.ConstHandler()
logging.basicConfig(level=const.get_logger_log_level(), format=const.get_logger_log_format(),
                    filename=const.get_logger_log_filename(), filemode=const.get_logger_log_filemode(), force=True)

def get_start_of_day(date):
    """
    returns the start of day of the given date by setting hour, minutes, seconds and microsecond to 0

    :param date: datetime

    :return: datetime
    """
    adjusted_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    logging.debug("input date: {original}, adjusted_date: {changed}".format(original=date, changed=adjusted_date))
    return adjusted_date

def get_start_of_week(date):
    """
    returns the date for monday

    :param date: datetime

    :return: datetime
    """
    adjusted_date = get_start_of_day(date - timedelta(days=date.weekday()))
    logging.debug("input date: {original}, adjusted_date: {changed}".format(original=date, changed=adjusted_date))
    return adjusted_date

def is_same_date(date1, date2):
    """
    compares two dates, ignores the time difference

    :param date1:  datetime
    :param date2:  datetime

    :return:  boolean
    """
    same_date = get_start_of_day(date1) == get_start_of_day(date2)
    logging.debug(
        "input date: {original1} and {original2}, is same date?: {same_date}".format(original1=date1, original2=date2,
                                                                                   same_date=same_date))
    return same_date

def is_today(date):
    """
    checks if date is today

    :param date: datetime

    :return: boolean
    """
    return is_same_date(date, datetime.now())

def count_days_between_dates(start_date, end_date):
    """
    counts the days between two dates

    :param start_date: datetime
    :param end_date: datetime

    :return: integer, 0 or +
    """
    date_difference = abs((get_start_of_day(end_date) - get_start_of_day(start_date)).days)
    logging.debug("input date: {original1} and {original2}, days between: {difference}".format(original1=start_date,
                                                                                             original2=end_date,
                                                                                             difference=date_difference))
    return date_difference

def count_weeks_between_dates(start_date, end_date):
    """
    counts the weeks between two dates

    :param start_date: datetime
    :param end_date: datetime

    :return: integer, 0 or +
    """
    date_difference = count_days_between_dates(get_start_of_week(start_date), get_start_of_week(end_date))
    date_difference_weeks = int(date_difference / 7) if date_difference != 0 else 0
    logging.debug(
        "input date: {original1} and {original2}, days between: {difference_day}, weeks between: {difference_weeks}".format(
            original1=start_date,
            original2=end_date,
            difference_day=date_difference,
            difference_weeks=date_difference_weeks))
    return date_difference_weeks

def count_days_till_today(date):
    """
    counts the days till today

    :param date: datetime

    :return: integer, 0 or +
    """
    return count_days_between_dates(date, datetime.now())

def count_weeks_till_today(date):
    """
    counts the weeks till today

    :param date: datetime

    :return: integer, 0 or +
    """
    return count_weeks_between_dates(date, datetime.now())

def get_last_month(date):
    """
    get the 1st of the last month of the given date

    :param date: datetime

    :return: datetime
    """
    cleaned_date = get_start_of_day(date)
    last_month = cleaned_date.replace(day=1) - timedelta(days=1) # set to first day of the month and reduce one day
    last_month = last_month.replace(day=1) # set to first day of the past month
    return last_month

def parse_string_to_datetime(string_date):
    """
    convert string date to datetime by format "yyyy-mm-dd hh:mm:ss.ffffff"

    :param string_date:

    :return: datetime
    """
    try:
        return datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            logging.error('could not parse string_date: {}, return None'.format(string_date))
    return None
