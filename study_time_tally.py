import json
import sys
import time
from datetime import timedelta, datetime
from math import ceil
from os import path, rename as file_rename, remove as file_del

from tools import log_tools

"""Study Time Tally
    By Michael Fulcher

    Send Donations (recommended $1.50USD) to -
    PayPal: mjfulcher58@gmail.com
    Bitcoin: 3DXiJxie6En3wcyxjmKZeY2zFLEmK8y42U
    Other options @ http://michaelfulcher.yolasite.com/
"""
'''[0] Name of Subject, [1] Days to iterate required hours up and Amount of hours per day in,
[2] Start date, [3] End Date, [4] Hours done'''

def save_json(f_data: dict, json_path: str, label: str) -> None:
    json_path_old = json_path[:-4] + 'old'
    json_path_old2 = json_path_old + '2'
    if path.isfile(json_path):
        if path.isfile(json_path_old):
            if path.isfile(json_path_old2):
                file_del(json_path_old2)
            file_rename(json_path_old, json_path_old2)
        file_rename(json_path, json_path_old)
    with open(json_path, 'w', encoding='utf-8') as out:
        json.dump(f_data, out, ensure_ascii=False, indent=4)
    log_tools.tprint(label + ' JSON Written')

def menu_char_check(a_word: str, options: str) -> bool:
    message = " is not a valid input"
    if len(a_word) == 0:
        print("Enter" + message)
    elif len(a_word) == 1 and a_word in options:
        return True
    else:
        print(a_word + message)
    return False

'''Found @: https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python#_=_'''
def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, '%d/%m/%Y').date()
        return True
    except ValueError:
        print(date_text + " not a valid input")
        return False

def get_date() -> str:
    while 1:
        date = input("Enter Date (dd/mm/yyyy):")
        if validate_date(date):
            return date

def validate_start_date(end_date: str, old: str) -> str:
    while 1:
        print(f"\nStart Date, format - dd/mm/yyyy. Current Date ({old})")
        start_date = get_date()
        if datetime.strptime(end_date, '%d/%m/%Y').date() > datetime.strptime(start_date, '%d/%m/%Y').date():
            print(f"Start date must be before the end date ({end_date}).")
        else:
            return start_date

def validate_end_date(start_date: str, old: str = None) -> str:
    while 1:
        if old:
            print(f"\nEnd Date, format - dd/mm/yyyy. Current Date ({old})")
        else:
            print("\nEnd Date, format - dd/mm/yyyy.")
        end_date = get_date()
        if datetime.strptime(end_date, '%d/%m/%Y').date() < datetime.strptime(start_date, '%d/%m/%Y').date():
            print(f"End date must be after the start date ({start_date}).")
        else:
            return end_date

'''found @: https://stackoverflow.com/questions/9044084/efficient-date-range-overlap-calculation-in-python
    requires passed vars to be datetime objects'''
def overlap_check(start_of_range1, end_of_range1, start_of_range2, end_of_range2) -> bool:
    latest_start = max(start_of_range1, start_of_range2)
    earliest_end = min(end_of_range1, end_of_range2)
    delta = (earliest_end - latest_start).days + 1
    if delta > 0:
        return True
    else:
        return False

def tally_hours(start_date: str, end_date: str, day_dict: dict) -> int:
    date_start = datetime.strptime(start_date, '%d/%m/%Y').date()
    date_today = datetime.today().date()
    if date_today < date_start:
        return 0
    date_end = datetime.strptime(end_date, '%d/%m/%Y').date()
    if date_end < date_today:
        date_today = date_end
    range_list = [[date_start, date_today]]
    if 'holidays' in data and len(data['holidays']) > 0:
        holiday_list = list()
        holiday_dict = dict()
        for name, date in data['holidays'].items():
            holiday_start = datetime.strptime(date[0], '%d/%m/%Y').date()
            holiday_end = datetime.strptime(date[1], '%d/%m/%Y').date()
            if overlap_check(date_start, date_today, holiday_start, holiday_end):
                holiday_list.append(name)
                holiday_dict[name] = [holiday_start, holiday_end]
        one_day = timedelta(days=1)
        rangelist_size = 1
        for holiday in holiday_dict.values():
            n = 0
            while n < rangelist_size:  # holiday_start = holiday[0], holiday_end = holiday[1]
                # term_end = range_list[n][1], term_start = range_list[n][0]
                if holiday[0] > range_list[n][1] or holiday[1] < range_list[n][0]:  # filter out pointless tests
                    n += 1
                    continue
                if holiday[0] <= range_list[n][0]:  # holiday starts before or start of term
                    if holiday[1] >= range_list[n][1]:
                        range_list.pop(n)
                        rangelist_size -= 1
                    else:
                        range_list[n][0] = holiday[1] + one_day
                        n += 1
                else:  # holiday starts after 'term' starts.
                    new_end = holiday[0] - one_day
                    if holiday[1] < range_list[n][1]:
                        range_list.append([holiday[1] + one_day, range_list[n][1]])
                        range_list[n][1] = new_end
                        rangelist_size += 1
                        break
                    else:
                        range_list[n][1] = new_end
                        n += 1
    n = 0  # n var repurposed to grand total of hours
    weeks_hours = 0
    for hour in day_dict.values():
        weeks_hours += hour
    for i in range_list:        
        weeks = i[0].weekday()
        days = (i[1] - i[0]).days + (1 if weeks == 0 else weeks - 6)
        while weeks not in [0, 7]:
            sch = str(weeks)
            if sch in day_dict.keys():
                n += day_dict[sch]
            weeks += 1
        weeks = days // 7  # weeks repurposed to 'number of weeks'
        days = days % 7  # days var repurposed to length of week.
        n += weeks * weeks_hours
        if days != 0:
            weeks = i[1].weekday()  # weeks repurposed to 'day of week number'
            while days >= 0:
                sch = str(weeks)
                if sch in day_dict.keys():
                    n += day_dict[sch]
                days -= 1
                if weeks == 0:
                    weeks = 6
                else:
                    weeks -= 1
    return n

def tabs_list(a_list: list):  # generate data for correct spacing in data display columns
    t_width = n = 0
    tabs = list()
    for item_name in a_list:
        tabs.append(len(item_name))
        if tabs[n] > t_width:
            t_width = tabs[n]
        n += 1
    n -= 1
    if t_width % 8 == 0:
        add_space = True
    else:
        add_space = False
    t_width = ceil(t_width/8)
    while n >= 0:
        tabs[n] = t_width - tabs[n]//8
        n -= 1
    return t_width, add_space, tabs

def display_holiday_list(add_numbers: bool = False) -> int:
    t_width, add_space, tabs = tabs_list([*data['holidays'].keys()])
    add_numbers_str = '\t' if add_numbers else ''
    tab_section = '\t' * t_width
    print(f"\nSaved Holidays:\n{add_numbers_str}Name{tab_section}{' ' if add_space else ''}Start Date\tEnd Date")
    n = 0
    for holiday, dates in data['holidays'].items():
        add_numbers_str = str(n) + '.\t' if add_numbers else ''
        tab_section = '\t' * tabs[n]
        print(f"{add_numbers_str}{holiday}{tab_section}{' ' if add_space else ''}{dates[0]}\t{dates[1]}")
        n += 1
    return n

def hours_display(item1: str, item2: str) -> str:
    output = str()
    if settings['display completed %']:
        output += item1
    else:
        if settings['display extra completed'] and not settings['display extra completed %']:
            output += '\t'
    if settings['display extra completed']:
        if settings['display completed %']:
            output += '\t'
        else:
            if settings['display extra completed %']:
                output += '\t'
        output += item2
    return output

def main_menu() -> chr:
    valid_option = False
    # add past work and work hours needed to meet obligation
    if "subjects" in data and len(data["subjects"]) > 0:
        items_present = True
        t_width, add_space, tabs = tabs_list([i[0] for i in data['subjects']])
    else:
        items_present = False
    while not valid_option:
        if items_present:
            tabs_section = '\t' * t_width
            line_end = hours_display("\t%", "|Extra Completed")
            line = f'\nTally totals:\nName{tabs_section}{" " if add_space else ""}Hours Owing\tHours Completed{line_end}'
            if settings['display extra completed %']:
                if not settings['display extra completed']:
                    line += '\t|'
                line += ' %'
            print(line)
            n = 0
            for subject in data["subjects"]:
                hours = tally_hours(subject[2], subject[3], subject[1])
                tabs_section = "\t" * tabs[n]
                line = f'{subject[0]}{tabs_section}{" " if add_space else ""}{hours}\t\t{subject[4][0]}h {subject[4][1]}m\t'
                if subject[4][0] == 0 and subject[4][1] == 0 or hours == 0:
                    percent = 0
                    zero_in_normal_hours = True
                else:
                    percent = (subject[4][0] * 60 + subject[4][1]) / (hours * 60)
                    zero_in_normal_hours = False
                line += hours_display(f'\t{percent * 100:.1f}%', f'|{subject[5][0]}h {subject[5][1]}m\t')
                if settings['display extra completed %']:
                    if not settings['display extra completed']:
                        line += '\t|'
                    else:
                        line += '\t '
                    percent = 0 if zero_in_normal_hours == True and subject[5][0] == 0 and subject[5][1] == 0 else ((subject[4][0] + subject[5][0]) * 60 + subject[4][1] + subject[5][1]) / (hours * 60)
                    line += f'{percent * 100:.1f}%'
                print(line)
                n += 1
        else:
            print("Subject list is empty.")
        print('\n\t--MAIN MENU--\n\tAdd to (T)ally\n\tUse t(I)mer to Add to Tally\n\t(A)dd Subject\n\t(R)emove Subject\n\t(E)dit Subject\n\t(H)olidays Menu\n\t(S)ettings Menu\n\te(X)it')
        menu_option = input("Choose Option:").upper()
        valid_option = menu_char_check(menu_option, 'TIXAREHS')
    return menu_option

def print_selected_days(day_list: list) -> None:
    if len(day_list) > 0:
        print("\nSelected Days:")
        for i in day_list:
            print(weekdays[int(i)])
    else:
        print("No days Selected")

def setup_day_options(start_date, end_date, need_length: bool = True):
    if type(start_date) == str:
        start_date_obj = datetime.strptime(start_date, '%d/%m/%Y').date()
        end_date_obj = datetime.strptime(end_date, '%d/%m/%Y').date()
    else:
        start_date_obj = start_date
        end_date_obj = end_date
    length = (end_date_obj - start_date_obj).days + 1
    if length == 1:
        if need_length:
            return day_options[start_date_obj.weekday()], length
        else:
            return day_options[start_date_obj.weekday()]
    elif length < 7:
        first_day = start_date_obj.weekday()
        last_day = first_day + length
        s_day_options = day_options[first_day:last_day]
        if last_day > 7:
            last_day -= 7
            s_day_options = day_options[0:last_day] + s_day_options
        if need_length:
            return s_day_options, length
        else:
            return s_day_options
    else:
        if need_length:
            return day_options, length
        else:
            return day_options

def check_digit(num_str: str, allow_enter_be_zero: bool):
    if num_str == '':
        if allow_enter_be_zero:
            return True, 0
        else:
            print('<Enter> is not valid input.')
            return False, 0
    elif num_str.isdecimal():
        return True, int(num_str)
    else:
        print("Input must be a decimal number.")
        return False, 0

def get_time_digit(time_div_str: str) -> int:
    valid_num = False
    while not valid_num:
        selector = input('Number of {}(s) to add:'.format(time_div_str))
        valid_num, digit = check_digit(selector, True)
    return digit

def get_hour(day_num: int) -> int:
    valid_num = False
    while not valid_num:
        selector = input("Number of hours for {}:".format(weekdays[day_num]))
        valid_num, digit = check_digit(selector, False)
    return digit

def create_days_dict(s_day_options: str, length: int, return_day_list: bool=False, days=dict()):
    if length == 1:
        length = day_options.find(s_day_options)  # length is repurposed to index of 'day_option' index
        day_str = str(length)
        days[day_str] = None
        print("Course is one day, day is auto-set to " + weekdays[length])
    else:
        if return_day_list:
            day_list = list()
        day_pick_number = 0
        while 1:
            print_selected_days(days)
            output = str()
            for day in s_day_options:
                output += menu_weekdays[day_options.find(day)] + ", "
            print('\n--SELECT DAYS--\n{}\nEnter X when finished.'.format(output[:-2]))
            selector = input('Option:').upper()
            if menu_char_check(selector, s_day_options + 'X'):
                if selector == "X":
                    break
                day_str = str(day_options.find(selector))
                days[day_str] = None
                if return_day_list:
                    day_list.append(day_str)
                day_pick_number += 1
                if day_pick_number == length:
                    break
                n = s_day_options.rfind(selector)
                s_day_options = s_day_options[:n] + s_day_options[n + 1:]
    for day in days:
        if not days[day]:
            days[day] = get_hour(int(day))
    if return_day_list:
        return days, day_list
    else:
        return days

def get_name(type_text: str, name_list: list) -> str:
    while 1:
        name = input("Name of {}:".format(type_text))
        if len(name) > 0:
            if name not in name_list:
                return name
            else:
                print("Name {} already exists.".format(name))
        else:
            print("Name must be at least 1 character.")

def add_menu() -> list:
    name_list = [x[0] for x in data['subjects']]
    print('\n\t--ADD SUBJECT--')
    name = get_name('Subject', name_list)
    print("\n\tStart Date, format - dd/mm/yyyy.")
    start_date = get_date()
    end_date = validate_end_date(start_date)
    days = create_days_dict(*setup_day_options(start_date, end_date))
    log_tools.tprint("Added Subject - " + name)
    return [name, days, start_date, end_date, [0, 0], [0, 0]]

def display_subject_list() -> int:
    t = 0
    for subject in data["subjects"]:
        print("\t{} - {}".format(str(t), subject[0]))
        t += 1
    return t

def validate_selector(a_string: str, num: int) -> bool:
    if a_string.isnumeric():
        a = int(a_string)
        if 0 <= a < num:
            return True
        else:
            print(a_string + " is not a valid option")
            return False

def remove_menu() -> bool:
    if "subjects" in data and len(data['subjects']) > 0:
        while 1:
            print("\n--REMOVE MENU--")
            n = display_subject_list()
            selector = input("Subject to remove:").upper()
            if selector == "X":
                return False
            elif validate_selector(selector, n):
                old = data["subjects"].pop(int(selector))[0]
                log_tools.tprint("Removed Subject - " + old)
                return True
    print("\nSubject list is empty.")
    return False

def check_day_range(start_date_obj, end_date_obj, old_day_range):
    new_day_range = setup_day_options(start_date_obj, end_date_obj, False)
    new_day_range_list = [str(day_options.find(x)) for x in new_day_range]
    day_list = list()  # days that may be removed later
    day_range_change = False
    for day in old_day_range:
        if day not in new_day_range_list:
            day_range_change = True
            day_list.append(day)
    return day_range_change, day_list

def remove_days_from_dict(subject: int, remove_list: list) -> None:
    for i in remove_list:
        data['subjects'][subject][1].pop(i)

def change_date(subject: int, date2change: int, date_word_str: str, length: int, new_start_date_obj, new_end_date_obj, new_date: str) -> None:
    if length < 7:
        day_range_change, day_list = check_day_range(new_start_date_obj, new_end_date_obj, [*data['subjects'][subject][1].keys()])
        if day_range_change:
            log_output = str()
            question_str = "Is this correct?\n(Y)es to make changes\n(N)o to cancel changes\n:"
            for day in day_list:
                log_output += weekdays[int(day)] + ", "
            log_out_msg = log_output[:-2] + " will be removed.\n"
            if length == 1:
                while 1:
                    day_of_week = new_start_date_obj.weekday()
                    day_of_week_str = str(day_of_week)
                    selector = input("\nDetected that your new day range is one day, day will be auto-set to {}{s}{a}".format(weekdays[day_of_week], s="." if len(log_output) == 0 else " and " + log_out_msg, a=question_str)).upper()
                    if selector == "N":
                        break
                    elif selector == "Y":
                        old = data['subjects'][subject][date2change]
                        data['subjects'][subject][date2change] = new_date
                        if day_of_week_str in data['subjects'][subject][1].keys():
                            remove_days_from_dict(subject, day_list)
                            log_tools.tprint("Changed {} {} date from {} to {} and removed {}. (Not Saved)".format(data['subjects'][subject][0], date_word_str, old, data['subjects'][subject][date2change], log_output[:-2]))
                        else:
                            remove_days_from_dict(subject, day_list)
                            data['subjects'][subject][1][day_of_week_str] = get_hour(int(day_of_week))
                            log_tools.tprint("Changed {} {} date from {} to {}, added {} and removed {}. (Not Saved)".format(data['subjects'][subject][0], date_word_str, old, data['subjects'][subject][date2change], weekdays[day_of_week], log_output[:-2]))
                        break
                    else:
                        print("Invalid input.")
            else:
                while 1:
                    selector = input("\nDetected that your new day range is less than the old day range.\n{}{}".format(log_out_msg, question_str)).upper()
                    if selector == "N":
                        break
                    elif selector == "Y":
                        remove_days_from_dict(subject, day_list)
                        old = data['subjects'][subject][date2change]
                        data['subjects'][subject][date2change] = new_date
                        log_tools.tprint("Changed {} {} date from {} to {} and removed {}. (Not Saved)".format(data['subjects'][subject][0], date_word_str, old, data['subjects'][subject][date2change], log_output[:-2]))
                        break
                    else:
                        print("Invalid input.")
    else:
        old = data['subjects'][subject][date2change]
        data['subjects'][subject][date2change] = new_date
        log_tools.tprint("Changed {} {} date from {} to {}. (Not Saved)".format(data['subjects'][subject][0], date_word_str, old, data['subjects'][subject][date2change]))

def edit_time_tally(subject_choice: int, time_category: int) -> None:
    selector = None
    print("\n--Edit {a} Tally of {b}--\nCurrent Tally: {c}h {d}m\nChanges are done by subtracting, not by directed edit.".format(a="Normal" if time_category == 4 else "Extra", b=data['subjects'][subject_choice][0], c=str(data['subjects'][subject_choice][time_category][0]), d=str(data['subjects'][subject_choice][time_category][1])))
    while selector != 'X':
        selector = input("--Field to edit:\n1. Hour\n2. Minute\ne(X)it without saving\n:").upper()
        if selector == '1':
            while 1:
                selector = input("Decrease hour by:").upper()
                if selector == 'X':
                    break
                elif selector.isdigit():
                    n = int(selector)
                    if data['subjects'][subject_choice][time_category][0] < n:
                        print("Amount to subtract cannot be larger than current hours ({}h)".format(str(data['subjects'][subject_choice][time_category][0])))
                    else:
                        old = data['subjects'][subject_choice][time_category][0]
                        data['subjects'][subject_choice][time_category][0] -= n
                        log_tools.tprint("Decreased {} - hour by {} from {}h to {}h. (Not Saved).".format(data['subjects'][subject_choice][0], selector, str(old), str(data['subjects'][subject_choice][time_category][0])))
                        selector = 'X'
                        break
                else:
                    print("Input must be a number")
        elif selector == '2':
            while 1:
                selector = input("Decrease minutes by (can subtract greater than 59minutes):").upper()
                if selector == 'X':
                    break
                elif selector.isdigit():
                    n = int(selector)
                    old = data['subjects'][subject_choice][time_category][0] * 60 + data['subjects'][subject_choice][time_category][1]
                    if n > old:
                        print("Amount to subtract cannot be larger then current hours + minutes ({}h {}m)".format(str(data['subjects'][subject_choice][time_category][0]), str(data['subjects'][subject_choice][time_category][1])))
                    else:
                        old = data['subjects'][subject_choice][time_category][0]
                        old_minute = data['subjects'][subject_choice][time_category][1]
                        data['subjects'][subject_choice][time_category][1] -= n
                        while data['subjects'][subject_choice][time_category][1] < 0:
                            data['subjects'][subject_choice][time_category][1] += 60
                            data['subjects'][subject_choice][time_category][0] -= 1
                        log_tools.tprint("Decreased {} - {a} time by {b} from {oh}h {om}m to {h}h {m}m. (Not Saved).".format(data['subjects'][subject_choice][0], a="Normal" if time_category == 4 else "Extra", b=selector, oh=str(old), om=str(old_minute), h=str(data['subjects'][subject_choice][time_category][0]), m=str(data['subjects'][subject_choice][time_category][1])))
                        selector = 'X'
                        break
                else:
                    print("Input must be a number")
        elif selector != "X":
            print("Invalid input.")

def edit_menu() -> bool:
    if "subjects" in data and len(data['subjects']) > 0:
        while 1:
            print("\n--EDIT SUBJECT MENU--\nExit and (S)ave Changes\ne(X)it without saving")
            n = display_subject_list()
            selector = input("Subject to edit:").upper()
            if selector == 'X':
                log_tools.tprint("Exiting edit menu without saving.")
                return False
            elif selector == 'S':
                log_tools.tprint("Exiting edit menu and saving changes.")
                return True
            elif validate_selector(selector, n):
                subject_choice = int(selector)
                while 1:  # if user changes dates do check on day range and incorrect days are selected then - throw error
                    if data['subjects'][subject_choice][3] == data['subjects'][subject_choice][2]:
                        one_day_course = True
                        n = 5
                    else:
                        one_day_course = False
                        n = 7
                    print("\n--Edit Subject {}--\ne(X)it to previous menu\n(S)ave changes\n1. Name\n2. Start Date\t\t{}\n3. End Date\t\t{}{d}\n6. Remove from Normal Tally\t{nh}h {nm}m\n7. Remove from Extra Tally\t{eh}h {em}m\n::Edit a Day".format(data['subjects'][subject_choice][0], data['subjects'][subject_choice][2], data['subjects'][subject_choice][3], d="\n4. Add Day\n5. Remove Day" if one_day_course is False else "", nh=str(data['subjects'][subject_choice][4][0]), nm=str(data['subjects'][subject_choice][4][1]), eh=str(data['subjects'][subject_choice][5][0]), em=str(data['subjects'][subject_choice][5][1])))
                    for day, hour in data['subjects'][subject_choice][1].items():
                        n += 1
                        print("{}. {}\t\t{} Hour{s} ".format(n, weekdays[int(day)], hour, s='' if hour == 1 else 's'))
                    selector = input("Field to edit:").upper()
                    if selector == 'X':
                        break
                    elif selector == 'S':
                        log_tools.tprint("Exiting edit menu and saving changes.")
                        return True
                    else:
                        if validate_selector(selector, n + 1):
                            field = int(selector)
                            if (one_day_course is False and field > 7) or (one_day_course and field > 5):  # Change day hours
                                day = [*data['subjects'][subject_choice][1].keys()][field - 6 if one_day_course else field - 8]
                                while 1:
                                    day_name = weekdays[int(day)]
                                    print("\n--Edit {} {}--\n--X to exit.".format(data['subjects'][subject_choice][0], day_name))
                                    num = input("Number of hours:").upper()
                                    if num.isdecimal():
                                        old = data['subjects'][subject_choice][1][day]
                                        data['subjects'][subject_choice][1][day] = int(num)
                                        log_tools.tprint("Changed {} {} time from {} to {}. (Not Saved)".format(data['subjects'][subject_choice][0], day_name, str(old), str(data['subjects'][subject_choice][1][day])))
                                        break
                                    elif num == "X":
                                        break
                                    else:
                                        print("Number must be a decimal number.")
                            else:
                                if field == 1:  # Change Name
                                    name = input("\nNew name of Subject:")
                                    if len(name) > 0:
                                        old = data['subjects'][subject_choice][0]
                                        data['subjects'][subject_choice][0] = name
                                        log_tools.tprint("Renamed {} to {}".format(old, data['subjects'][subject_choice][0]))
                                    else:
                                        print("Name must be at least 1 character.")
                                        break
                                elif field == 2:  # Change start date
                                    # old = data['subjects'][subject_choice][2]
                                    while 1:
                                        print("\nStart Date, format - dd/mm/yyyy. Current Date ({})".format(data['subjects'][subject_choice][2]))
                                        new_date = get_date()
                                        new_date_obj = datetime.strptime(new_date, '%d/%m/%Y').date()
                                        end_date_obj = datetime.strptime(data['subjects'][subject_choice][3], '%d/%m/%Y').date()
                                        if end_date_obj < new_date_obj:
                                            print("Start date must be before the end date ({}).".format(data['subjects'][subject_choice][3]))
                                        else:
                                            break
                                    change_date(subject_choice, 2, "start", (end_date_obj - new_date_obj).days + 1, new_date_obj, end_date_obj, new_date)
                                elif field == 3:  # Change end date
                                    new_date = validate_end_date(data['subjects'][subject_choice][2])
                                    start_date_obj = datetime.strptime(data['subjects'][subject_choice][2], '%d/%m/%Y').date()
                                    new_date_obj = datetime.strptime(new_date, '%d/%m/%Y').date()
                                    change_date(subject_choice, 3, "end", (new_date_obj - start_date_obj).days + 1, start_date_obj, new_date_obj, new_date)
                                elif field == 4:  # Add days
                                    s_day_options, length = setup_day_options(data['subjects'][subject_choice][2], data['subjects'][subject_choice][3])
                                    for day in data['subjects'][subject_choice][1].keys():
                                        n = s_day_options.rfind(day_options[int(day)])
                                        s_day_options = s_day_options[:n] + s_day_options[n + 1:]
                                    print(s_day_options)
                                    data['subjects'][subject_choice][1], day_list = create_days_dict(s_day_options, length, True, data['subjects'][subject_choice][1])
                                    log_output = str()
                                    for day in day_list:
                                        log_output += "{} {} hour{s}, ".format(weekdays[int(day)], str(data['subjects'][subject_choice][1][day]), s="" if data['subjects'][subject_choice][1][day] == 1 else "s")
                                    log_tools.tprint("Added to {} - {}. (Not Saved)".format(data['subjects'][subject_choice][0], log_output[:-2]))
                                elif field == 5:  # Remove a day
                                    print("\n--Remove a day from {}--".format(data['subjects'][subject_choice][0]))
                                    days = [*data['subjects'][subject_choice][1].keys()]
                                    while 1:
                                        n = 0
                                        for day, hour in data['subjects'][subject_choice][1].items():
                                            n += 1
                                            print("{}. {}\t Hour{a}: {b}".format(str(n), weekdays[int(day)], a="" if hour == 1 else "s", b=str(hour)))
                                        selector = input("Field to edit:").upper()
                                        if selector == 'X':
                                            break
                                        elif validate_selector(selector, n + 1):
                                            n = int(selector) - 1
                                            data['subjects'][subject_choice][1].pop(days[n])
                                            log_tools.tprint("Removed {} from {}. (Not Saved)".format(weekdays[int(days[n])], data['subjects'][subject_choice][0]))
                                            break
                                elif field == 6:  # Edit Normal Tally
                                    edit_time_tally(subject_choice, 4)
                                elif field == 7:  # Edit Extra Tally
                                    edit_time_tally(subject_choice, 5)
    else:
        print("\nSubject list is empty.")
    return False

def add_to_daily_tally(hour, minute):
    pass

def add_hour_minute(subject: int, time_category: int, hour: int, minute: int) -> None:
    old_hour = data['subjects'][subject][time_category][0]
    old_minute = data['subjects'][subject][time_category][1]
    data['subjects'][subject][time_category][0] += hour
    data['subjects'][subject][time_category][1] += minute
    while data['subjects'][subject][time_category][1] > 59:
        data['subjects'][subject][time_category][1] -= 60
        data['subjects'][subject][time_category][0] += 1
    ## add daily tally here
    log_tools.tprint("Increased {}{a} Hours from {b}h {c}m to {d}h {e}m.".format(data['subjects'][subject][0], a=" Normal" if time_category == 4 else " Extra", b=str(old_hour), c=str(old_minute), d=str(data['subjects'][subject][time_category][0]), e=str(data['subjects'][subject][time_category][1])))

def time_convert_str(sec: float) -> str:
    mins = sec // 60
    sec = int(sec % 60)
    hours = int(mins // 60)
    mins = int(mins % 60)
    return f"{'0' + str(hours) if hours < 10 else str(hours)}:{'0' + str(mins) if mins < 10 else str(mins)}:{'0' + str(sec) if sec < 10 else str(sec)}"

'''Found this getwch() method in getpass.py @ https://github.com/python/cpython/blob/3.8/Lib/getpass.py'''
def thread_timer_cancel() -> None:
    global s
    while 1:
        c = getwch()
        if c == '\r' or c == '\n':
            s = False
            print('\n')
            break
        if c == '\003':
            raise KeyboardInterrupt

def timer_tally() -> bool:
    global s
    if "subjects" in data and len(data['subjects']) > 0:
        if use_live_update_timer:
            x = threading.Thread(target=thread_timer_cancel)
        while 1:
            print("\n\t--TIMER MENU--")
            n = display_subject_list()
            selector = input("Subject to add tally to:").upper()
            if selector == "X":
                return False
            elif validate_selector(selector, n):
                selector = int(selector)
                time_category = 5 if datetime.strptime(log_tools.run_date, '%d-%m-%Y').date() > datetime.strptime(data['subjects'][selector][3], '%d/%m/%Y').date() else 4
                print("\nAdding to Tally of " + data['subjects'][selector][0])
                print('NOTE: Time spans lower than 1 minute will not be saved.')
                c = input('\nPress Enter to start or X to Exit:').upper()
                if c == 'X':
                    return False
                elif c == '':
                    start_time = time.time()
                    log_tools.tprint(f"Timer for {data['subjects'][selector][0]} started")
                    if use_live_update_timer:
                        x.start()
                        print('Press Enter to stop timer')
                        while s:
                            current_time = time.time()
                            sys.stdout.write('\rTime Lapsed = ' + time_convert_str(current_time - start_time))
                            sys.stdout.flush()
                            time.sleep(0.5)
                    else:
                        while s:
                            c = input('Press Enter to stop timer')
                            if c == '':
                                s = False
                            else:
                                print('Invalid command.')
                    current_time = time.time()
                    current_time = current_time - start_time  # current_time repurposed to length of time span
                    current_time = int(current_time // 60)  # current_time repurposed to minutes
                    hours = current_time // 60
                    current_time = current_time % 60
                    print('Timer stopped at {}\n'.format('{0} minute{s}'.format(current_time, s='' if current_time == 1 else 's') if hours == 0 else '{0} hour{s} {m}'.format(hours, s=' ' if hours == 1 else 's ', m='{0} minute{s}'.format(current_time, s='' if current_time == 1 else 's'))))
                    s = True
                    if current_time != 0 or hours != 0:
                        add_hour_minute(selector, time_category, hours, current_time)
                        return True
                    else:
                        log_tools.tprint(f'Time span for {data["subjects"][selector][0]} was less than 1 minute, nothing saved.')
                        return False
                else:
                    print('Invalid command, returning to main menu.')
                    return False
    print("Subject list in empty.")
    return False

def add_to_tally() -> bool:
    if "subjects" in data and len(data['subjects']) > 0:
        while 1:
            print("\n\t--TALLY MENU--")
            n = display_subject_list()
            selector = input("Subject to add tally to:").upper()
            if selector == "X":
                return False
            elif validate_selector(selector, n):
                selector = int(selector)
                time_category = 5 if datetime.strptime(log_tools.run_date, '%d-%m-%Y').date() > datetime.strptime(data['subjects'][selector][3], '%d/%m/%Y').date() else 4
                print("Adding to Tally of " + data['subjects'][selector][0])
                if settings['tallyEditHour']:
                    hour = get_time_digit('hour')
                else:
                    hour = 0
                if settings['tallyEditMinute']:
                    minute = get_time_digit('minute')
                else:
                    minute = 0
                add_hour_minute(selector, time_category, hour, minute)
                return True
    print("Subject list in empty.")
    return False

def holiday_menu() -> bool:
    while 1:
        if len(data['holidays']) > 0:
            holiday_names = [*data['holidays'].keys()]
            display_holiday_list()
            num_options = True
            print("\n\t--HOLIDAY MENU--\n\tExit and (S)ave Changes\n\te(X)it without saving\n\t1. Add Holiday\n\t2. Remove Holiday\n\t3. Edit Holiday")
        else:
            print('\nNo holidays saved.')  # make menu change when holiday list empty...
            holiday_names = list()
            num_options = False
            print('\n\t--HOLIDAY MENU--\n\tExit and (S)ave Changes\n\te(X)it without saving\n\t1. Add Holiday\n')
        selector = input(("Option:" if num_options else "Field to edit:")).upper()
        if menu_char_check(selector, 'SX' + ('1' if num_options is False else '123')):
            if selector == '1':
                name = get_name('Holiday', holiday_names)
                print("\nStart Date, format - dd/mm/yyyy.")
                start_date = get_date()
                end_date = validate_end_date(start_date)
                holiday_names.append(name)
                data['holidays'][name] = [start_date, end_date]
                log_tools.tprint('Added {} to Saved Holidays. (Not Saved).'.format(name))
            elif selector == '2':
                while 1:
                    print('\n\t--REMOVE HOLIDAY MENU--\n\te(X)it\n')
                    n = display_holiday_list(True)
                    field = input('Holiday to remove:').upper()
                    if field == "X":
                        break
                    elif validate_selector(field, n):
                        num = int(field)
                        old_name = holiday_names[num]
                        data['holidays'].pop(holiday_names[num])
                        holiday_names.pop(num)
                        log_tools.tprint("Removed {} from Saved Holidays. (Not Saved)".format(old_name))
                        break
            elif selector == '3':
                while 1:
                    print('\n\t--EDIT HOLIDAY MENU--\n\te(X)it\n')
                    n = display_holiday_list(True)
                    field = input('Holiday to edit:').upper()
                    if field == 'X':
                        break
                    elif validate_selector(field, n):
                        num = int(field)
                        while 1:
                            print('\n\t--EDIT HOLIDAY {}--\n\te(X)it to previous menu\n\t(S)ave changes\n\t1. Name\n\t2. Start Date\t{}\n\t3. End Date\t{}'.format(holiday_names[num], data['holidays'][holiday_names[num]][0], data['holidays'][holiday_names[num]][1]))
                            field = input('Field to edit:').upper()
                            if field == '1':
                                selector = get_name('holiday', holiday_names)
                                old = holiday_names[num]
                                data['holidays'][selector] = data['holidays'].pop(old)
                                holiday_names.pop(num)
                                holiday_names.append(selector)
                                log_tools.tprint("Renamed holiday - {} to {}".format(old, selector))
                                break
                            elif field == '2':
                                old = data['holidays'][holiday_names[num]][0]
                                data['holidays'][holiday_names[num]][0] = validate_start_date(data['holidays'][holiday_names[num]][1], data['holidays'][holiday_names[num]][0])
                                log_tools.tprint('Changed holiday - {} from {} to {}'.format(holiday_names[num], old, data['holidays'][holiday_names[num]][0]))
                                break
                            elif field == '3':
                                old = data['holidays'][holiday_names[num]][1]
                                data['holidays'][holiday_names[num]][1] = validate_end_date(data['holidays'][holiday_names[num]][0], data['holidays'][holiday_names[num]][1])
                                log_tools.tprint('Changed holiday - {} from {} to {}'.format(holiday_names[num], old, data['holidays'][holiday_names[num]][1]))
                                break
                            elif field == 'X':
                                break
                            else:
                                print("Invalid input.")
            elif selector == 'X':
                return False
            elif selector == 'S':
                return True

def get_description_of_tally_setting() -> str:
    return 'Both' if settings['tallyEditHour'] and settings['tallyEditMinute'] else 'Hour' if settings['tallyEditHour'] else 'Minute'

def change_tally_usage_setting(new_hour_bol: bool, new_minute_bol: bool) -> None:
    old = get_description_of_tally_setting()
    settings['tallyEditMinute'] = new_minute_bol
    settings['tallyEditHour'] = new_hour_bol
    log_tools.tprint('Changed Tally Usage - from {} to {} (Not Saved)'.format(old, get_description_of_tally_setting()))

def toggle_boolean_setting(setting_key: str) -> None:
    settings[setting_key] = not settings[setting_key]
    log_tools.tprint('Changed {} - from {} to {} (Not Saved)'.format(setting_key, str(not settings[setting_key]), str(settings[setting_key])))

def settings_menu() -> bool:
    while 1:
        print("\n\t--CURRENT SETTINGS--\n\t-Main Menu Display-\n\t1. Display Completed Percent:\t\t{}\n\t2. Display extra completed:\t\t{}\n\t3. Display extra Completed Percent:\t{}".format(str(settings['display completed %']), str(settings['display extra completed']), str(settings['display extra completed %'])))
        print('\n\t-Usage-\n\t(E)dit tallies by:\t' + get_description_of_tally_setting())
        print("\n\t-SETTINGS MENU-\n\tExit and (S)ave Changes\n\te(X)it without saving")
        selector = input('Option to toggle, or command:').upper()
        if selector == 'X':
            return False
        elif selector == 'S':
            return True
        elif selector == '1':
            toggle_boolean_setting('display completed %')
        elif selector == '2':
            toggle_boolean_setting('display extra completed')
        elif selector == '3':
            toggle_boolean_setting('display extra completed %')    
        elif selector == 'E':
            while 1:
                print('--Change Tally Edit Method--\n\t(M)inute\n\t(H)our\n\t(B)oth\n\te(X)it')
                field = input("Choose Option:").upper()
                if field == 'M':
                    change_tally_usage_setting(False, True)
                    break
                elif field == 'H':
                    change_tally_usage_setting(True, False)
                    break
                elif field == 'B':
                    change_tally_usage_setting(True, True)
                    break
                elif field == 'X':
                    break
                else:
                    print("Invalid input.")
        else:
            print("Invalid input.")

def check_for_backup(name: str, file_path: str) -> None:
    log_tools.tprint('{} file ({}) empty or corrupt.'.format(name, path.abspath(file_path)))
    if path.isfile(file_path[:-4] + 'old'):
        log_tools.tprint("Backup file (.old) is present.")
        print("\t\tIt is likely you have suffered some data loss.\t\tConsider renaming old file to JSON.")
    else:
        if path.isfile(file_path[:-4] + 'old2'):
            log_tools.tprint("Backup file (.old2) is present.")
            print("\t\tIt is highly likely you have suffered some data loss.\t\tConsider renaming old2 file to JSON.")
        else:
            log_tools.tprint("No backup {} file found.".format(name))


if __name__ == "__main__":
    if 'idlelib.run' in sys.modules:
        use_live_update_timer = False
    else:
        import threading
        from msvcrt import getwch
        use_live_update_timer = True
    log_tools.script_id = "StudyTimeTally"
    log_tools.run_date = time.strftime('%d-%m-%Y', time.localtime())
    log_tools.initialize(False)
    s = True
    menu_mode = 'm'
    day_options = 'MTWHFSU'
    data_json_path = r'.\data\study_tally_data.json'
    settings_json_path = r'.\data\study_tally_settings.json'
    weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    menu_weekdays = ("(M)onday", "(T)uesday", "(W)ednesday", "T(H)ursday", "(F)riday", "(S)aturday", "S(U)nday")

    print("Study Time Tally\n\tBy Michael Fulcher\nSend Donations to - PayPal: mjfulcher58@gmail.com or Bitcoin: 3DXiJxie6En3wcyxjmKZeY2zFLEmK8y42U -- Suggested Donation: $1.50USD\nOther donation options @ http://michaelfulcher.yolasite.com/\n\n")
    if not path.isdir(r'.\data'):
        from os import makedirs
        makedirs('data')
        log_tools.tprint("Data directory created.")
        del makedirs
    if path.isfile(data_json_path):
        with open(data_json_path, 'r') as open_file:
            try:
                data = json.load(open_file, parse_int=int)
            except json.decoder.JSONDecodeError:
                check_for_backup("Data", data_json_path)
                menu_mode = 'e'
    else:
        data = dict()
    if path.isfile(settings_json_path):
        with open(settings_json_path, 'r') as open_file:
            try:
                settings = json.load(open_file, parse_int=int)
            except json.decoder.JSONDecodeError:
                check_for_backup("Settings", settings_json_path)
                menu_mode = 'e'
    else:
        settings = dict()
        settings['display completed %'] = True
        settings['display extra completed'] = False
        settings['display extra completed %'] = False
        settings['tallyEditHour'] = True
        settings['tallyEditMinute'] = True
    while menu_mode not in ['X', 'e']:
        if menu_mode == 'm':
            menu_mode = main_menu()
        elif menu_mode == 'T':
            if add_to_tally():
                save_json(data, data_json_path, "Data")
            menu_mode = 'm'
        elif menu_mode == 'I':
            if timer_tally():
                save_json(data, data_json_path, "Data")
            menu_mode = 'm'
        elif menu_mode == 'A':
            if 'subjects' not in data:
                data['subjects'] = list()
            data['subjects'].append(add_menu())
            save_json(data, data_json_path, "Data")
            menu_mode = 'm'
        elif menu_mode == 'R':
            if remove_menu():
                save_json(data, data_json_path, "Data")
            menu_mode = 'm'
        elif menu_mode == 'E':
            if edit_menu():
                save_json(data, data_json_path, "Data")
            menu_mode = 'm'
        elif menu_mode == 'H':
            if 'holidays' not in data:
                data['holidays'] = dict()
            if holiday_menu():
                save_json(data, data_json_path, "Data")
            menu_mode = 'm'
        elif menu_mode == 'S':
            if settings_menu():
                save_json(settings, settings_json_path, "Settings")
            menu_mode = 'm'
    if menu_mode == 'e':
        print("\nExited on error.")
    else:
        print("\nBye.")
