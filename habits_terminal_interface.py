"""
terminal interface for habits.
creates a dialog and works as main
"""

import logging
import random
from helper import const_handler
from users import user_handler
from habits import habits_handler

const = const_handler.ConstHandler()
logging.basicConfig(level=const.get_logger_log_level(), format=const.get_logger_log_format(),
                    filename=const.get_logger_log_filename(), filemode=const.get_logger_log_filemode(), force=True)

user_handler_obj = user_handler.UserHandler()
habits_handler_obj = habits_handler.Habits()

user_id = None
user_name = ''


def __dialog_menu_main__():
    """
    dialog for a menu, directing to other dialogs
    """
    print('User: {}'.format(user_name))
    print('--main menu--')

    dialog_target = None

    while dialog_target is None:
        print('please select:')
        print('[1] for the users-menu')
        print('[2] for the habits-menu')
        print('[exit] to exit the program')

        primary_selection = input('please select:').strip().lower()
        match primary_selection:
            case 'exit':
                print()
                print('bye bye!')
                exit(0)
            case '1':
                print()
                print('please select what you would like to do:')
                print('[1] create a new user')
                print('[2] change the selected user')
                print('[3] change the name of a user')
                print('[4] delete a user')
                print('[back] to go back to the main menu')
                print('[exit] to exit the program')

                user_input = ''
                while user_input == '':
                    user_input = input('please select:').strip().lower()
                    match user_input:
                        case '1':
                            dialog_target = 'user_create'
                        case '2':
                            dialog_target = 'user_change'
                        case '3':
                            dialog_target = 'user_edit'
                        case '4':
                            dialog_target = 'user_delete'
                        case 'back':
                            dialog_target = None
                            print()
                        case 'exit':
                            print()
                            print('bye bye!')
                            exit(0)
                        case _:
                            print('invalid selection, please try again')
                            print()
                            user_input = ''
            case '2':
                if len(habits_handler_obj.get_habits()) == 0:
                    print()
                    print('you currently have no habits, please create a new habit')
                    print()
                    dialog_target = 'habit_create'
                else:
                    print()
                    print('please select what you would like to do:')
                    print('[1] create a new habit')
                    print('[2] edit your habits')
                    print('[3] delete a habit')
                    print('[4] mark your habit as done')
                    print('[5] display the details of your habits')
                    print('[6] display the unfinished habits')
                    print('[7] show all or filtered habits')
                    print('[back] to go back to the main menu')
                    print('[exit] to exit the program')

                    user_input = ''
                    while user_input == '':
                        user_input = input('please select:').strip().lower()
                        match user_input:
                            case '1':
                                dialog_target = 'habit_create'
                            case '2':
                                dialog_target = 'habit_edit'
                            case '3':
                                dialog_target = 'habit_delete'
                            case '4':
                                dialog_target = 'habit_check'
                            case '5':
                                dialog_target = 'habit_detail'
                            case '6':
                                dialog_target = 'habit_unfinished'
                            case '7':
                                dialog_target = 'habit_show'
                            case 'back':
                                dialog_target = None
                                print()
                            case 'exit':
                                print()
                                print('bye bye!')
                                exit(0)
                            case _:
                                print('invalid selection, please try again')
                                print()
                                user_input = ''
            case _:
                print('invalid selection, please try again')
                print()
                dialog_target = None

    print()
    match dialog_target:
        case 'user_create':
            __dialog_create_user__()
        case 'user_change':
            __dialog_change_user__()
        case 'user_edit':
            __dialog_edit_user__()
        case 'user_delete':
            __dialog_delete_user__()
        case 'habit_create':
            __dialog_add_habit__()
        case 'habit_edit':
            __dialog_edit_habit__()
        case 'habit_delete':
            __dialog_delete_habit__()
        case 'habit_check':
            __dialog_check_habit__()
        case 'habit_detail':
            __dialog_details_habit__()
        case 'habit_unfinished':
            __dialog_display_unfinished_habits__()
        case 'habit_show':
            __dialog_display_filtered_habits__()
        case _:
            print('something went wrong while selecting, please try again')
            print()
            __dialog_menu_main__()


def __dialog_create_user__():
    """
    dialog for creating a new user
    """
    global user_id, user_name

    print('create new user')
    print('insert user name:')

    new_user_name = ''
    while new_user_name == '':
        new_user_name = input('please enter a name:')

        if new_user_name == '':
            print('no empty names allowed, please try again')
            print()
        elif new_user_name.strip().lower() == 'exit' or new_user_name.strip().lower() == 'back':
            print('invalid user name, please dont use the keywords "back" or "exit"')
            print()
            new_user_name = ''

    new_user_id = user_handler_obj.create_user(new_user_name)  # creating a user returns the new id
    print()
    print('user has been created')
    print('continue with created user?')
    continue_diction = input('please select (yes/no):').strip().lower()
    print()

    if continue_diction == 'y' or continue_diction == 'yes':
        user_id = str(new_user_id)
        user_name = new_user_name
        habits_handler_obj.select_user(user_id)
        __dialog_menu_main__()
    else:
        if user_id is None:
            __dialog_select_user__()
        else:
            __dialog_menu_main__()


def __dialog_select_user__():
    """
    dialog for selecting a user, forces to select or create a user
    initial function, differs from __dialog_change_user__()
    """
    global user_id, user_name

    users = user_handler_obj.get_all_users()

    if len(users) == 0:
        print('No user has been created yet')
        __dialog_create_user__()
    else:
        print('--select user--')
        print('Please select:')
        print('[create] to create a new user')
        print('[exit] to exit the program')
        print('or select a users:')

        for index, user in enumerate(users):
            print('[{index}] to select the user: {user}'.format(index=index + 1,
                                                                user=user.get_name()))  # easier for users to start index with 1

        valid_selection = False
        to_creat_user = False

        while not valid_selection:
            selection = input('please select:').strip().lower()

            match selection:
                case 'create':
                    valid_selection = True
                    to_creat_user = True  # to create user
                case 'exit':
                    print('bye bye!')
                    exit(0)
                case _:
                    try:
                        selected_index = int(selection) - 1

                        if 0 <= selected_index < len(users):
                            selected_user = users[selected_index]
                            user_id = str(selected_user.get_user_id())
                            user_name = selected_user.get_name()
                            habits_handler_obj.select_user(user_id)
                            valid_selection = True  # to main
                        else:
                            print('invalid selection, please try again')
                            print()
                            valid_selection = False

                    except ValueError:
                        print('invalid selection, please try again')
                        print()
                        valid_selection = False

        print()
        if to_creat_user:
            __dialog_create_user__()
        else:
            __dialog_menu_main__()


def __dialog_change_user__():
    """
    dialog for changing the current user
    differs from __dialog_select_user__()
    """
    global user_id, user_name

    users = user_handler_obj.get_all_users()

    if len(users) == 1:
        print('only one user has been created yet')
        print('please create more users to be able to switch users')
        print()
        __dialog_menu_main__()
    else:
        print('--change user--')
        print('please select:')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('users:')

        for index, user in enumerate(users):
            print('[{index}] to select the user: {user}'.format(index=index + 1, user=user.get_name()))

        user_selection = None
        while user_selection is None:
            user_selection = input('please select:').strip().lower()
            match user_selection:
                case 'exit':
                    print()
                    print('bye bye!')
                    exit(0)
                case _:
                    if user_selection != 'back':
                        try:
                            selected_index = int(user_selection) - 1

                            if 0 <= selected_index < len(users):
                                selected_user = users[selected_index]
                                user_id = str(selected_user.get_user_id())
                                user_name = selected_user.get_name()
                                habits_handler_obj.select_user(user_id)
                            else:
                                print('invalid selection, please try again')
                                print()
                                user_selection = None
                        except ValueError:
                            print('invalid selection, please try again')
                            print()
                            user_selection = None

        print()
        __dialog_menu_main__()


def __dialog_edit_user__():
    """
    dialog for editing a user-name
    """
    global user_name, user_id

    users = user_handler_obj.get_all_users()

    if len(users) == 1:
        print('only one user has been created yet')
        print('please enter the new name of your user "{}"'.format(users[0].get_name()))

        new_name = ''
        while new_name == '':
            new_name = input('please enter a name:')

            if new_name == '':
                print('no empty names allowed, please try again')
                print()
            elif new_name.strip().lower() == 'exit' or new_name.strip().lower() == 'back':
                print('invalid user name, please dont use the keywords "back" or "exit"')
                print()
                new_name = ''

        user_handler_obj.rename_user(user_id, new_name)
        user_name = new_name
        print('name updated')
        print()
        __dialog_menu_main__()
    else:
        print('--edit user--')
        print('please select:')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('users:')

        for index, user in enumerate(users):
            print('[{index}] to select the user: {user}'.format(index=index + 1, user=user.get_name()))

        user_selection = None
        while user_selection is None:
            user_selection = input('please select:').strip().lower()

            match user_selection:
                case 'exit':
                    print()
                    print('bye bye!')
                    exit(0)
                case _:
                    if user_selection != 'back':
                        try:
                            selected_index = int(user_selection) - 1

                            if 0 <= selected_index < len(users):
                                selected_user = users[selected_index]
                                print('please enter the new name of the user "{}"'.format(selected_user.get_name()))

                                new_name = ''
                                while new_name == '':
                                    new_name = input('please enter a name:')
                                    if new_name == '':
                                        print('no empty names allowed, please try again')
                                        print()
                                    elif new_name.strip().lower() == 'exit' or new_name.strip().lower() == 'back':
                                        print('invalid user name, please dont use the keywords "back" or "exit"')
                                        print()
                                        new_name = ''

                                user_handler_obj.rename_user(selected_user.get_user_id(), new_name)
                                if str(selected_user.get_user_id()) == str(user_id):
                                    user_name = new_name
                            else:
                                print('invalid selection, please try again')
                                print()
                                user_selection = None
                        except ValueError:
                            print('invalid selection, please try again')
                            print()
                            user_selection = None

        print('name updated')
        print()
        __dialog_menu_main__()


def __dialog_delete_user__():
    """
    dialog for deleting a user
    """
    global user_name, user_id

    users = user_handler_obj.get_all_users()

    if len(users) == 1:
        print('only one user has been created yet')
        print('this user cannot be deleted unless there is another one')

        __dialog_menu_main__()
    else:
        print('--delete user--')
        print('please select:')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('users:')

        for index, user in enumerate(users):
            print('[{index}] to select the user: {user}'.format(index=index + 1, user=user.get_name()))

        user_selection = None
        force_user_select = False

        while user_selection is None:
            user_selection = input('please select:').strip().lower()

            match user_selection:
                case 'exit':
                    print()
                    print('bye bye!')
                    exit(0)
                case _:
                    if user_selection != 'back':
                        try:
                            selected_index = int(user_selection) - 1

                            if 0 <= selected_index < len(users):
                                selected_user = users[selected_index]
                                print('note: all habits of the user will be deleted as well')
                                print('are you sure you want to delete the user "{user}"?'.format(
                                    user=selected_user.get_name()))

                                decision = ''
                                while decision == '':
                                    decision = input('please select (yes/no):').strip().lower()
                                    if decision == 'y' or decision == 'yes':
                                        user_handler_obj.delete_user(selected_user.get_user_id())
                                        # would clutter the db if you don't delete habits without users
                                        habits_handler_obj.delete_all_habits_for_user(selected_user.get_user_id())

                                        print()
                                        print('user has been deleted')
                                        print('all habits of the user has been deleted')

                                        # force into 'select user' if user deleted the current active user
                                        if str(selected_user.get_user_id()) == str(user_id):
                                            print()
                                            print('you have deleted your own current user')
                                            user_id = None
                                            user_name = ''
                                            force_user_select = True

                            else:
                                print('invalid selection, please try again')
                                user_selection = None

                        except ValueError:
                            print('invalid selection, please try again')
                            user_selection = None

        print()
        if force_user_select:
            __dialog_select_user__()
        else:
            __dialog_menu_main__()


def __dialog_add_habit__():
    """
    dialog for adding a habit
    """
    print('please enter the name of the habit you want to add')

    user_input_title = ''
    while user_input_title == '':
        user_input_title = input('please enter a title:')
        if user_input_title == '':
            print('no empty titles allowed, please try again')
            print()
        if user_input_title.strip().lower() == 'exit' or user_input_title.strip().lower() == 'back':
            print('invalid habit title, please dont use the keywords "back" or "exit"')
            print()
            user_input_title = ''

    print()
    print('please select a periodicity for the habit')
    print('[1] daily')
    print('[2] weekly')

    user_input_periodicity = ''
    while not (user_input_periodicity == '1' or user_input_periodicity == '2'):
        user_input_periodicity = input('please select a periodicity: (1/2)')
        print()

    print()
    print('you can add an optional description to the habit')
    print('entering nothing will let the description empty')
    user_input_description = input('please enter a description:')
    print()

    if user_input_periodicity == '1':
        habits_handler_obj.add_habit(user_input_title, user_input_description, const.get_periodicity_daily())
    else:
        habits_handler_obj.add_habit(user_input_title, user_input_description, const.get_periodicity_weekly())

    print('habit has been created')
    print()
    __dialog_menu_main__()


def __dialog_edit_habit__():
    """
    dialog for editing a habits title and description
    """
    print('--edit habit--')
    habit_selection = habits_handler_obj.get_habits()

    if len(habit_selection) == 0:
        print('you dont have any habits that could be edited')
    else:
        print('please select:')
        print('note: that you can not change the periodicity of a habit')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('habits:')

        for index, habit in enumerate(habit_selection):
            print('[{index}] to select the habit with the title:'.format(index=index + 1))
            print('    "{}"'.format(habit.get_title()))

        selected_input = None
        while selected_input is None:
            selected_input = input('please select:').strip().lower()

            if selected_input == 'exit':
                print()
                print('bye bye!')
                exit(0)
            elif selected_input != 'back':
                try:
                    selected_index = int(selected_input) - 1

                    if 0 <= selected_index < len(habit_selection):
                        selected_habit = habit_selection[selected_index]
                        print('please enter the new title for the habit')
                        print('leaving the input empty will not change the title')

                        new_title = None
                        while new_title is None:
                            new_title = input('please enter a title:')
                            if new_title == '':
                                new_title = selected_habit.get_title()
                            elif new_title.strip().lower() == 'exit' or new_title.strip().lower() == 'back':
                                print('invalid user name, please dont use the keywords "back" or "exit"')
                                print()
                                new_title = None

                        print()
                        print('please enter the new description for the habit')
                        print('leaving the input empty will not change the description')
                        new_description = input('please enter a description:')
                        print()

                        if new_description == '':
                            new_description = selected_habit.get_description()

                        habits_handler_obj.edit_habit(selected_habit.get_id(), new_title, new_description)
                        print('habit has been updated')
                        print()
                    else:
                        print('invalid selection, please try again')
                        print()
                        selected_input = None

                except ValueError:
                    print('invalid selection, please try again')
                    print()
                    selected_input = None

    print()
    __dialog_menu_main__()


def __dialog_delete_habit__():
    """
    dialog for deleting a habit
    """
    print('--delete habit--')
    habit_selection = habits_handler_obj.get_habits()

    if len(habit_selection) == 0:
        print('you dont have any habits that could be deleted')
    else:
        print('please select:')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('habits:')

        for index, habit in enumerate(habit_selection):
            print('[{index}] to select the habit with the title:'.format(index=index + 1))
            print('    "{}"'.format(habit.get_title()))

        selected_input = None

        while selected_input is None:
            selected_input = input('please select:').strip().lower()

            if selected_input == 'exit':
                print()
                print('bye bye!')
                exit(0)
            elif selected_input != 'back':
                try:
                    selected_index = int(selected_input) - 1

                    if 0 <= selected_index < len(habit_selection):
                        selected_habit = habit_selection[selected_index]
                        print('are you sure you want to delete the habit with the title:')
                        print('    "{}"?'.format(selected_habit.get_title()))

                        decision = ''
                        while decision == '':
                            decision = input('please select (yes/no):').strip().lower()
                            if decision == 'y' or decision == 'yes':
                                habits_handler_obj.delete_habit(selected_habit.get_id())
                                print()
                                print('habit has been deleted')
                                # not really, it just sets the flag 'deactivated' to true

                    else:
                        print('invalid selection, please try again')
                        print()
                        selected_input = None

                except ValueError:
                    print('invalid selection, please try again')
                    print()
                    selected_input = None

    print()
    __dialog_menu_main__()


def __dialog_check_habit__():
    """
    dialog for checking a habit as finished
    """
    print('--check habit--')
    habit_selection = habits_handler_obj.get_unchecked_habits()

    if len(habit_selection) == 0:
        print('all your habits have been marked as done, congratulations!')
    else:
        print('please select:')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('habits:')

        for index, habit in enumerate(habit_selection):
            print('[{index}] to select the habit with the title:'.format(index=index + 1))
            print('    "{}"'.format(habit.get_title()))

        selected_input = None
        while selected_input is None:
            selected_input = input('please select:').strip().lower()

            if selected_input == 'exit':
                print()
                print('bye bye!')
                exit(0)
            elif selected_input != 'back':
                try:
                    selected_index = int(selected_input) - 1

                    if 0 <= selected_index < len(habit_selection):
                        selected_habit = habit_selection[selected_index]
                        habits_handler_obj.check_habit(selected_habit.get_id())
                        affirmations = ('Congratulations!', 'Way to go!', 'Nailed it!', '👏', '🏆', 'Fantastic!',
                                        'Stupendous!', 'Amazing!', 'Incredible!', 'Spectacular!', 'Keep going!',
                                        'Keep it up!')
                        print()
                        print('habit has be marked as finished')
                        print(random.choice(affirmations))
                    else:
                        print('invalid selection, please try again')
                        print()
                        selected_input = None

                except ValueError:
                    print('invalid selection, please try again')
                    print()
                    selected_input = None

    print()
    __dialog_menu_main__()


def __dialog_details_habit__():
    """
    dialog for getting a habits details
    selection of habits is filtered to unfinished habits
    """
    print('--habits details--')
    habit_selection = habits_handler_obj.get_habits()

    if len(habit_selection) == 0:
        print('you dont have any habits that could be shown')
    else:
        print('please select:')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')
        print('habits:')

        for index, habit in enumerate(habit_selection):
            print('[{index}] to select the habit with the title:'.format(index=index + 1))
            print('    "{}"'.format(habit.get_title()))
        selected_input = None

        while selected_input is None:
            selected_input = input('please select:').strip().lower()

            if selected_input == 'exit':
                print()
                print('bye bye!')
                exit(0)
            elif selected_input != 'back':
                try:
                    selected_index = int(selected_input) - 1

                    if 0 <= selected_index < len(habit_selection):
                        selected_habit = habit_selection[selected_index]
                        periodicity = 'daily' if selected_habit.get_periodicity() == const.get_periodicity_daily() else 'weekly'
                        print()
                        print('details:')
                        print('title: {}'.format(selected_habit.get_title()))
                        if selected_habit.get_description() != '':
                            print('description: {}'.format(selected_habit.get_description()))
                        print('id: {}'.format(selected_habit.get_id()))
                        print('created at: {}'.format(selected_habit.get_created()))
                        print('periodicity: {}'.format(periodicity))
                        print('current streak: {}'.format(selected_habit.get_streak()))
                        print('longest streak: {}'.format(selected_habit.get_longest_streak()))
                        if selected_habit.get_last_checked() != '':
                            print('last checked: {}'.format(selected_habit.get_last_checked()))
                        if selected_habit.get_last_break() != '':
                            print('last break: {}'.format(selected_habit.get_last_break()))
                        print('break history: {}'.format(selected_habit.get_break_history()))
                    else:
                        print('invalid selection, please try again')
                        print()
                        selected_input = None

                except ValueError:
                    print('invalid selection, please try again')
                    print()
                    selected_input = None

    print()
    __dialog_menu_main__()


def __dialog_display_unfinished_habits__():
    """
    dialog for displaying all unfinished habits
    """
    print('--show unfinished habit--')
    habit_selection = habits_handler_obj.get_unchecked_habits()

    if len(habit_selection) == 0:
        print('you dont have any unfinished habits, congratulations!')
    else:
        for habit in habit_selection:
            periodicity = 'daily' if habit.get_periodicity() == const.get_periodicity_daily() else 'weekly'
            print('title: {}'.format(habit.get_title()))
            if habit.get_description() != '':
                print('description: {}'.format(habit.get_description()))
            print('periodicity: {}'.format(periodicity))
            print()

    print()
    __dialog_menu_main__()


def __dialog_display_filtered_habits__():
    """
    dialog for displaying all habits that have been filtered or sorted
    """
    print('--show filtered habit--')

    # default display for all selections
    def print_habit(habit_to_print):
        print('title: {}'.format(habit_to_print.get_title()))

        if habit_to_print.get_description() != '':
            print('description: {}'.format(habit_to_print.get_description()))

        print('current streak: {}'.format(habit_to_print.get_streak()))
        print('longest streak: {}'.format(habit_to_print.get_longest_streak()))

    if len(habits_handler_obj.get_habits()) == 0:
        print('you dont have any habits that could be shown')
    else:
        print('please select:')
        print('[1] show all habits')
        print('[2] show all daily habits')
        print('[3] show all weekly habits')
        print('[4] show top 5 streaks')
        print('[5] show top 5 longest streaks')
        print('[6] show top 5 breaks of last month')
        print('[7] show top 5 breaks over all')
        print('[8] show top 5 oldest habits')
        print('[back] to go back to the main menu')
        print('[exit] to exit the program')

        user_input = ''
        while user_input == '':
            user_input = input('please select:').strip().lower()

            match user_input:
                case '1':
                    print('all habits:')
                    print()
                    found_habits = habits_handler_obj.get_habits()

                    for found_habit in found_habits:
                        print_habit(found_habit)
                        print()

                case '2':
                    print('daily habits:')
                    print()
                    found_habits = habits_handler_obj.get_habits_by_periodicity(const.get_periodicity_daily())

                    if len(found_habits) == 0:
                        print('you dont have any daily habits that could be shown')
                    else:
                        for found_habit in found_habits:
                            print_habit(found_habit)
                            print()
                case '3':
                    print('weekly habits:')
                    print()
                    found_habits = habits_handler_obj.get_habits_by_periodicity(const.get_periodicity_weekly())

                    if len(found_habits) == 0:
                        print('you dont have any weekly habits that could be shown')
                    else:
                        for found_habit in found_habits:
                            print_habit(found_habit)
                            print()
                case '4':
                    print('top 5 habits by streak:')
                    print()
                    found_habits = habits_handler_obj.get_habits_by_streak()
                    max_index = 5 if len(found_habits) > 5 else len(found_habits)

                    for i in range(max_index):
                        print_habit(found_habits[i])
                        print()
                case '5':
                    print('top 5 habits by longest streak:')
                    print()
                    found_habits = habits_handler_obj.get_habits_by_longest_streak()
                    max_index = 5 if len(found_habits) > 5 else len(found_habits)

                    for i in range(max_index):
                        print_habit(found_habits[i])
                        print()
                case '6':
                    print('top 5 habits breaks last month:')
                    print()
                    found_habits_results = habits_handler_obj.get_habits_by_last_month_breaks()
                    found_habits = found_habits_results.get('habits')
                    corresponding_breaks = found_habits_results.get('breaks')
                    max_index = 5 if len(found_habits) > 5 else len(found_habits)

                    for i in range(max_index):
                        print_habit(found_habits[i])
                        print('last month breaks: {}'.format(corresponding_breaks[i]))
                        print()
                case '7':
                    print('top 5 habits breaks:')
                    print()
                    found_habits_results = habits_handler_obj.get_habits_by_break()
                    found_habits = found_habits_results.get('habits')
                    corresponding_breaks = found_habits_results.get('breaks')
                    max_index = 5 if len(found_habits) > 5 else len(found_habits)

                    for i in range(max_index):
                        print_habit(found_habits[i])
                        print('breaks: {}'.format(corresponding_breaks[i]))
                        print()
                case '8':
                    print('top 5 oldest habits:')
                    print()
                    found_habits = habits_handler_obj.get_habits_by_created()
                    max_index = 5 if len(found_habits) > 5 else len(found_habits)

                    for i in range(max_index):
                        print_habit(found_habits[i])
                        print('created: {}'.format(found_habits[i].get_created()))
                        print()
                case 'exit':
                    print()
                    print('bye bye!')
                    exit(0)
                case 'back':
                    break
                case _:
                    print('invalid selection, please try again')
                    print()
                    user_input = ''

    print()
    __dialog_menu_main__()


print('~~Welcome to Habits~~')
__dialog_select_user__()
