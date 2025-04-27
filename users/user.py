class User:
    """
    User class, containing the user-name and its id

    provided functions:
    get_user_id()
    get_name()
    """
    __name__ = ''
    __user_id__ = ''

    def __init__(self, user_id, name):
        self.__user_id__ = user_id
        self.__name__ = name

    def get_user_id(self):
        """
        :return: user-id
        """
        return self.__user_id__

    def get_name(self):
        """
        :return: user-name
        """
        return self.__name__