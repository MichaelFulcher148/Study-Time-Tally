# import pytest
from datetime import datetime
from study_time_tally import menu_char_check, validate_date, overlap_check, check_digit, validate_selector

def test_menu_char_check(capsys):
    assert menu_char_check('L', 'TIXDAREHS') is False
    captured = capsys.readouterr()
    assert captured.out == 'L is not a valid input\n'
    assert menu_char_check('[', 'TIXDAREHS') is False
    captured = capsys.readouterr()
    assert captured.out == '[ is not a valid input\n'
    assert menu_char_check('T', 'TIXDAREHS') is True
    assert menu_char_check('', 'TIXDAREHS') is False
    captured = capsys.readouterr()
    assert captured.out == 'Enter is not a valid input\n'

def test_validate_date(capsys):
    assert validate_date('01/04/2023') is True
    assert validate_date('00/03/2022') is False
    captured = capsys.readouterr()
    assert captured.out == '00/03/2022 is not a valid input\n'
    assert validate_date('32/01/1993') is False
    captured = capsys.readouterr()
    assert captured.out == '32/01/1993 is not a valid input\n'


# get_date()
# def test_validate_start_date(end_date: str, old: str):

# validate_end_date(start_date: str, old: str = None)

def test_overlap_check():
    assert overlap_check(datetime.strptime("1/8/1998", '%d/%m/%Y').date(), datetime.strptime("14/9/2001", '%d/%m/%Y').date(),
                         datetime.strptime("15/9/2001", '%d/%m/%Y').date(), datetime.strptime("16/9/2001", '%d/%m/%Y').date()) is False
    assert overlap_check(datetime.strptime("1/8/1998", '%d/%m/%Y').date(), datetime.strptime("14/9/2001", '%d/%m/%Y').date(),
                         datetime.strptime("1/9/2001", '%d/%m/%Y').date(), datetime.strptime("16/9/2001", '%d/%m/%Y').date()) is True


# tally_hours(start_date: str, end_date: str, day_dict: dict, cur=None)
# tabs_list(a_list: list)
# display_holiday_list_db(add_numbers: bool, names_list: dict, id_range: dict, for_removal: list, changed_names: dict, changed_start: dict, changed_end: dict) -> int:
# display_holiday_list(add_numbers: bool = False) -> int:
# hours_display(item1: str, item2: str) -> str:
# display_menu_stats(name: str, startDate, endData, days: dict, normal_hours_done: int, normal_minutes_done: int, extra_hours_done: int, extra_minutes_done: int, num_tabs: int, add_space: bool, curs=None) -> None:
# get_enabled_subjects(db_loc: str) -> list:
# main_menu() -> chr:
# check_fix_daily_progress():
# print_selected_days(day_list: list) -> None:
# setup_day_options(start_date, end_date, need_length: bool = True):

def test_check_digit(capsys):
    assert check_digit("3", True) == (True, 3)
    assert check_digit("h", True) == (False, 0)
    captured = capsys.readouterr()
    assert captured.out == "Input must be a decimal number.\n"
    assert check_digit("h", False) == (False, 0)
    captured = capsys.readouterr()
    assert captured.out == "Input must be a decimal number.\n"
    assert check_digit("", False) == (False, 0)
    captured = capsys.readouterr()
    assert captured.out == "<Enter> is not valid input.\n"
    assert check_digit("", True) == (True, 0)
    assert check_digit("4.5", False) == (False, 0)
    captured = capsys.readouterr()
    assert captured.out == "Input must be a decimal number.\n"

# get_time_digit(time_div_str: str)
# get_hour(day_num: int)
# create_days_dict(s_day_options: str, length: int, return_day_list: bool = False, days=None):
# get_name(type_text: str, name_list: list)
# add_menu_common()
# add_menu_db()
# add_menu()
# display_subject_list()

def test_validate_selector(capsys):
    assert validate_selector("1", 10, 2) is False
    captured = capsys.readouterr()
    assert captured.out == "1 is not a valid option.\n"
    assert validate_selector("1", 10, 1) is True
    assert validate_selector("0", 10) is True
    assert validate_selector("5", 10, 1) is True
    assert validate_selector("6", 10) is True
    assert validate_selector("10", 10, 2) is False
    captured = capsys.readouterr()
    assert captured.out == "10 is not a valid option.\n"
    assert validate_selector("10", 10) is False
    captured = capsys.readouterr()
    assert captured.out == "10 is not a valid option.\n"
    assert validate_selector("11", 10) is False
    captured = capsys.readouterr()
    assert captured.out == "11 is not a valid option.\n"
    assert validate_selector("11", 10, 2) is False
    captured = capsys.readouterr()
    assert captured.out == "11 is not a valid option.\n"
