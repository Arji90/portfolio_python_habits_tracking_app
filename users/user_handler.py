import sqlite3
import logging
from helper import const_handler
from users import user


class UserHandler:
    """
    Handler for test-users required for the project.

    provided functions:
    create_user()
    rename_user()
    delete_user()
    get_all_users()
    """

    const = const_handler.ConstHandler()
    logging.basicConfig(level=const.get_logger_log_level(), format=const.get_logger_log_format(),
                        filename=const.get_logger_log_filename(), filemode=const.get_logger_log_filemode(), force=True)

    def __sql_call__(self, query, params=(), fetch=False):
        """
        private function for sql-handling

        :param query: sql query as string
        :param params: tuple of parameters to pass to sql query
        :param fetch: boolean flag to fetch results from sql query

        :return: tuple of results from sql query
        """
        return_value = True

        connection = sqlite3.connect('./users/user.db')
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
        query = '''CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, deactivated BIT DEFAULT 0)'''

        self.__sql_call__(query)

    def create_user(self, name):
        """
        creates a new users

        :param name: string

        :return: created id for the users
        """
        query = 'INSERT INTO users (name, deactivated) VALUES (?, ?)'
        created_id = self.__sql_call__(query, (name, False))
        return created_id

    def rename_user(self, user_id, name):
        """
        renames the users of given user_id

        :param user_id:
        :param name:
        """
        query = 'UPDATE users SET name = ? WHERE id = ?'
        self.__sql_call__(query, (name, user_id))

    def delete_user(self, user_id):
        """
        sets the deactivated flag for given user_id to true

        :param user_id:
        """
        query = 'UPDATE users SET deactivated = 1 WHERE id = {user_id}'.format(user_id=user_id)
        self.__sql_call__(query)

    def get_all_users(self):
        """
        returns a list of all users with deactivated flag as false

        :return: list of user objects
        """
        query = 'SELECT * FROM users WHERE deactivated=0'
        sql_result = self.__sql_call__(query=query, fetch=True)
        users = []
        for sql_user in sql_result:
            users.append(user.User(user_id=sql_user[0], name=sql_user[1]))
        logging.debug(users)
        return users
