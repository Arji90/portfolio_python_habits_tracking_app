# Habits App
## Setup
### Python
this app is made in using Python 3.13.1.

if issues occur while you are using a different version, please try the version mentioned.

for more information and an installation guide, please visit: [python](https://www.python.org/).

### Properties
to overwrite the given properties, create a 'habits.properties' file
in the root of the project.

the default properties are defines as follows:
```
[Periodicity]=
daily=0
weekly=1
[DBSection]=
name=habits
[Const]=
displayLog=False
[Logging]=
level=WARNING
format=%(levelname)s: %(asctime)s: %(message)s
filename=None
filemode=None
[TestUsers]=
userA=test_user_id_1
userB=test_user_id_2
```
important: changing the periodicity values while a habits-database with content already exist
will cause the program to stop working!

### Setup databases with example data (relevant for the tutor)
to set up the databases with the required example-data, please execute **habits_test_db_entries.py**

the script will display a warning that it will delete the 2 databases (if they exist) and replace them with the example-content.

note: please execute this AFTER editing the habits.properties file to prevent errors

```bash
python ./habits_test_db_entries.py
```

### Automated testing
the written tests in the test_handler are based on pytest 8.3.5

the tests use their own habits created from the current date to test the calculations accurately.

if issues occur while you are using a different version, please try the version mentioned.

for more information and an installation guide, please visit: [pytest](https://docs.pytest.org/).

## Start-up
### Starting the terminal
to start the terminal simply execute **habits_terminal_interface.py**
```bash
python ./habits_terminal_interface.py
```
interactions are solly done by the terminal, all options the user has are displayed before the input is expected.

### Starting automated tests
To start the automated tests, just call pytest in the root of the project
```bash
pytest
```
or alternatively this
```bash
python -m pytest
```
if pytest does not have an alias yet.

### Using habits_handler separately
import the habits_handler and initialize it with the class Habits().

before handling any habits, a user-id has to be given by calling select_user().

## Features
### habits_terminal_interface.py (ui)
- add, rename, delete, and change users
- add, rename, check and delete habits
- display all habits of the current user
- display all unfinished habits of a user
- display all daily or weekly habits of a user
- display the top 5 of a user by:
  - streak
  - longest streak
  - breaks of last month
  - breaks over all
  - creation date

(note: top 5 is arbitrary, can be replaced by any number, the code returns all habits sorted)

### habits_handler.py
- adjust const-values by habits.properties file
  - reference values for daily and weekly periodicities (will be written in the DB)
  - path and name of the habits-db
  - logging level, format and file-export
  - test-user IDs (2)
- multi-user handling by a user-id-string (see select_user())
- test-user detection to prevent database-interactions and sql-string/value testing
- providing periodicities for development, so reading from const_handler is not necessary
- add, rename delete and check habits
- delete all habits by user-id (no protection implemented, use with caution)
- select_user() allows a list of habits as a parameter, if the user-id is a test-user, this will enable test-mode
- get-functions for:
  - get all
  - get all by daily or weekly (filtered)
  - get all by streak (sorted)
  - get all by longest streak (sorted)
  - get all by breaks (sorted)
  - get all by last month breaks (sorted)
  - get all by created date (sorted)
  - get all unchecked (filtered)
- all get-functions take an optional boolean to force-reload all habits from the DB

## potential use-cases
- a (more or less) simple habits organizer to be used in the terminal or as a backend
- base for potential future projects like:
  - usage on private servers for personal use, for example implemented into smart-home-systems
  - implementation into an API for app-usage
- printing the code out for an interesting wallpaper