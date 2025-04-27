"""
provides the Habit object and WrongUserException
"""
import logging
from datetime import datetime, timedelta
import json
from helper import const_handler
from helper import time_handler


class WrongUserException(Exception):
    """
    custom error if the given user-id does not match the user-if of the habit
    """
    def __init__(self, message):
        super().__init__(message)


# noinspection SqlDialectInspection
class Habit:
    """
    Habit Object, takes: habit_id, user_id, title, description, created, last_break, last_checked, streak,
    longest_streak, periodicity and break_history when called
    automatically updates last_break, break_history and streak when called

    provided functions:
    get_id()
    get_title()
    get_description()
    get_created()
    get_last_break()
    get_last_checked()
    get_streak()
    get_longest_streak()
    get_periodicity()
    get_break_history()
    get_last_months_breaks()

    set_title()
    set_description()

    check()
    is_checked()

    create_update_query()
    """
    __id__ = ''
    __title__ = ''
    __description__ = ''
    __created__ = ''
    __last_break__ = ''
    __last_checked__ = ''
    __streak__ = 0
    __longest_streak__ = 0
    __periodicity__ = ''
    __break_history__ = {}
    __user_id__ = ''

    const = const_handler.ConstHandler()
    logging.basicConfig(level=const.get_logger_log_level(), format=const.get_logger_log_format(),
                        filename=const.get_logger_log_filename(), filemode=const.get_logger_log_filemode(), force=True)

    def __init__(self, habit_id, user_id, title, description, periodicity, created, last_break, last_checked,
                 streak, longest_streak, break_history):
        """
        init function, creates habit-object from parameters
        updates history, last_break and break_history when called
        parses break_history string from parameters into dictionary

        :param habit_id: integer
        :param user_id: string
        :param title: string
        :param description: string
        :param created: string
        :param last_break: string
        :param last_checked: string
        :param streak: integer
        :param longest_streak: integer
        :param periodicity: string
        :param break_history: string

        :raise: NameError if periodicity of the habit does not match the values from const
        :raise: ValueError if created, last_checked or last_break is not parseable
        """
        self.__id__ = habit_id
        self.__user_id__ = user_id
        self.__title__ = title
        self.__description__ = description
        self.__created__ = created
        self.__last_break__ = last_break
        self.__last_checked__ = last_checked
        self.__streak__ = streak
        self.__longest_streak__ = longest_streak
        self.__periodicity__ = periodicity
        try:
            self.__break_history__ = json.loads(break_history)
        except ValueError:
            logging.error('could not parse break_history string to dictionary for habit-id: {}'.format(habit_id))
            self.__break_history__ = {}

        # calculate break_history, set last_break and set streak
        today = time_handler.get_start_of_day(datetime.today())
        yesterday = today - timedelta(days=1)

        # get last_checked or created if it's not set yet, create a datetime object of it and set it to start of day
        _last_checked_date_parsed_ = time_handler.parse_string_to_datetime(
            self.__last_checked__ if len(self.__last_checked__) != 0 else self.__created__)
        if _last_checked_date_parsed_ is None:
            if len(self.__last_checked__) == 0:
                raise ValueError(
                    'created could not be parsed for habit: {}, please contact the admin.'.format(
                        habit_id))
            else:
                raise ValueError(
                    'last_checked could not be parsed for habit: {}, please contact the admin.'.format(
                        habit_id))

        last_checked_date = time_handler.get_start_of_day(_last_checked_date_parsed_)
        last_checked_days_till_today = time_handler.count_days_till_today(last_checked_date)

        # get last_break if it exists, create a datetime object and set it to start of day or None
        _last_break_date_parse_ = None
        if len(self.__last_break__) != 0:
            _last_break_date_parse_ = time_handler.parse_string_to_datetime(self.__last_break__)
            if _last_break_date_parse_ is None:
                raise ValueError(
                    'last_break could not be parsed for habit: {}, please contact the admin.'.format(habit_id))

        last_break_date = time_handler.get_start_of_day(
            _last_break_date_parse_) if _last_break_date_parse_ is not None else None

        if last_break_date is None:
            last_interaction_date = last_checked_date
        else:
            last_break_days_till_today = time_handler.count_days_till_today(last_break_date)

            if last_checked_days_till_today <= last_break_days_till_today:
                last_interaction_date = last_checked_date
            else:
                last_interaction_date = last_break_date

        # the point where I regretted making the break_history...
        # calculate the breaks from last interaction till today, daily or weekly intervals
        if self.__periodicity__ == self.const.get_periodicity_daily():
            emergency_break = 0 # just in case
            # start counting the day after last interaction because it should already be calculated
            # sideeffect: the day it is created counts as 'trial' and is not counted into breaks
            last_interaction_date = last_interaction_date + timedelta(days=1)

            # last_interaction_date < today not last_interaction_date <= today because today does not count as a break
            while emergency_break <= 3650 and last_interaction_date < today:
                # needs to be a string to make it compatible with json
                history_year = str(last_interaction_date.year)
                history_month = str(last_interaction_date.month)
                emergency_break += 1  # to prevent infinite loop, equals to ~10 years

                # create break-history entries if not exist
                if self.__break_history__.get(history_year) is None:
                    self.__break_history__[history_year] = {}
                if self.__break_history__.get(history_year).get(history_month) is None:
                    self.__break_history__[history_year][history_month] = 0

                self.__break_history__[history_year][history_month] += 1
                last_interaction_date = last_interaction_date + timedelta(days=1)

            # if emergency_break != 0 there were breaks calculated so last_break and streak needs to be updated
            if emergency_break != 0:
                self.__last_break__ = str(yesterday)
                self.__streak__ = 0

        elif self.__periodicity__ == self.const.get_periodicity_weekly():
            emergency_break = 0 # just in case
            monday = time_handler.get_start_of_week(yesterday)
            # start counting the monday after last interaction because it should already be calculated
            # sideeffect: the week it is created counts as 'trial' and is not counted into breaks
            last_interaction_date = time_handler.get_start_of_week(last_interaction_date) + timedelta(days=7)

            # last_interaction_date < monday not last_interaction_date <= monday because this week does not count as a break
            while emergency_break <= 420 and last_interaction_date < monday:
                # needs to be a string to make it compatible with json
                history_year = str(last_interaction_date.year)
                history_month = str(last_interaction_date.month)
                emergency_break += 1  # to prevent infinite loop, equals to ~10 years

                # create break-history entries if not exist
                if self.__break_history__.get(history_year) is None:
                    self.__break_history__[history_year] = {}
                if self.__break_history__.get(history_year).get(history_month) is None:
                    self.__break_history__[history_year][history_month] = 0

                self.__break_history__[history_year][history_month] += 1
                last_interaction_date = last_interaction_date + timedelta(days=7)  # add a week to last_interaction_date

            # if emergency_break != 0 there were breaks calculated so last_break and streak needs to be updated
            if emergency_break != 0:
                self.__last_break__ = str(yesterday)
                self.__streak__ = 0

        else:
            raise NameError('unknown periodicity, does not match any from const_handler: {}. please contact the admin.'
                            .format(self.__periodicity__))

    def get_id(self):
        """
        :return: user_id
        """
        return self.__id__

    def get_title(self):
        """
        :return: title
        """
        return self.__title__

    def get_description(self):
        """
        :return: description
        """
        return self.__description__

    def get_created(self):
        """
        :return: created date as string
        """
        return self.__created__

    def get_last_break(self):
        """
        :return: last break date as string
        """
        return self.__last_break__

    def get_last_checked(self):
        """
        :return: last checked date as string
        """
        return self.__last_checked__

    def get_streak(self):
        """
        :return: streak
        """
        return self.__streak__

    def get_longest_streak(self):
        """
        :return: longest streak
        """
        return self.__longest_streak__

    def get_periodicity(self):
        """
        :return: periodicity
        """
        return self.__periodicity__

    def get_break_history(self):
        """
        break history format: {'yyyy':{'mm':breaks(int)}}

        :return: break history as a dictionary
        """
        return self.__break_history__

    def get_last_months_breaks(self):
        """
        takes info from break history

        :return: number of months breaks for the last month or 0
        """
        last_month_date = time_handler.get_last_month(datetime.today())  # get 1st of the last month
        # needs to be a string to make it compatible with json
        last_month_year = str(last_month_date.year)
        last_month_month = str(last_month_date.month)

        last_month_year_history = self.__break_history__.get(last_month_year)

        # check if the year exist in the history
        if last_month_year_history is not None:
            last_month_month_of_year_history = last_month_year_history.get(last_month_month)

            # check if the month exist in the history
            if last_month_month_of_year_history is not None:
                return last_month_month_of_year_history

        return 0

    def set_title(self, new_title, user_id):
        """
        changes the title of a habit, requires user_id to prevent accidental user-collisions

        :param new_title:
        :param user_id:

        :raise: WrongUserException if mismatch user_id
        """
        if user_id == self.__user_id__:
            self.__title__ = new_title
        else:
            raise WrongUserException('given user_id does not match user-id in habit')

    def set_description(self, new_description, user_id):
        """
        changes the description of a habit, requires user_id to prevent accidental user-collisions

        :param new_description:
        :param user_id:

        :raise: WrongUserException in mismatch cuser_id
        """
        if user_id == self.__user_id__:
            self.__description__ = new_description
        else:
            raise WrongUserException('given user_id does not match user-id in habit')

    def check(self, user_id):
        """
        checks the habit, requires user_id to prevent accidental user-collisions

        :param user_id:

        :raise: WrongUserException if mismatch user_id
        """
        if user_id == self.__user_id__:
            if not self.is_checked():
                self.__last_checked__ = str(datetime.today())
                self.__streak__ += 1
                if self.__streak__ > self.__longest_streak__:
                    self.__longest_streak__ = self.__streak__
        else:
            raise WrongUserException('given user_id does not match user-id in habit')

    def is_checked(self):
        """
        returns true if habit is checked

        :return: boolean

        :raise: NameError if periodicity of the habit does not match the values from const
        """
        today_detailed = datetime.today()
        today = time_handler.get_start_of_day(today_detailed)
        monday = time_handler.get_start_of_week(today)

        if self.__last_checked__ == '':
            return False
        else:
            try:
                last_checked = time_handler.parse_string_to_datetime(self.__last_checked__)

                if self.__periodicity__ == self.const.get_periodicity_daily():
                    if time_handler.is_today(last_checked):
                        return True
                elif self.__periodicity__ == self.const.get_periodicity_weekly():
                    if time_handler.is_same_date(monday, time_handler.get_start_of_week(last_checked)):
                        return True
                else:
                    # critical error, it is not possible to handle any habits if periodicity is unknown
                    raise NameError(
                        'unknown periodicity, does not match any from const_handler: {}. please contact the admin.'
                        .format(self.__periodicity__))
                return False
            except ValueError:
                logging.error('could not parse last_checked, count this habit as checked and overwrite last_checked')
                self.__last_checked__ = str(datetime.today())
                self.__streak__ += 1
                if self.__streak__ > self.__longest_streak__:
                    self.__longest_streak__ = self.__streak__
                return True

    def create_update_query(self, user_id):
        """
        creates update query for habit, requires user_id to prevent accidental user-collisions

        :param user_id:
        :return: dictionary with 'query' for the sql-query-string and 'values' for the tuple of values

        :raise: WrongUserException if mismatch user_id
        """
        if user_id == self.__user_id__:
            query_string = '''UPDATE habits SET title = ?, description = ?,
                              last_break = ?, last_checked = ?, streak = ?,
                              longest_streak = ?, break_history = ? WHERE id = ? AND user_id = ?'''
            query_values = (self.__title__, self.__description__, self.__last_break__, self.__last_checked__,
                            self.__streak__, self.__longest_streak__, json.dumps(self.__break_history__),
                            self.__id__, self.__user_id__)
            return {
                'query': query_string,
                'values': query_values,
            }
        else:
            raise WrongUserException('given user_id does not match user-id in habit')
