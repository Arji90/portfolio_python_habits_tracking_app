"""
test script to set up databases for presentation
"""

import sqlite3
import os
import json
from tabulate import tabulate
from datetime import datetime, timedelta
from helper import const_handler

Const = const_handler.ConstHandler()

def main():
    print('this is a script to replace all dbs (./users/user.db and {}.db)'.format(Const.get_habits_db_name()))
    print('it will delete and create new databases!')
    print('are you sure? please type "yes" to continue')
    decision = input('remove all entries?')
    if decision.lower().strip() == 'yes':
        print('replacing all databases...')
        file_path_users_db = './users/user.db'
        file_path_habits_db = Const.get_habits_db_name() + '.db'

        sql_create_user_db = '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, deactivated BIT DEFAULT 0)'''
        sql_create_habit_db = '''CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, 
                    title TEXT NOT NULL, description TEXT, 
                    periodicity TEXT NOT NULL, created_at TEXT NOT NULL,
                    deactivated BIT DEFAULT 0, last_break TEXT, last_checked TEXT,
                    streak INTEGER DEFAULT 0, longest_streak INTEGER DEFAULT 0, break_history TEXT)'''

        sql_add_test_users_query = '''INSERT INTO users (name, deactivated) VALUES (?, ?)'''
        sql_add_test_users_values = (('main test user', 0), ('alternative test user', 0))

        sql_add_test_habits_query = '''INSERT INTO habits (user_id, title, description, periodicity, created_at, last_break, 
                    last_checked, streak, longest_streak, break_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        __date_today__ = datetime.today()
        __date_8weeks_ago__ = __date_today__ - timedelta(days=56)
        __date_7weeks_ago__ = __date_today__ - timedelta(days=49)
        __date_6weeks_ago__ = __date_today__ - timedelta(days=42)
        __date_4weeks_ago__ = __date_today__ - timedelta(days=28)
        __date_2weeks_ago__ = __date_today__ - timedelta(days=14)
        __date_1week_ago__ = __date_today__ - timedelta(days=7)
        __date_yesterday__ = __date_today__ - timedelta(days=1)

        __pet_walk_history__ = {}
        for i in range(8): # break for __date_8weeks_ago__ to __date_7weeks_ago__ (both including) for last month breaks
            current_date = __date_8weeks_ago__ + timedelta(days=i)
            # if the test-data is created shortly after new year, date handling is always a pain
            year = current_date.year
            month = current_date.month

            if __pet_walk_history__.get(year) is None:
                __pet_walk_history__[year] = {}
            if __pet_walk_history__.get(year).get(month) is None:
                __pet_walk_history__[year][month] = 0
            __pet_walk_history__[year][month] += 1

        habit_1 = (1, 'Quit smoking', '', Const.get_periodicity_daily(),
                   str(__date_4weeks_ago__), '', str(__date_2weeks_ago__), 13, 13, '{}')
        habit_2 = (1, 'Go for a walk', "It doesn't matter how long", Const.get_periodicity_daily(),
                   str(__date_6weeks_ago__), '', str(__date_yesterday__), 41, 41, '{}')
        habit_3 = (1, 'Vacuum', 'Vacuum all rooms', Const.get_periodicity_weekly(),
                   str(__date_7weeks_ago__), '', str(__date_1week_ago__), 6, 6, '{}')
        habit_4 = (1, 'Taking your pet for a walk', "but it's a goldfish...", Const.get_periodicity_daily(),
                   str(__date_8weeks_ago__), str(__date_7weeks_ago__), '', 0, 0, json.dumps(__pet_walk_history__))
        habit_5 = (2, 'Go for a walk', 'Or not, who cares', Const.get_periodicity_daily(),
                   str(__date_8weeks_ago__), '', '', 0, 0, '{}')

        sql_add_test_habits_values = (habit_1, habit_2, habit_3, habit_4, habit_5)

        # update users
        if os.path.exists(file_path_users_db):
            os.remove(file_path_users_db)
            print('deleted {}'.format(file_path_users_db))
        connection = sqlite3.connect(file_path_users_db)
        cursor = connection.cursor()
        cursor.execute(sql_create_user_db)
        connection.commit()
        cursor.executemany(sql_add_test_users_query, sql_add_test_users_values)
        connection.commit()
        created_users = cursor.execute("select * from users").fetchall()
        print()
        # added for transparency reason
        print('created users for testing:')
        print(tabulate(created_users, headers=['id', 'name', 'deactivated']))
        print()
        connection.close()

        # update habits
        if os.path.exists(file_path_habits_db):
            os.remove(file_path_habits_db)
            print('deleted {}'.format(file_path_habits_db))
        connection = sqlite3.connect(file_path_habits_db)
        cursor = connection.cursor()
        cursor.execute(sql_create_habit_db)
        connection.commit()
        cursor.executemany(sql_add_test_habits_query, sql_add_test_habits_values)
        connection.commit()
        created_habits = cursor.execute("select * from habits").fetchall()
        print()
        # added for transparency reason
        print('created habits for testing:')
        print(tabulate(created_habits, headers=['id', 'user-id', 'title', 'description', 'periodicity',
                                                'created date', 'deactivated', 'last break', 'last checked',
                                                'steak', 'longest streak', 'break history']))
        connection.close()

main()