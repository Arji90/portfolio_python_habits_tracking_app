"""
provides the Habits object, MissingUserIdException and HabitDoesNotExistException
"""
import sqlite3
import logging
from datetime import datetime
from helper import const_handler, time_handler
from habits import habit


def __habit_id_compare__(habit_id_a, habit_id_b):
    """
    static helper function to compare two habit_ids after issues with string and int
    database uses auto-incrementing integer as key, so int is default

    :param habit_id_a: string or int
    :param habit_id_b: string or int

    :return: boolean

    :raise: ValueError if habit_id_a or habit_id_b are not parseable into integer
    """
    return int(habit_id_a) == int(habit_id_b)

class MissingUserIdException(Exception):
    """
    custom error if the given user-id does not match the user-if of the habit
    """
    def __init__(self):
        super().__init__('no user_id has been provided, please call "select_user(user_id)"')

class HabitDoesNotExistException(Exception):
    """
    custom error if the given habit-id does not exist
    """
    def __init__(self, habit_id):
        super().__init__('No habit with the id: {} could be found'.format(habit_id))

# noinspection SqlDialectInspection
class Habits:
    """
    Habits object, creates db if it doesn't exist yet when initiated.

    provided functions:
    select_user()
    has_user_id()
    get_periodicities()
    add_habit()
    edit_habit()
    delete_habit()
    delete_all_habits_for_user()
    check_habit()
    get_habits()
    get_habits_by_periodicity()
    get_habits_by_streak()
    get_habits_by_longest_streak()
    get_habits_by_break()
    get_habits_by_last_month_breaks()
    get_habits_by_created()
    get_unchecked_habits()
    """
    const = const_handler.ConstHandler()
    logging.basicConfig(level=const.get_logger_log_level(), format=const.get_logger_log_format(),
                        filename=const.get_logger_log_filename(), filemode=const.get_logger_log_filemode(), force=True)

    def __sql_call__(self, query, params=(), fetch=False):
        """
        function for sql-handling

        :param query: sql query as string
        :param params: tuple of parameters to pass to sql query
        :param fetch: boolean flag to fetch results from sql query

        :return: tuple of results from sql query if fetch is true, else return True
        """
        return_value = True

        connection = sqlite3.connect(self.const.get_habits_db_name().strip() + '.db')
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        if fetch:
            return_value = cursor.fetchall()
        elif query.startswith('INSERT'):
            return_value = cursor.lastrowid # returns the new users-id when created
        connection.close()
        return return_value

    def __init__(self):
        """initial function, creates the database if it doesn't exist yet."""
        query = '''CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, 
                    title TEXT NOT NULL, description TEXT, 
                    periodicity TEXT NOT NULL, created_at TEXT NOT NULL,
                    deactivated BIT DEFAULT 0, last_break TEXT, last_checked TEXT,
                    streak INTEGER DEFAULT 0, longest_streak INTEGER DEFAULT 0, break_history TEXT)'''

        self.__sql_call__(query)

    __user_id__ = None
    __habits__ = None

    def __is_test_user__(self):
        return self.__user_id__ == self.const.get_user_test_id_a() or self.__user_id__ == self.const.get_user_test_id_b()

    def __update_habits_list__(self):
        """
        updates habits-list from DB

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if not self.__is_test_user__():
            if self.has_user_id():
                query = '''SELECT id, user_id, title, description, periodicity, created_at, last_break, last_checked, 
                streak, longest_streak, break_history FROM habits WHERE user_id = ? AND deactivated = 0'''
                result = self.__sql_call__(query, (self.__user_id__,), True)
                logging.debug(result)

                self.__habits__ = []
                for habit_data in result:
                    # surely nothing can go wrong here
                    habit_object = habit.Habit(habit_data[0], habit_data[1], habit_data[2], habit_data[3],
                                                       habit_data[4], habit_data[5], habit_data[6], habit_data[7],
                                                       habit_data[8], habit_data[9], habit_data[10])
                    logging.debug(habit_object.__dict__)
                    self.__habits__.append(habit_object)
            else:
                raise MissingUserIdException()

    def __save_habit__(self, habit_id):
        """
        writes the habit-data with the given habit-id to the database

        :param habit_id: integer

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise HabitDoesNotExistException when the given habit_id does not exist
        """
        if not self.__is_test_user__():
            if self.has_user_id():
                found_habit = False

                for current_habit in self.__habits__:
                    if __habit_id_compare__(current_habit.get_id(), habit_id):
                        found_habit = True
                        try:
                            query_data = current_habit.create_update_query(self.__user_id__)
                            self.__sql_call__(query_data['query'], query_data['values'])
                        except habit.WrongUserException:
                            # prevents overwriting habits from other users
                            logging.error('habit with habit-id {habit} does not exist for user with user-id: {user}'.format(habit = habit_id, user = self.__user_id__))

                if not found_habit:
                    raise HabitDoesNotExistException(habit_id)
            else:
                raise MissingUserIdException()

    def __save_all_habits__(self):
        """
        writes all habits into the database

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if not self.__is_test_user__():
            if self.has_user_id():
                for current_habit in self.__habits__:
                    try:
                        query_data = current_habit.create_update_query(self.__user_id__)
                        self.__sql_call__(query_data.query, query_data.values)
                    except habit.WrongUserException:
                        # prevents overwriting habits from other users
                        logging.error('habit with habit-id {habit} does not exist for user with user-id: {user}'.format(
                            habit=current_habit.get_id(), user=self.__user_id__))
            else:
                raise MissingUserIdException()

    def select_user(self, user_id, test_habits=None):
        """
        set user_id and calls __update_habits_list__()

        :param user_id: string
        :param test_habits: list of habits for automated tests only

        :raise: ValueError if test_habits is not given while using a test-user
        """
        self.__user_id__ = user_id
        logging.debug('switch to user with user_id: {}'.format(user_id))
        if self.__is_test_user__():
            if type(test_habits) is list:
                self.__habits__ = test_habits
            else:
                raise ValueError('no test_habits are given or is not a list')
        else:
            self.__update_habits_list__()

    def has_user_id(self):
        return self.__user_id__ is not None

    def get_periodicities(self):
        """
        get a dictionary of all periodicities available so const_handler is not needed for it separately
        (I'm aware it's not used in habits_terminal_interface.py, the function is more for a theoretical future user)

        :return: dictionary
        """
        return {
            'daily': self.const.get_periodicity_daily(),
            'weekly': self.const.get_periodicity_weekly()
        }

    def add_habit(self, title, description, periodicity):
        """
        creates a new habit, adds it to the db and updates the list of habits after.

        :param title: string
        :param description: string
        :param periodicity: string

        :return: tuple of sql-query and query values, if user_id is a test-user

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise: NameError when the given periodicity is not matching from const_handler (call get_periodicities())
        """
        if self.has_user_id():
            if periodicity == self.const.get_periodicity_daily() or periodicity == self.const.get_periodicity_weekly():
                query_string = '''INSERT INTO habits (user_id, title, description, periodicity, created_at, last_break, 
                        last_checked, streak, longest_streak, break_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                query_values = (self.__user_id__, title, description, periodicity, datetime.now(), '', '', 0, 0, '{}')

                if not self.__is_test_user__():
                    logging.debug(query_string)
                    logging.debug(query_values)
                    self.__sql_call__(query_string, query_values)
                    self.__update_habits_list__() # update habits list with all new data, especially the ids
                else:
                    return query_string, query_values
            else:
                raise NameError('periodicity must be {daily_val} for daily or {weekly_val} for weekly periodicity'
                                 .format(daily_val=self.const.get_periodicity_daily(), weekly_val=self.const.get_periodicity_weekly()))
        else:
            raise MissingUserIdException()

    def edit_habit(self, habit_id, title = '', description = ''):
        """
        updates title and description of the habit with the given habit_id.

        :param habit_id:
        :param title:
        :param description:

        :return: updated habit, if user_id is a test-user

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise HabitDoesNotExistException when the given habit_id does not exist
        """
        if self.has_user_id():
            found_habit = False

            for current_habit in self.__habits__:
                if __habit_id_compare__(current_habit.get_id(), habit_id):
                    if len(title) > 0:
                        current_habit.set_title(title, self.__user_id__)
                    if len(description) > 0:
                        current_habit.set_description(description, self.__user_id__)

                    if not self.__is_test_user__():
                        logging.debug('change title to: {}'.format(current_habit.get_title()))
                        logging.debug('change description to: {}'.format(current_habit.get_description()))
                        self.__save_habit__(current_habit.get_id())
                        self.__update_habits_list__()
                        found_habit = True
                    else:
                        return current_habit

            if not found_habit:
                raise HabitDoesNotExistException(habit_id)
        else:
            raise MissingUserIdException()

    def delete_habit(self, habit_id):
        """
        deletes the habit with the given habit_id.

        :param habit_id:

        :return: tuple of sql-query and query values, if user_id is a test-user

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise HabitDoesNotExistException when the given habit_id does not exist
        """
        if self.has_user_id():
            found_habit = False

            for current_habit in self.__habits__:
                if __habit_id_compare__(current_habit.get_id(), habit_id):
                    found_habit = True
                    query_string = '''UPDATE habits SET deactivated = ? WHERE id = ? AND user_id = ?'''
                    query_values = (1, habit_id, self.__user_id__)

                    if not self.__is_test_user__():
                        logging.debug(query_string)
                        logging.debug(query_values)
                        self.__sql_call__(query_string, query_values)
                        self.__update_habits_list__()
                    else:
                        return query_string, query_values
            if not found_habit:
                raise HabitDoesNotExistException(habit_id)
        else:
            raise MissingUserIdException()

    def delete_all_habits_for_user(self, user_id):
        """
        function deletes all habits with a given user-id
        use with caution, no protections are implemented here like permissions

        :return: tuple of sql-query and query values, if user_id is a test-user

        :param user_id: any userid
        """
        query_string = '''UPDATE habits SET deactivated = ? WHERE user_id = ?'''
        query_values = (1, user_id)

        if not self.__is_test_user__():
            logging.debug(query_string)
            logging.debug(query_values)
            self.__sql_call__(query_string, query_values)
            if user_id == self.__user_id__:
                self.__update_habits_list__()
        else:
            return query_string, query_values

    def check_habit(self, habit_id):
        """
        checks the habit with the given habit_id as finished

        :param habit_id:

        :return: updated habit, if user_id is a test-user

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise HabitDoesNotExistException when the given habit_id does not exist
        """
        if self.has_user_id():
            found_habit = False

            for current_habit in self.__habits__:
                if __habit_id_compare__(current_habit.get_id(), habit_id):
                    found_habit = True
                    current_habit.check(self.__user_id__)

                    if not self.__is_test_user__():
                        self.__save_habit__(current_habit.get_id())
                        self.__update_habits_list__()
                    else:
                        return current_habit

            if not found_habit:
                raise HabitDoesNotExistException(habit_id)
        else:
            raise MissingUserIdException()

    def get_habits(self, force_update=False):
        """
        return all current habits

        :param force_update: boolean - reload habits from database (default false)

        :return: tuple of habits

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()
            return tuple(self.__habits__)
        else:
            raise MissingUserIdException()

    def get_habits_by_periodicity(self, periodicity, force_update=False):
        """
        return filtered list by given periodicity

        :param periodicity: string
        :param force_update: boolean - reload habits from database (default false)

        :return: tuple of habits

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise NameError when given periodicity does not match for const_handler (call get_periodicities())
        """
        if self.has_user_id():
            if periodicity == self.const.get_periodicity_daily() or periodicity == self.const.get_periodicity_weekly():
                if force_update:
                    self.__update_habits_list__()

                result_list = []

                for current_habit in self.__habits__:
                    if current_habit.get_periodicity() == periodicity:
                        result_list.append(current_habit)

                return tuple(result_list)
            else:
                # critical error, it is not possible to handle any habits if periodicity is unknown
                raise NameError(
                    'unknown periodicity, does not match any from const_handler: {}. please contact the admin.'
                    .format(periodicity))
        else:
            raise MissingUserIdException()

    def get_habits_by_streak(self, force_update=False):
        """
        return list of habits, sorted by streak (desc)

        :param force_update: boolean - reload habits from database (default false)

        :return: tuple of habits

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()

            sorted_habits = sorted(self.__habits__, key=lambda current_habit: current_habit.get_streak(), reverse=True)
            return tuple(sorted_habits)
        else:
            raise MissingUserIdException()

    def get_habits_by_longest_streak(self, force_update=False):
        """
        return list of habits, sorted by longest_streak (desc)

        :param force_update: boolean - reload habits from database (default false)

        :return: tuple of habits

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()

            sorted_habits = sorted(self.__habits__, key=lambda current_habit: current_habit.get_longest_streak(), reverse=True)
            return tuple(sorted_habits)
        else:
            raise MissingUserIdException()

    def get_habits_by_break(self, force_update=False):
        """
        return list of habits, sorted by the sum of all breaks (from break_history) (desc)

        :param force_update: boolean - reload habits from database (default false)

        :return: dictionary of habits and breaks with "habits" and "breaks"

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()

            reference_list = [] # list of the breaks, mirroring the result_list
            result_list = []

            # custom sorting for breaks
            for current_habit in self.__habits__:
                breaks_sum = 0

                for year in current_habit.get_break_history().keys():
                    for month in current_habit.get_break_history().get(year).keys():
                        breaks_sum += current_habit.get_break_history().get(year).get(month)

                # search for correct position
                target_index = 0
                for current_index, current_break in enumerate(reference_list):
                    if current_break <= breaks_sum:
                        target_index = current_index
                        break

                result_list.insert(target_index, current_habit)
                reference_list.insert(target_index, breaks_sum)

            logging.debug(reference_list)
            return {"habits": result_list, "breaks": reference_list}
        else:
            raise MissingUserIdException()

    def get_habits_by_last_month_breaks(self, force_update=False):
        """
        return list of habits, sorted by the breaks of last month (from break_history) (desc)

        :param force_update: boolean - reload habits from database (default false)

        :return: :return: dictionary of habits and breaks with "habits" and "breaks"

        :raise: MissingUserIdException when no user_id is given (call select_user())
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()

            reference_list = []  # list of the breaks, mirroring the result_list
            result_list = []

            last_month_date = time_handler.get_last_month(datetime.now())
            year = str(last_month_date.year)
            month = str(last_month_date.month)

            # custom sorting for breaks
            for current_habit in self.__habits__:
                target_index = -1
                current_habit_break = 0

                if current_habit.get_break_history().get(year) is not None:
                    if current_habit.get_break_history().get(year).get(month) is not None:
                        current_habit_break = current_habit.get_break_history().get(year).get(month)

                        if current_habit_break > 0:
                            current_habit.last_months_breaks = current_habit_break
                            for current_index, current_break in enumerate(reference_list):
                                if current_break <= current_habit_break:
                                    target_index = current_index
                                    break

                if target_index == -1:
                    reference_list.append(current_habit_break)
                    result_list.append(current_habit)
                else:
                    reference_list.insert(target_index, current_habit_break)
                    result_list.insert(target_index, current_habit)

            logging.debug(reference_list)
            return {"habits": result_list, "breaks": reference_list}
        else:
            raise MissingUserIdException()

    def get_habits_by_created(self, force_update=False):
        """
        return list of habits, sorted by the creation date (oldest first)

        :param force_update: boolean - reload habits from database (default false)

        :return: tuple of habits

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise: ValueError when the created-date of a habit could not be parsed
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()

            reference_list = []  # list of the datetime objects, mirroring the result_list
            result_list = []

            # custom sorting for created-at date
            for current_habit in self.__habits__:
                current_habit_created = time_handler.parse_string_to_datetime(current_habit.get_created())

                if current_habit_created is None or len(result_list) == 0:
                    result_list.append(current_habit)
                    reference_list.append(current_habit_created)
                else:
                    found = False
                    for current_index, current_break in enumerate(reference_list):
                        if current_break is None or current_habit_created <= current_break:
                            found = True
                            result_list.insert(current_index, current_habit)
                            reference_list.insert(current_index, current_habit_created)
                            break

                    if not found:
                        result_list.append(current_habit)
                        reference_list.append(current_habit_created)


            return tuple(result_list)
        else:
            raise MissingUserIdException()

    def get_unchecked_habits(self, force_update=False):
        """
        return filtered list of all unchecked habits

        :param force_update: boolean - reload habits from database (default false)

        :return: tuple of habits

        :raise: MissingUserIdException when no user_id is given (call select_user())
        :raise: NameError if periodicity of the habit does not match the values from const
        """
        if self.has_user_id():
            if force_update:
                self.__update_habits_list__()

            result_list = []

            for current_habit in self.__habits__:
                if not current_habit.is_checked():
                    result_list.append(current_habit)

            return tuple(result_list)
        else:
            raise MissingUserIdException()
