# Количество секунд в минуте
SECONDS_IN_MINUTES = 60
# Количество секунд в часе
SECONDS_IN_HOURS = 60 * SECONDS_IN_MINUTES
# Количество секунд в дне
SECONDS_IN_DAYS = 24 * SECONDS_IN_HOURS
# Количество секунд в неделе
SECONDS_IN_WEEKS = 7 * SECONDS_IN_DAYS
# Количество секунд в месяце (в 30 днях)
SECONDS_IN_MONTHS = 30 * SECONDS_IN_DAYS
# Количество секунд в году
SECONDS_IN_YEARS = 365 * SECONDS_IN_DAYS

# Методы в этом файле написаны для работы с единицами измерения времени (unit), заданными словами:
#  'seconds' - секунды;
#  'minutes' - минуты;
#  'hours' - часы;
#  'weeks' - недели;
#  'days' - дни;
#  'months' - месяцы;
#  'years' - годы;
#  'ten years' - десятилетия.


def unit_in_symbol(unit):
    """
    @Описание:
        Определяет символ для заданной единицы измерения.
    :param unit: единица измерения времени (String)
    :return:
    """
    if unit == 'seconds':
        symbol = 'sec'
    elif unit == 'minutes':
        symbol = 'min'
    elif unit == 'hours':
        symbol = 'h'
    elif unit == 'days':
        symbol = 'd'
    elif unit == 'weeks':
        symbol = 'w'
    elif unit == 'months':
        symbol = 'mon'
    elif unit == 'years':
        symbol = 'y'
    elif unit == 'ten years':
        symbol = '10y'
    else:
        symbol = 'error'

    return symbol


def seconds_to_unit(seconds, unit):
    """
    @Описание:
        Метод переводит секунды в заданную единицу измерения времени.
    :param seconds: количество секунд, которые переводятся в единицы измерения времени unit.
    :param unit: единица измерения времени, в которые переводятся секунды seconds (String).
    :return: количество единиц измерения времени unit, в которые переводятся секунды seconds.
    """
    if unit == 'seconds':
        seconds = seconds
    elif unit == 'minutes':
        seconds = seconds_to_minutes(seconds)
    elif unit == 'hours':
        seconds = seconds_to_hours(seconds)
    elif unit == 'days':
        seconds = seconds_to_days(seconds)
    elif unit == 'weeks':
        seconds = seconds_to_weeks(seconds)
    elif unit == 'months':
        seconds = seconds_to_months(seconds)
    elif unit == 'years':
        seconds = seconds_to_years(seconds)
    elif unit == 'ten years':
        seconds = seconds_to_ten_years(seconds)

    return seconds


def to_get_unit_in_seconds(unit):
    """
    @Описание:
        Метод возвращает количество секунд в одной заданной единице измерения времени.
    :param unit: единица измерения времени, для которой возвращается количество секунд (String).
    :return: количество секунд в одной единице измерения времени unit.
    """
    if unit == 'seconds':
        seconds_quantity = 1
    elif unit == 'minutes':
        seconds_quantity = SECONDS_IN_MINUTES
    elif unit == 'hours':
        seconds_quantity = SECONDS_IN_HOURS
    elif unit == 'days':
        seconds_quantity = SECONDS_IN_DAYS
    elif unit == 'weeks':
        seconds_quantity = SECONDS_IN_WEEKS
    elif unit == 'months':
        seconds_quantity = SECONDS_IN_MONTHS
    elif unit == 'years':
        seconds_quantity = SECONDS_IN_YEARS
    elif unit == 'ten years':
        seconds_quantity = 10 * SECONDS_IN_YEARS
    else:
        seconds_quantity = 1

    return seconds_quantity


def seconds_to_minutes(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в минуты.
    :param seconds: количество секунд, которое переводится в минуты.
    :return: заданное количество секунд seconds в минутах.
    """""
    return seconds / SECONDS_IN_MINUTES


def seconds_to_hours(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в часы.
    :param seconds: количество секунд, которое переводится в часы.
    :return: заданное количество секунд seconds в часах.
    """
    return seconds / SECONDS_IN_HOURS


def seconds_to_days(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в дни.
    :param seconds: количество секунд, которое переводится в дни.
    :return: заданное количество секунд seconds в днях.
    """
    return seconds / SECONDS_IN_DAYS


def seconds_to_weeks(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в недели.
    :param seconds: количество секунд, которое переводится в недели.
    :return: заданное количество секунд seconds в неделях.
    """
    return seconds / SECONDS_IN_WEEKS


def seconds_to_months(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в месяцы.
    :param seconds: количество секунд, которое переводится в месяцы.
    :return: заданное количество секунд seconds в месяцах.
    """
    return seconds / SECONDS_IN_MONTHS


def seconds_to_years(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в годы.
    :param seconds: количество секунд, которое переводится в годы.
    :return: заданное количество секунд seconds в годах.
    """
    return seconds / SECONDS_IN_YEARS


def seconds_to_ten_years(seconds):
    """
    @Описание:
        Метод переводит заданное количество секунд в десятилетия.
    :param seconds: количество секунд, которое переводится в десятилетия.
    :return: заданное количество секунд seconds в десятилетиях.
    """
    return seconds / (10 * SECONDS_IN_YEARS)
