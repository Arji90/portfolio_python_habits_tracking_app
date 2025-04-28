"""
automated tests, use pytest on the project (see README.md)
"""
from helper import const_handler, time_handler
from habits import habits_handler, habit
from datetime import datetime, timedelta
import configparser
import pytest

__config__ = configparser.RawConfigParser()
__config__.read('habits.properties')

Const = const_handler.ConstHandler()

# read periodicities from habits.properties or set default values for const_handler test
__expected_daily_periodicity__ = __config__.get('Periodicity', 'daily') if __config__.has_option('Periodicity', 'daily') else 0
__expected_weekly_periodicity__ = __config__.get('Periodicity', 'weekly') if __config__.has_option('Periodicity', 'weekly') else 1

# originally only 14 days, but the feedback explicitly states 4 weeks for the tests as well
__expected_days_between__ = 28
__expected_weeks_between__ = int(__expected_days_between__ / 7)
__date_test_start__ = datetime.now() - timedelta(days=__expected_days_between__)
__date_test_end__ = datetime.now()
__expected_start_of_day__ = __date_test_end__.replace(hour=0, minute=0, second=0, microsecond=0)
__expected_start_of_week__ = __expected_start_of_day__ - timedelta(days=__expected_start_of_day__.weekday())

__date_last_month__ = time_handler.get_last_month(datetime.now())

#habits for update-calculations and check-handling
__habits_test_list__ = [habit.Habit(1, Const.get_user_test_id_a(), 'test 1', 'daily', Const.get_periodicity_daily(),
                                      str(__date_test_start__.replace(hour=8)), '', str(__date_test_start__), 0, 0, '{}'),
                        habit.Habit(2, Const.get_user_test_id_a(), 'test 2', 'weekly', Const.get_periodicity_weekly(),
                                      str(__date_test_start__.replace(hour=2)), '', '',
                                      0, 5, '{{"{year}":{{"{month}":2}}}}'.format(year=__date_last_month__.year, month=__date_last_month__.month))]

# habits that should not be updated from init for testing the sorting, rename and delete functions
__alternative_habits_test_list = [habit.Habit(3, Const.get_user_test_id_b(), 'test habit for sorting', 'should always be last',
                                      Const.get_periodicity_daily(), str((__date_test_end__ - timedelta(days=1)).replace(hour=6)), str(__date_test_end__ - timedelta(days=1)),
                                      str(__date_test_end__ - timedelta(days=1)),1, 1, '{}'),
                                  habit.Habit(4, Const.get_user_test_id_b(), 'test habit for sorting', 'should always be first',
                                      Const.get_periodicity_weekly(), str((__date_test_end__ - timedelta(days=1)).replace(hour=2)), str(__date_test_end__ - timedelta(days=1)),
                                      str(__date_test_end__ - timedelta(days=1)),7, 10,
                                      '{{"{year}":{{"{month}":2}}}}'.format(year=__date_last_month__.year, month=__date_last_month__.month))]

Habits = habits_handler.Habits()
Habits.select_user(Const.get_user_test_id_a(), __habits_test_list__)

# testing Habits instance for missing user-id behaviour
Habits_without_user = habits_handler.Habits()

def test_habits_user_id_requirement():
    """
    Tests if the functions protected by habits require user id throw exception correctly
    result of discovering that pytest.raises() exist
    """
    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.__update_habits_list__()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.__save_habit__('') # parameters should not be relevant here

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.__save_all_habits__()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.add_habit('', '', '') # parameters should not be relevant here

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.edit_habit('') # parameters should not be relevant here

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.delete_habit('') # parameters should not be relevant here

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.check_habit('') # parameters should not be relevant here

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits_by_periodicity('') # parameters should not be relevant here

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits_by_streak()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits_by_longest_streak()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits_by_break()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits_by_last_month_breaks()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_habits_by_created()

    with pytest.raises(habits_handler.MissingUserIdException):
        Habits_without_user.get_unchecked_habits()

def test_const_periodicity():
    """
    Test is reading from properties done correctly?
    If no properties exist, are the default values correct?
    """
    assert __expected_daily_periodicity__ == Const.get_periodicity_daily() # is daily periodicity created correctly?
    assert __expected_weekly_periodicity__ == Const.get_periodicity_weekly() # is weekly periodicity created correctly?

def test_date_calculations():
    """
    Test functions from time_handler.py
    """
    # is start of day created correctly?
    assert time_handler.get_start_of_day(datetime.now()) == __expected_start_of_day__
    # is start of week created correctly?
    assert time_handler.get_start_of_week(datetime.now()) == __expected_start_of_week__
    # are 2 dates compared correctly and is the time ignored? - expect true -
    assert time_handler.is_same_date(__expected_start_of_day__, __expected_start_of_day__ + timedelta(hours=12))
    # are 2 dates compared correctly? - expect false -
    assert not time_handler.is_same_date(__date_test_start__, __date_test_end__)
    # is date today and is the time ignored? - expect true -
    assert time_handler.is_today(__expected_start_of_day__ + timedelta(hours=12))
    # is date today? - expect false -
    assert not time_handler.is_today(__date_test_start__)
    # are days between counted correctly and does the order of the inserted dates matter?
    assert time_handler.count_days_between_dates(__date_test_start__, __date_test_end__) == __expected_days_between__
    # are days between counted correctly and does the order of the inserted dates matter?
    assert time_handler.count_days_between_dates(__date_test_end__, __date_test_start__) == __expected_days_between__
    # are the days until today counted correctly?
    assert time_handler.count_days_till_today(__date_test_start__) == __expected_days_between__
    # are weeks between counted correctly and does the order of the inserted dates matter?
    assert time_handler.count_weeks_between_dates(__date_test_start__, __date_test_end__) == __expected_weeks_between__
    # are weeks between counted correctly and does the order of the inserted dates matter?
    assert time_handler.count_weeks_between_dates(__date_test_end__, __date_test_start__) == __expected_weeks_between__
    # are the weeks until today counted correctly?
    assert time_handler.count_weeks_till_today(__date_test_start__) == __expected_weeks_between__
    # is get_last_month calculated correctly?
    assert time_handler.get_last_month(datetime(year=2025, month=2, day=1)).month == 1
    # is get_last_month calculated correctly and does it count the year change?
    assert time_handler.get_last_month(datetime(year=2025, month=1, day=1)).month == 12
    assert time_handler.get_last_month(datetime(year=2025, month=1, day=1)).year == 2024
    # are date-strings parsed correctly?
    parsed_date = time_handler.parse_string_to_datetime('2025-12-24 12:00:00.000000')
    assert parsed_date.year == 2025 and parsed_date.month == 12 and parsed_date.day == 24
    # is the ValueError Exception called correctly while parsing an invalid date-string (return None and log error)?
    assert time_handler.parse_string_to_datetime('24.12.2025 12:00:00.000000') is None

def test_habit_autoupdating():
    """
    Testing streak, last_break and break_history of __habits_test_list__
    :raise: Exception if testing-mode could not be enabled in Habits
    """
    if Habits.__is_test_user__():
        # should contain 2 habits
        assert len(Habits.get_habits()) == 2
        for current_habit in Habits.get_habits():
            # streaks should be 0
            assert current_habit.get_streak() == 0
            # last break should be yesterday
            assert time_handler.is_same_date(time_handler.parse_string_to_datetime(current_habit.get_last_break()), datetime.now() - timedelta(days=1))

            # calculates the sum of all breaks
            breaks_sum = 0
            for year in current_habit.get_break_history().keys():
                for month in current_habit.get_break_history().get(year).keys():
                    breaks_sum += current_habit.get_break_history().get(year).get(month)

            if current_habit.get_id() == 1:
                assert breaks_sum == __expected_days_between__ - 1 # -1 for no break for current day
            else:
                assert breaks_sum == __expected_weeks_between__ + 1 # -1 for no break for current week and +2 from history
    else:
        raise Exception('Habits is not in testing-mode, something went wrong')

def test_update_queries():
    """
    Testing queries and data attached to Habits
    :raise: Exception if testing-mode could not be enabled in Habits
    """
    if Habits.__is_test_user__():
        # should contain 2 habits
        assert len(Habits.get_habits()) == 2
        for current_habit in Habits.get_habits():
            query = current_habit.create_update_query(Const.get_user_test_id_a())
            query_string = query.get('query')
            query_values = query.get('values')

            # check if dict has string and values
            assert query_string is not None
            assert query_values is not None

            # check if keywords exist in string
            assert 'UPDATE' in query_string
            assert 'title' in query_string
            assert 'description' in query_string
            assert 'last_break' in query_string
            assert 'last_checked' in query_string
            assert 'streak' in query_string
            assert 'longest_streak' in query_string
            assert 'break_history' in query_string
            assert 'WHERE' in query_string
            assert 'id' in query_string
            assert 'user_id' in query_string

            # check if the values are correct and in expected order
            # title
            assert True if len(query_values) > 0 and query_values[0] == current_habit.get_title() else False
            # description
            assert True if len(query_values) > 1 and query_values[1] == current_habit.get_description() else False
            # last_break
            assert True if len(query_values) > 2 and str(query_values[2]) == str(current_habit.get_last_break()) else False
            # last_checked
            assert True if len(query_values) > 3 and str(query_values[3]) == str(current_habit.get_last_checked()) else False
            # streak
            assert True if len(query_values) > 4 and query_values[4] == current_habit.get_streak() else False
            # longest_streak
            assert True if len(query_values) > 5 and query_values[5] == current_habit.get_longest_streak() else False
            # break_history
            # just check if the break_history is not empty
            assert True if len(query_values) > 6 and query_values[6] != '{}' else False
            # id
            assert True if len(query_values) > 7 and query_values[7] == current_habit.get_id() else False
            # user_id
            assert True if len(query_values) > 8 and query_values[8] == Const.get_user_test_id_a() else False
    else:
        raise Exception('Habits is not in testing-mode, something went wrong')

def test_habits_unfinished_response():
    """
    check for number of unchecked habits
    """
    unchecked_habits = Habits.get_unchecked_habits()
    assert len(unchecked_habits) == 2

def test_habits_check_response():
    """
    check all habits and check their last_checked, streak and longest_streak
    :raise: Exception if testing-mode could not be enabled in Habits
    """
    if Habits.__is_test_user__():
        # should contain 2 habits
        assert len(Habits.get_habits()) == 2
        for current_habit in Habits.get_habits():
            Habits.check_habit(current_habit.get_id())
            assert time_handler.is_same_date(time_handler.parse_string_to_datetime(current_habit.get_last_checked()), __expected_start_of_day__)
            assert current_habit.get_streak() == 1
            if current_habit.get_id() == 1:
                assert current_habit.get_longest_streak() == 1 # 0 -> 1 for the first habit
            else:
                assert current_habit.get_longest_streak() == 5 # 5 -> 5 for the 2nd habit
    else:
        raise Exception('Habits is not in testing-mode, something went wrong')

def test_habits_unfinished_response_after_check():
    """
    check for number of unchecked habits after checking all habits
    """
    unchecked_habits = Habits.get_unchecked_habits()
    assert len(unchecked_habits) == 0

def test_habits_switch_user_handling():
    """
    check for setting the habits correctly on user-change
    sets up habits for the sorting test
    """
    Habits.select_user(Const.get_user_test_id_b(), __alternative_habits_test_list)
    new_habits = Habits.get_habits()

    for current_habit in new_habits:
        assert current_habit.get_id() == 3 or current_habit.get_id() == 4

def test_habits_sorting_response():
    """
    checks the sorting functions
    """
    daily_habits = Habits.get_habits_by_periodicity(Const.get_periodicity_daily())
    weekly_habits = Habits.get_habits_by_periodicity(Const.get_periodicity_weekly())
    habits_by_streak = Habits.get_habits_by_streak()
    habits_by_longest_streak = Habits.get_habits_by_streak()
    habits_by_break = Habits.get_habits_by_break()
    habits_by_breaks_last_month = Habits.get_habits_by_last_month_breaks()
    habits_by_created = Habits.get_habits_by_created()

    # in python, if "A and B" while A is false, B will not be executed and skipped
    assert len(daily_habits) == 1 and daily_habits[0].get_id() == 3
    assert len(weekly_habits) == 1 and weekly_habits[0].get_id() == 4
    assert len(habits_by_streak) == 2 and habits_by_streak[0].get_id() == 4
    assert len(habits_by_longest_streak) == 2 and habits_by_longest_streak[0].get_id() == 4
    assert len(habits_by_break.keys()) == 2 and len(habits_by_break.get('habits')) == 2 and len(habits_by_break.get('breaks')) == 2 and habits_by_break.get('habits')[0].get_id() == 4
    assert len(habits_by_breaks_last_month.keys()) == 2 and len(habits_by_breaks_last_month.get('habits')) == 2 and len(habits_by_breaks_last_month.get('breaks')) == 2 and habits_by_breaks_last_month.get('habits')[0].get_id() == 4
    assert len(habits_by_created) == 2 and habits_by_created[0].get_id() == 4

def test_habits_create():
    """
    tests create-habit behaviour (see tutor feedback)
    """
    # error because periodicity is invalid
    with pytest.raises(NameError):
        Habits.add_habit('', '', '')

    if Habits.__is_test_user__():
        sql_results = Habits.add_habit('title', 'description', Const.get_periodicity_weekly())
        assert len(sql_results) == 2

        query_string = sql_results[0]
        query_values = sql_results[1]

        assert 'INSERT' in query_string
        assert 'user_id' in query_string
        assert 'title' in query_string
        assert 'description' in query_string
        assert 'periodicity' in query_string
        assert 'created_at' in query_string
        assert 'last_break' in query_string
        assert 'last_checked' in query_string
        assert 'streak' in query_string
        assert 'longest_streak' in query_string
        assert 'break_history' in query_string

        assert len(query_values) == 10
        assert query_values[0] == Const.get_user_test_id_b()
        assert query_values[1] == 'title'
        assert query_values[2] == 'description'
        assert query_values[3] == Const.get_periodicity_weekly()
        assert time_handler.is_today(query_values[4])
        assert query_values[5] == ''
        assert query_values[6] == ''
        assert query_values[7] == 0
        assert query_values[8] == 0
        assert query_values[9] == '{}'
    else:
        raise Exception('Habits is not in testing-mode, something went wrong')

def test_habits_edit():
    """
    tests edit-habit behaviour (see tutor feedback)
    """
    # error because no valid habit_id was given
    with pytest.raises(habits_handler.HabitDoesNotExistException):
        Habits.edit_habit(-1)

    if Habits.__is_test_user__():
        new_title = 'title replacement'
        new_description = 'description replacement'
        new_title_2 = 'title replacement 2'
        new_description_2 = 'description replacement 2'

        updated_habit = Habits.edit_habit(3)
        assert updated_habit.get_id() == 3
        assert updated_habit.get_title() == 'test habit for sorting'
        assert updated_habit.get_description() == 'should always be last'

        updated_habit = Habits.edit_habit(3, title=new_title)
        assert updated_habit.get_id() == 3
        assert updated_habit.get_title() == new_title
        assert updated_habit.get_description() == 'should always be last'

        updated_habit = Habits.edit_habit(3, description=new_description)
        assert updated_habit.get_id() == 3
        assert updated_habit.get_title() == new_title
        assert updated_habit.get_description() == new_description

        updated_habit = Habits.edit_habit(3, new_title_2, new_description_2)
        assert updated_habit.get_id() == 3
        assert updated_habit.get_title() == new_title_2
        assert updated_habit.get_description() == new_description_2
    else:
        raise Exception('Habits is not in testing-mode, something went wrong')

def test_habits_delete():
    """
    tests delete-habit behaviour (see tutor feedback)
    """
    # error because no valid habit_id was given
    with pytest.raises(habits_handler.HabitDoesNotExistException):
        Habits.delete_habit(-1)

    if Habits.__is_test_user__():
        # test delete 1 habit
        sql_results = Habits.delete_habit(3)
        assert len(sql_results) == 2

        query_string = sql_results[0]
        query_values = sql_results[1]

        assert 'UPDATE' in query_string
        assert 'deactivated' in query_string
        assert 'id' in query_string
        assert 'user_id' in query_string

        assert len(query_values) == 3
        assert query_values[0] == 1
        assert query_values[1] == 3
        assert query_values[2] == Const.get_user_test_id_b()

        # test delete all habits of a user
        sql_delete_all = Habits.delete_all_habits_for_user(Const.get_user_test_id_b())

        assert len(sql_delete_all) == 2

        query_string_delete_all = sql_delete_all[0]
        query_values_delete_all = sql_delete_all[1]

        assert 'UPDATE' in query_string_delete_all
        assert 'deactivated' in query_string_delete_all
        assert 'user_id' in query_string_delete_all

        assert len(query_values_delete_all) == 2
        assert query_values_delete_all[0] == 1
        assert query_values_delete_all[1] == Const.get_user_test_id_b()


    else:
        raise Exception('Habits is not in testing-mode, something went wrong')