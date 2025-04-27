"""
provides the ConstHandler object
"""
import logging
import configparser


class ConstHandler:
    """
    Provides constants to the project which can be overwritten in the habits.properties file (see README.md).

    logging is disabled here by default, enable in properties file (see README.md)

    given functions:
    get_periodicity_daily()
    get_periodicity_weekly()
    get_habits_db_name()
    get_logger_log_level()
    get_logger_log_format()
    get_logger_log_filename()
    get_logger_log_filemode()
    get_user_test_id_a()
    get_user_test_id_b()
    """
    __config__ = configparser.RawConfigParser()
    __config__.read('habits.properties')

    # act as well as the storage for the variable as well as its default value
    __periodicity_daily__ = 0
    __periodicity_weekly__ = 1
    __habits_db_name__ = 'habits'
    __logger_log_level__ = logging.WARNING
    __logger_log_format__ = '%(levelname)s: %(asctime)s: %(message)s'
    __logger_log_filename__ = None
    __logger_log_filemode__ = None

    # users-ids for automated tests
    __user_test_id_a__ = 'test_user_a'
    __user_test_id_b__ = 'test_user_b'

    def __get_config_data__(self, section, option, default_value):
        """
        private function to read config file if possible to return its value or the given default value.

        :param section: section name in config file
        :param option: option name in config file
        :param default_value: default value if config is not set

        :return: data from config file or the given default value
        """
        if self.__config__.has_section(section):
            try:
                config_data = self.__config__.get(section, option)

                if isinstance(config_data, str):
                    config_data = config_data.strip()

                # if the data from the config file does not correspond to a log-level, it uses the default value
                if section == 'Logging' and option == 'level':
                    logging_log_level = logging.getLevelNamesMapping().get(config_data)
                    if logging_log_level is None:
                        return default_value
                    else:
                        return logging_log_level
                return config_data
            except configparser.NoOptionError:
                logging.info(
                    'could not find "{option}" in section "{section}", default value "{default_value}" will be used.'.format(
                        option=option, section=section, default_value=default_value))
        else:
            logging.info(
                'habits.properties or section "{section}" could not be found, default value "{default_value}" for option "{option}" will be used'.format(
                    section=section, default_value=default_value, option=option))
        return default_value

    def __get_logging_file_config_data__(self):
        """
        private function to set __logger_log_filename__ and __logger_log_filemode__ because they validate each other
        from habits.properties file.
        """
        if self.__config__.has_section('Logging'):
            try:
                config_data_filename = self.__config__.get('Logging', 'filename')
                config_data_filemode = self.__config__.get('Logging', 'filemode')

                if isinstance(config_data_filename, str):
                    config_data_filename = config_data_filename.strip()

                if isinstance(config_data_filemode, str):
                    config_data_filemode = config_data_filemode.strip()

                if (config_data_filename is not None
                        and config_data_filename.lower() != 'none'
                        and config_data_filemode is not None
                        and (config_data_filemode.lower() == 'a' or config_data_filemode.lower() == 'w')):
                    self.__logger_log_filename__ = config_data_filename
                    self.__logger_log_filemode__ = config_data_filemode
            except configparser.NoOptionError:
                logging.info(
                    'could not find "filename" or "filemode" in section "Logging", file-export for logs is disabled by default.')
        else:
            logging.info(
                'habits.properties or section "Logging" could not be found, file-export for logs is disabled by default.')

    def __init__(self):
        """
        init function, sets log-level of const_handler from habits.properties file, default is Warning
        sets all values from habits.properties file or uses its default values
        """
        if self.__config__.has_section('Const'):
            const_log_display = self.__config__.get('Const', 'displayLog')
            if const_log_display is not None and (
                    'true' in const_log_display.lower() or 'yes' in const_log_display.lower()):
                logging.basicConfig(level=logging.INFO, force=True)

        self.__periodicity_daily__ = self.__get_config_data__('Periodicity', 'daily', self.__periodicity_daily__)
        self.__periodicity_weekly__ = self.__get_config_data__('Periodicity', 'weekly', self.__periodicity_weekly__)
        self.__habits_db_name__ = self.__get_config_data__('DBSection', 'name', self.__habits_db_name__)
        self.__logger_log_level__ = self.__get_config_data__('Logging', 'level', self.__logger_log_level__)
        self.__logger_log_format__ = self.__get_config_data__('Logging', 'format', self.__logger_log_format__)
        self.__get_logging_file_config_data__()
        self.__user_test_id_a__ = self.__get_config_data__('TestUsers', 'userA', self.__user_test_id_a__)
        self.__user_test_id_b__ = self.__get_config_data__('TestUsers', 'userB', self.__user_test_id_b__)

    def get_periodicity_daily(self):
        """
        :return: Periodicity -> daily from habits.properties or 0
        """
        return self.__periodicity_daily__

    def get_periodicity_weekly(self):
        """
        :return: Periodicity -> weekly from habits.properties or 1
        """
        return self.__periodicity_weekly__

    def get_habits_db_name(self):
        """
        :return: DBSection -> name from habits.properties or 'habits'
        """
        return self.__habits_db_name__

    def get_logger_log_level(self):
        """
        :return: Logging -> level from habits.properties or logging.WARNING
        """
        return self.__logger_log_level__

    def get_logger_log_format(self):
        """
        :return: Logging -> format from habits.properties or '%(levelname)s: %(asctime)s: %(message)s'
        """
        return self.__logger_log_format__

    def get_logger_log_filename(self):
        """
        :return: Logging -> filename from habits.properties or None
        """
        return self.__logger_log_filename__

    def get_logger_log_filemode(self):
        """
        :return: Logging -> filemode from habits.properties or None
        """
        return self.__logger_log_filemode__

    def get_user_test_id_a(self):
        """
        :return: TestUsers -> userA from habits.properties or 'test_user_a'
        """
        return self.__user_test_id_a__

    def get_user_test_id_b(self):
        """
        :return: TestUsers -> userB from habits.properties or 'test_user_b'
        """
        return self.__user_test_id_b__
