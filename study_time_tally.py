import json
import sys
import time
from datetime import timedelta, datetime, date
from math import ceil
from os import path
from tools.file import save_json
import sqlite3
from contextlib import closing
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
        if datetime.strptime(end_date, '%d/%m/%Y').date() < datetime.strptime(start_date, '%d/%m/%Y').date():
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
    return True if delta > 0 else False

def tally_hours(start_date: str, end_date: str, day_dict: dict, cur=None) -> int:
    date_start = datetime.strptime(start_date, '%d/%m/%Y').date()
    date_today = datetime.today().date()
    if date_today < date_start:
        return 0
    date_end = datetime.strptime(end_date, '%d/%m/%Y').date()
    if date_end < date_today:
        date_today = date_end
    range_list = [[date_start, date_today]]
    holiday_list = list()
    if cur:
        results = cur.execute("SELECT startDate, endDate FROM Holiday WHERE startDate > (?) AND endDate < (?)", (date_start.strftime('%Y-%m-%d'), date_today.strftime('%Y-%m-%d'))).fetchall()
        for holiday in results:
            holiday_list.append([datetime.strptime(holiday[0], '%Y-%m-%d').date(), datetime.strptime(holiday[1], '%Y-%m-%d').date()])
    else:
        if 'holidays' in data and len(data['holidays']) > 0:
            for name, date in data['holidays'].items():
                holiday_start = datetime.strptime(date[0], '%d/%m/%Y').date()
                holiday_end = datetime.strptime(date[1], '%d/%m/%Y').date()
                if overlap_check(date_start, date_today, holiday_start, holiday_end):
                    holiday_list.append([holiday_start, holiday_end])
    one_day = timedelta(days=1)
    rangelist_size = 1
    for holiday in holiday_list:
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
    weeks_hours = n = 0  # n var repurposed to grand total of hours
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
    add_space = True if t_width % 8 == 0 else False
    t_width = ceil(t_width / 8)
    while n >= 0:
        tabs[n] = t_width - tabs[n] // 8
        n -= 1
    return t_width, add_space, tabs

def display_holiday_list_db(add_numbers: bool, names_list: dict, id_range: dict, for_removal: list, changed_names: dict, changed_start: dict, changed_end: dict) -> int:
    new_name_list = list()
    names_list_keys = [*names_list.keys()]
    for id, name in names_list.items():
        if id in changed_names.keys():
            new_name_list.append(changed_names[id])
        else:
            new_name_list.append(name)
    new_keys = list()
    for id, name in changed_names.items():
        if id not in names_list_keys:
            new_name_list.append(name)
            new_keys.append(id)
    nums = names_list_keys + new_keys
    t_width, add_space, tabs = tabs_list(new_name_list)
    add_numbers_str = '\t' if add_numbers else ''
    tab_section = '\t' * t_width
    print(f"\nSaved Holidays:\n{add_numbers_str}Name{tab_section}{' ' if add_space else ''}Start Date\tEnd Date")
    n = 0
    for id in nums:
        add_numbers_str = str(n) + '.\t' if add_numbers else ''
        tab_section = '\t' * tabs[n]
        print(f"{add_numbers_str}{changed_names[id] if id in changed_names.keys() else names_list[id]}{tab_section}{' ' if add_space else ''}{changed_start[id] if id in changed_start.keys() else id_range[id][0]}\t{changed_end[id] if id in changed_end.keys() else id_range[id][1]}\t{'(Removed)' if id in for_removal else ''}")
        n += 1
    return n

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

def display_menu_stats(name: str, startDate, endData, days: dict, normal_hours_done: int, normal_minutes_done: int, extra_hours_done: int, extra_minutes_done: int, num_tabs: int, add_space: bool, curs=None) -> None:
    num_hours = tally_hours(startDate, endData, days, curs)
    tabs_section = "\t" * num_tabs
    line = f'{name}{tabs_section}{" " if add_space else ""}{num_hours}\t\t{normal_hours_done}h {normal_minutes_done}m\t'
    if normal_hours_done == 0 and normal_minutes_done == 0 or num_hours == 0:
        ratio = 0
        zero_in_normal_hours = True
    else:
        ratio = (normal_hours_done * 60 + normal_minutes_done) / (num_hours * 60)
        zero_in_normal_hours = False
    line += hours_display(f'\t{ratio * 100:.1f}%', f'|{extra_hours_done}h {extra_minutes_done}m\t')
    if settings['display extra completed %']:
        line += '\t ' if settings['display extra completed'] else '\t|'
        ratio = 0 if zero_in_normal_hours and extra_hours_done == 0 and extra_minutes_done == 0 else ((normal_hours_done + extra_hours_done) * 60 + normal_minutes_done + extra_minutes_done) / (num_hours * 60)
        line += f'{ratio * 100:.1f}%'
    print(line)

def get_enabled_subjects(db_loc: str) -> list:
    with closing(sqlite3.connect(db_loc)) as db_con:
        with closing(db_con.cursor()) as cur:
            return cur.execute("SELECT ID, subjectName FROM Subject WHERE enabled = 1").fetchall()

def main_menu() -> chr:
    global last_past_hours_update
    valid_option = False
    past_hours_reset = True
    if settings['useDB']:
        print('\tDatabase Mode')
        subjects = get_enabled_subjects(database_path)
        if subjects:
            items_present = True
            t_width, add_space, tabs = tabs_list([i[1] for i in subjects])
        else:
            items_present = False
    # add work hours needed to meet obligation
    else:
        print('\tJSON Mode')
        if "subjects" in data and len(data["subjects"]) > 0:
            items_present = True
            t_width, add_space, tabs = tabs_list([i[0] for i in data['subjects']])
        else:
            items_present = False
    while not valid_option:
        if items_present:
            if settings['useRecentHoursDisplay']:
                if check_fix_daily_progress() or past_hours_reset:
                    past_hours_reset = False
                    dailykey_to_dayname = dict()
                    n = last_past_hours_update.weekday()
                    for x in daily_progress_keys[::-1]:
                        if x in past_hours:
                            dailykey_to_dayname[x] = n
                        n -= 1
                        if n == -1:
                            n = 6
                print(f"\n\t{'Recent Activity:':^{20}}")
                for x in daily_progress_keys:
                    if x in past_hours and (past_hours[x][1] != 0 or past_hours[x][0] != 0):
                        print(f"\t{weekdays[dailykey_to_dayname[x]]:^{9}}: {past_hours[x][0]}h {past_hours[x][1]}m")
            tabs_section = '\t' * t_width
            line_end = hours_display("\t%", "|Extra Completed")
            line = f'\nTally totals:\nName{tabs_section}{" " if add_space else ""}Hours Owing\tHours Completed{line_end}'
            if settings['display extra completed %']:
                if not settings['display extra completed']:
                    line += '\t|'
                line += ' %'
            print(line)
            n = 0
            if settings['useDB']:
                with closing(sqlite3.connect(database_path)) as db_con:
                    with closing(db_con.cursor()) as cur:
                        for subject_item in subjects:
                            date_range = cur.execute(f"SELECT startDate, endDate FROM Subject WHERE ID = (?)", (subject_item[0],)).fetchone()
                            days = cur.execute(f"SELECT dayCode, hours FROM SubjectDay WHERE subjectID = (?)", (subject_item[0],)).fetchall()
                            days_dict = dict()
                            for item in days:
                                days_dict[str(item[0])] = item[1]
                            normal_time_result = [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 0", (subject_item[0],)).fetchone()]
                            extra_time_result = [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType IN (1, 2)", (subject_item[0],)).fetchone()]
                            correct_time_format_display(normal_time_result)
                            correct_time_format_display(extra_time_result)
                            display_menu_stats(subject_item[1], datetime.strptime(date_range[0], '%Y-%m-%d').strftime('%d/%m/%Y'), datetime.strptime(date_range[1], '%Y-%m-%d').strftime('%d/%m/%Y'), days_dict, normal_time_result[0], normal_time_result[1], extra_time_result[0], extra_time_result[1], tabs[n], add_space, cur)
                            n += 1
            else:
                for subj in data["subjects"]:
                    display_menu_stats(subj[0], subj[2], subj[3], subj[1], subj[4][0], subj[4][1], subj[5][0], subj[5][1], tabs[n], add_space)
                    n += 1
        else:
            print("Subject list is empty.")
        print('\n\t--MAIN MENU--\n\tAdd to (T)ally\n\tUse t(I)mer to Add to Tally\n\t(A)dd Subject\n\t(R)emove Subject\n\t(E)dit Subject\n\t(H)olidays Menu\n\t(S)ettings Menu\n\te(X)it')
        menu_option = input("Choose Option:").upper()
        valid_option = menu_char_check(menu_option, 'TIXAREHS')
    return menu_option

def check_fix_daily_progress():
    global last_past_hours_update
    n = (datetime.now().date() - last_past_hours_update).days
    if n == 0:
        return False
    for j in range(n):
        for i in range(7):
            if i == 6:
                past_hours[daily_progress_keys[6]] = [0, 0]
            else:
                if daily_progress_keys[i + 1] not in past_hours:
                    if daily_progress_keys[i] in past_hours:
                        past_hours.pop(daily_progress_keys[i])
                else:
                    past_hours[daily_progress_keys[i]] = past_hours[daily_progress_keys[i + 1]]
    last_past_hours_update = datetime.now().date()
    return True

def print_selected_days(day_list: list) -> None:
    if day_list:
        print("\nSelected Days:")
        for i in day_list:
            print(weekdays[int(i)])
    else:
        print("No days Selected")

def setup_day_options(start_date, end_date, need_length: bool = True):
    """Uses global day_options = "MTWTFSS" to generate options according to length of time period (end_date_obj - start_date_obj).days + 1"""
    if type(start_date) == str:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d' if settings['useDB'] else '%d/%m/%Y').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d' if settings['useDB'] else '%d/%m/%Y').date()
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
        selector = input(f'Number of {time_div_str}(s) to add:')
        valid_num, digit = check_digit(selector, True)
    return digit

def get_hour(day_num: int) -> int:
    valid_num = False
    while not valid_num:
        selector = input(f"Number of hours for {weekdays[day_num]}:")
        valid_num, digit = check_digit(selector, False)
    return digit

def create_days_dict(s_day_options: str, length: int, return_day_list: bool = False, days=dict()):
    """Creates dictionary of given options str, length, return_day_list: bool, days dict: optional

    Returns dict of days
    if return_day_list = True
    Returns dict of days, days_options str"""
    if length == 1:
        length = day_options.find(s_day_options)  # length is repurposed to index of 'day_option' index
        day_str = str(length)
        days[day_str] = None
        print("Course is one day, day is auto-set to " + weekdays[length])
    else:
        day_pick_number = 0
        if return_day_list:
            day_list = list()
        while 1:
            print_selected_days(days)
            output = str()
            for d in s_day_options:
                output += menu_weekdays[day_options.find(d)] + ", "
            print(f'\n--SELECT DAYS--\n{output[:-2]}\nEnter X when finished.')
            selector = input('Option:').upper()
            if menu_char_check(selector, s_day_options + 'X'):
                if selector == "X":
                    break
                if settings['useDB']:
                    day_options_pos = day_options.find(selector)
                    days[day_options_pos] = None
                    day_str = str(day_options_pos)
                else:
                    day_str = str(day_options.find(selector))
                    days[day_str] = None
                if return_day_list:
                    day_list.append(day_str)
                day_pick_number += 1
                if day_pick_number == length:
                    break
                n = s_day_options.rfind(selector)
                s_day_options = s_day_options[:n] + s_day_options[n + 1:]
    for d in days:
        if not days[d]:
            days[d] = get_hour(int(d))
    if return_day_list:
        return days, day_list
    else:
        return days

def get_name(type_text: str, name_list: list) -> str:
    while 1:
        name = input(f"Name of {type_text}:").strip()
        if name:
            if name in name_list:
                print(f"Name {name} already exists.")
            else:
                return name
        else:
            print("Name must be at least 1 character.")

def add_menu_common():
    print('\n\t--ADD SUBJECT--')
    print("\n\tStart Date, format - dd/mm/yyyy.")
    start = get_date()
    end = validate_end_date(start)
    days = create_days_dict(*setup_day_options(datetime.strptime(start, '%d/%m/%Y').date() if settings['useDB'] else start, datetime.strptime(end, '%d/%m/%Y').date() if settings['useDB'] else end))
    return days, start, end

def add_menu_db() -> None:
    while 1:
        name = input(f"Name of Subject:").strip()
        if name:
            with closing(sqlite3.connect(database_path)) as db_con:
                with closing(db_con.cursor()) as cur:
                    result = cur.execute("SELECT ID, enabled FROM Subject WHERE subjectName IS (?)", (name,)).fetchone()
            if result:
                if result[1] == 0:  ## if already exists and is disabled, ask to re-enable
                    while (field := input(f'Name {name} already exists and is disabled, do you want to enable it, (Y)es or (N)o?').upper()) != 'N':
                        if field == 'Y':
                            with closing(sqlite3.connect(database_path)) as db_con:
                                with closing(db_con.cursor()) as cur:
                                    db_trans_change_display_setting(cur, result[0], name, True)
                                    db_con.commit()
                            return
                else:
                    print(f"Name {name} already exists.")
            else:
                break
        else:
            print("Name must be at least 1 character.")
    days, start_date, end_dat = add_menu_common()
    with closing(sqlite3.connect(database_path)) as db_con:
        with closing(db_con.cursor()) as cur:
            cur.execute("INSERT INTO Subject (subjectName, startDate, endDate, enabled) VALUES (?, ?, ?, 1)", (name, datetime.strptime(start_date, '%d/%m/%Y').strftime('%Y-%m-%d'), datetime.strptime(end_dat, '%d/%m/%Y').strftime('%Y-%m-%d')))
            result = cur.execute("SELECT ID FROM Subject WHERE subjectName IS (?)", (name,)).fetchone()[0]
            for d, hour in days.items():
                cur.execute("INSERT INTO SubjectDay (subjectID, dayCode, hours) VALUES (?, ?, ?)", (result, int(d), hour))
            db_con.commit()
            log_tools.tprint("DB Add: Subject - " + name)

def add_menu() -> list:
    name = get_name('Subject', [x[0] for x in data['subjects']])
    log_tools.tprint("Added Subject - " + name)
    return [name, *add_menu_common(), [0, 0], [0, 0]]

def display_subject_list() -> int:
    t = 0
    for subj in data["subjects"]:
        print("\t{} - {}".format(str(t), subj[0]))
        t += 1
    return t

def validate_selector(a_string: str, num: int, start_num: int = 0) -> bool:
    if a_string.isnumeric():
        a = int(a_string)
        if start_num <= a < num:
            return True
        else:
            print(a_string + " is not a valid option")
            return False

def remove_menu() -> bool:
    if settings['useDB']:
        with closing(sqlite3.connect(database_path)) as db_con:
            with closing(db_con.cursor()) as cur:
                subjects = cur.execute("SELECT ID, subjectName, enabled FROM Subject").fetchall()
        state_list = [subj[2] for subj in subjects]
        length = len(subjects)
        if length > 0:
            k = len(str(length))
            j = 0
            for subj in subjects:
                length = len(subj[1])
                if j < length:
                    j = length
            j += 2
            l = j + k + 11
            while 1:
                n = 0
                print(f"\n\t{'--Disable/Enable MENU--':^{l}}")
                for subj in subjects:
                    n += 1
                    print(f"\t{n:>{k}} - {subj[1]:<{j}}{'Enabled' if state_list[n - 1] == 1 else 'Disabled'}")
                selector = input("Subject to disable or enable:").upper()
                if selector == 'X':
                    break
                elif validate_selector(selector, length + 1, 1):
                    selector = int(selector) - 1
                    state_list[selector] = 0 if state_list[selector] == 1 else 1
                    with closing(sqlite3.connect(database_path)) as db_con:
                        with closing(db_con.cursor()) as cur:
                            cur.execute("UPDATE Subject SET enabled = (?) WHERE ID = (?)", (state_list[selector], subjects[selector][0]))
                            db_con.commit()
                            log_tools.tprint(f"DB Update: Subject {subjects[selector][1]} {'disabled' if state_list[selector] == 0 else 'enabled'}")
        else:
            print('No subjects found in DB')
    else:
        if "subjects" in data and len(data['subjects']) > 0:
            while 1:
                print("\n--REMOVE MENU--")
                n = display_subject_list()
                selector = input("Subject to remove:").upper()
                if selector == "X":
                    break
                elif validate_selector(selector, n):
                    old = data["subjects"].pop(int(selector))[0]
                    log_tools.tprint("Removed Subject - " + old)
                    save_json(data, data_path + 'study_tally_data.json', "Data")
                    break
        else:
            print("\nSubject list is empty.")

def check_day_range(start_date_obj, end_date_obj, old_day_range):
    new_day_range = setup_day_options(start_date_obj, end_date_obj, False)
    new_day_range_list = [str(day_options.find(x)) for x in new_day_range]
    day_list = list()  # days that may be removed later
    day_range_change = False
    for d in old_day_range:
        if d not in new_day_range_list:
            day_range_change = True
            day_list.append(d)
    return day_range_change, day_list

def remove_days_from_dict(subject: int, remove_list: list) -> None:
    for i in remove_list:
        data['subjects'][subject][1].pop(i)

def check_date_new_days_dict(length: int, new_start_date_obj, new_end_date_obj, old_days_dict: dict):
    if length < 7:
        day_range_change, day_list = check_day_range(new_start_date_obj, new_end_date_obj, [*old_days_dict.keys()])
        log_output = str()
        question_str = "Is this correct?\n(Y)es to make changes\n(N)o to cancel changes\n:"
        for day in day_list:
            log_output += weekdays[int(day)] + ", "
        log_out_msg = log_output[:-2] + " will be removed.\n"
        if length == 1:
            while 1:
                day_of_week = new_start_date_obj.weekday()
                day_of_week_str = str(day_of_week)
                selector = input(f"\nDetected that your new day range is one day, day will be auto-set to {weekdays[day_of_week]}{'.' if len(log_output) == 0 else ' and ' + log_out_msg}{question_str}").upper()
                if selector == "N":
                    return old_days_dict
                elif selector == "Y":
                    if day_of_week_str in old_days_dict.keys():
                        for i in day_list:
                            old_days_dict.pop(i)
                    else:
                        for i in day_list:
                            old_days_dict.pop(i)
                        old_days_dict[day_of_week_str] = get_hour(int(day_of_week))
                    log_tools.tprint(f"Removed {log_output[:-2]}. (Not Saved:DB Mode)")
                    return old_days_dict
                else:
                    print("Invalid input.")
        else:
            while 1:
                selector = input(f"\nDetected that your new day range is less than the old day range.\n{log_out_msg}{question_str}").upper()
                if selector == "N":
                    return old_days_dict
                elif selector == "Y":
                    for i in day_list:
                        old_days_dict.pop(i)
                    log_tools.tprint(f"Removed {log_output[:-2]}. (Not Saved:DB Mode)")
                    return old_days_dict
                else:
                    print("Invalid input.")
    else:
        return old_days_dict

def change_date_json(subject: int, date2change: int, date_word_str: str, length: int, new_start_date_obj, new_end_date_obj, new_date: str) -> None:
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
    print("\n--Edit {a} Tally of {b}--\nCurrent Tally: {c}h {d}m\nChanges are done by subtracting, not by saving the literal input.".format(a="Normal" if time_category == 4 else "Extra", b=data['subjects'][subject_choice][0], c=str(data['subjects'][subject_choice][time_category][0]), d=str(data['subjects'][subject_choice][time_category][1])))
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

def edit_time_tally_db(subject_name: str, time_category: str, old_hour: int, old_minute: int) -> tuple:
    selector = None
    while old_minute > 59:
        old_hour += 1
        old_minute -= 60
    print(f"\n--Edit {time_category} Tally of {subject_name}--\nCurrent Tally: {old_hour}h {old_minute}m\nChanges are done by subtracting, not by saving the literal input.")
    while selector != 'X':
        selector = input("--Field to edit:\n1. Hour\n2. Minute\ne(X)it without saving\n:").upper()
        if selector == '1':
            while 1:
                selector = input("Decrease hour by:").upper()
                if selector == 'X':
                    return None
                elif selector.isdigit():
                    n = int(selector)
                    if old_hour < n:
                        print(f"Amount to subtract cannot be larger than current hours ({old_hour}h)")
                    else:
                        return n, None
                else:
                    print("Input must be a number")
        elif selector == '2':
            while 1:
                selector = input("Decrease minutes by (can subtract greater than 59minutes):").upper()
                if selector == 'X':
                    return None
                elif selector.isdigit():
                    n = int(selector)
                    if n > old_hour * 60 + old_minute:
                        print(f"Amount to subtract cannot be larger then current hours + minutes ({old_hour}h {old_minute}m)")
                    else:
                        return None, n
                else:
                    print("Input must be a number")
        elif selector != "X":
            print("Invalid input.")

def get_subjects_date(date_type: str, subj_id: int, db_path: str) -> str:
    with closing(sqlite3.connect(db_path)) as db_con:
        with closing(db_con.cursor()) as cur:
            result = cur.execute(f"SELECT {date_type} FROM Subject WHERE ID = (?)", (subj_id,)).fetchone()
    return result[0]

def get_name_frm_subjects_list(a_id: int, subject_list: list) -> str:
    for i in subject_list:
        if i[0] == a_id:
            return i[1]

def correct_time_format_for_neg_minute(a_list: list, minute_num: int) -> None:
    while a_list[1] < minute_num:
        a_list[1] += 60
        a_list[0] -= 1

def correct_time_format_for_pos_minute(a_list: list) -> None:
    while a_list[1] > 59:
        a_list[1] -= 60
        a_list[0] += 1

def correct_time_format_display(time_list: list) -> None:
    if time_list[1] < 0:
        correct_time_format_for_neg_minute(time_list, 0)
    else:
        correct_time_format_for_pos_minute(time_list)

def check_time_tally_change(new_time_change_tuple: tuple, changed_time: dict, display_time_result: list, db_id: int, unsaved_changes: bool) -> None:
    if new_time_change_tuple[0]:
        if unsaved_changes:
            changed_time[db_id][0] -= new_time_change_tuple[0]
        else:
            changed_time[db_id] = [display_time_result[0] - new_time_change_tuple[0], display_time_result[1]]
    else:
        if unsaved_changes:
            changed_time[db_id][1] -= new_time_change_tuple[1]
        else:
            changed_time[db_id] = [display_time_result[0], display_time_result[1] - new_time_change_tuple[1]]
        correct_time_format_for_neg_minute(changed_time[db_id], 0)

def time_data_filter(t) -> int:
    return 0 if not t else t

def db_trans_change_display_setting(cur, db_id: int, name: str, new_setting: bool) -> None:
    cur.execute('UPDATE Subject SET enabled = (?) WHERE ID = (?)', (1 if new_setting else 0, db_id))
    log_tools.tprint(f'Saved to DB: {"Enabled" if new_setting else "Disabled"} Display for Subject Name {name} ID={db_id}')

def db_trans_change_subject_days(cur, db_id: int, name: str, new_days: dict) -> None:
    days_dict = {i[0]: i[1] for i in cur.execute(f"SELECT dayCode, hours FROM SubjectDay WHERE subjectID = (?)", (db_id,)).fetchall()}
    for k, v in new_days.items():
        if k in days_dict.keys():
            if v != days_dict[k]:
                cur.execute('UPDATE SubjectDay SET hours = (?) WHERE subjectID = (?) AND dayCode = (?)', (v, db_id, k))
                log_tools.tprint(f'Saved to DB: SubjectDay for Subject Name {name} ID={db_id} - changed {weekdays[int(k)]} hour from {days_dict[k]} to {v}')
        else:
            cur.execute('INSERT INTO SubjectDay (subjectID, dayCode, hours) VALUES (?, ?, ?)', (db_id, k, v))
            log_tools.tprint(f'Saved to DB: SubjectDay for Subject Name {name} ID={db_id} - added {weekdays[int(k)]} hour - {v}')
    for k in days_dict.keys():
        if k not in new_days.keys():
            cur.execute('DELETE FROM SubjectDay WHERE subjectID = (?) AND dayCode = (?)', (db_id, k))
            log_tools.tprint(f'Saved to DB: SubjectDay for Subject Name {name} ID={db_id} - removed {weekdays[int(k)]} hours {days_dict[k]}')

def db_trans_remove_frm_time_tally(cur, timestamp: str, db_id: int, name: str, old_time_list: list, new_time_list: list, time_type: str) -> None:
    time_adjustment = [0, (new_time_list[0] * 60 + new_time_list[1]) - (old_time_list[0] * 60 + old_time_list[1])]
    correct_time_format_for_neg_minute(time_adjustment, -59)
    cur.execute("INSERT INTO WorkLog (subjectID, logTimestamp, timeType, hour, minute, entryType) VALUES (?, ?, ?, ?, ?, 3)", (db_id, timestamp, time_type, time_adjustment[0], time_adjustment[1]))
    log_tools.tprint(f'Saved to DB: WorkLog Edit ({"During Course Range" if time_type == 0 else "Outside Course Range"} Hours): Subject Name {name} ID={db_id} - {time_adjustment[0]}h {time_adjustment[1]}m')

def db_trans_change_date_range_date(cur, db_id: int, name: str, new_date: str, date_type: str) -> None:
    result = cur.execute(f'SELECT {date_type} FROM Subject WHERE ID = (?)', (db_id,)).fetchone()
    if result[0] != new_date:
        cur.execute(f'UPDATE Subject SET {date_type} = (?) WHERE ID = (?)', (new_date, db_id))
        log_tools.tprint(f"Saved to DB: Subject Name {name} ID={db_id}, changed {date_type} from {result[0]} to {new_date}")

def db_trans_change_subject_name(cur, db_id: int, old_name: str, new_name: str) -> None:
    cur.execute("UPDATE Subject SET subjectName = (?) WHERE ID = (?)", (new_name, db_id))
    log_tools.tprint(f"Saved to DB: Subject Name {old_name} ID={db_id} changed to {new_name}")

def edit_menu_db() -> None:
    with closing(sqlite3.connect(database_path)) as db_con:
        with closing(db_con.cursor()) as cur:
            subjects = cur.execute("SELECT ID, subjectName FROM Subject").fetchall()
    length = len(subjects)
    if length > 0:
        unsaved_changes = False
        changed_names = dict()
        changed_start_date = dict()
        changed_end_date = dict()
        changed_normal_time = dict()
        changed_display_enable = dict()
        changed_extra_time = dict()
        changed_days = dict()
        while 1:
            n = 0
            print(f"\n--EDIT SUBJECT MENU : Unsaved Changes: {unsaved_changes}--\nExit and (S)ave Changes\ne(X)it without saving")
            indexes_of_changed_names = [*changed_names.keys()]
            for subj in subjects:
                n += 1
                if subj[0] in indexes_of_changed_names:
                    print(f'\t{n} - {changed_names[subj[0]]}')
                else:
                    print(f"\t{n} - {subj[1]}")
            selector = input("Subject to edit:").upper()
            if selector == 'X':
                break
            elif selector == 'S':
                if unsaved_changes:
                    update_entryType_list = list()
                    log_tools.tprint("Saving changes to Database.")
                    with closing(sqlite3.connect(database_path)) as db_con:
                        with closing(db_con.cursor()) as cur:
                            if changed_names:
                                for db_id, var in changed_names.items():
                                    db_trans_change_subject_name(cur, db_id, get_name_frm_subjects_list(db_id, subjects), var)
                                changed_names.clear()
                                subjects = cur.execute("SELECT ID, subjectName FROM Subject").fetchall()
                            if changed_start_date:
                                for db_id, var in changed_start_date.items():
                                    db_trans_change_date_range_date(cur, db_id, get_name_frm_subjects_list(db_id, subjects), var, "startDate")
                                    update_entryType_list.append(db_id)
                                changed_start_date.clear()
                            if changed_end_date:
                                for db_id, var in changed_end_date.items():
                                    db_trans_change_date_range_date(cur, db_id, get_name_frm_subjects_list(db_id, subjects), var, "endDate")
                                    if db_id not in update_entryType_list:
                                        update_entryType_list.append(db_id)
                                changed_end_date.clear()
                            if changed_normal_time:
                                # now_time = datetime.now()
                                now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                one_day_course = True  # repurposed to indicate if now_time has been generated
                                for db_id, var in changed_normal_time.items():
                                    db_trans_remove_frm_time_tally(cur, now_time_str, db_id, get_name_frm_subjects_list(db_id, subjects), [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 0", (db_id,)).fetchone()], var, 0)
                                changed_normal_time.clear()
                            if changed_extra_time:
                                if not one_day_course:
                                    # now_time = datetime.now()
                                    now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                for db_id, var in changed_extra_time.items():
                                    db_trans_remove_frm_time_tally(cur, now_time_str, db_id, get_name_frm_subjects_list(db_id, subjects), [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 1", (db_id,)).fetchone()], var, 1)
                                changed_extra_time.clear()
                            if changed_days:
                                for db_id, var in changed_days.items():
                                    db_trans_change_subject_days(cur, db_id, get_name_frm_subjects_list(db_id, subjects), var)
                                changed_days.clear()
                            if changed_display_enable:
                                for db_id, var in changed_display_enable.items():
                                    db_trans_change_display_setting(cur, db_id, get_name_frm_subjects_list(db_id, subjects), var)
                                changed_display_enable.clear()
                            for db_id in update_entryType_list:
                                results = cur.execute("SELECT startDate, endDate FROM Subject WHERE ID = (?)", (db_id,)).fetchone()
                                cur.execute("UPDATE WorkLog SET timeType = IIF(logTimestamp >= (?) AND logTimestamp <= (?), 0, 1) WHERE subjectID = (?)", (results[0] + ' 00:00:00', results[1] + ' 23:59:59', db_id))
                            db_con.commit()
                    unsaved_changes = False
                else:
                    print("No changed saved because non where found.")
            elif validate_selector(selector, length + 1, 1):
                selector_int = int(selector) - 1
                with closing(sqlite3.connect(database_path)) as db_con:
                    with closing(db_con.cursor()) as cur:
                        if subjects[selector_int][0] in changed_start_date.keys():
                            start_date = changed_start_date[subjects[selector_int][0]]
                        else:
                            start_date = cur.execute("SELECT startDate FROM Subject WHERE ID = (?)", (subjects[selector_int][0],)).fetchone()[0]
                        if subjects[selector_int][0] in changed_end_date.keys():
                            end_date = changed_end_date[subjects[selector_int][0]]
                        else:
                            end_date = cur.execute("SELECT endDate FROM Subject WHERE ID = (?)", (subjects[selector_int][0],)).fetchone()[0]
                        if subjects[selector_int][0] in changed_normal_time.keys():
                            normal_time_result = changed_normal_time[subjects[selector_int][0]]
                        else:
                            normal_time_result = [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 0", (subjects[selector_int][0],)).fetchone()]
                        if subjects[selector_int][0] in changed_extra_time.keys():
                            extra_time_result = changed_extra_time[subjects[selector_int][0]]
                        else:
                            extra_time_result = [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 1", (subjects[selector_int][0],)).fetchone()]
                        if subjects[selector_int][0] in changed_days.keys():
                            days_dict = changed_days[subjects[selector_int][0]]
                        else:
                            days_dict = {i[0]: i[1] for i in cur.execute(f"SELECT dayCode, hours FROM SubjectDay WHERE subjectID = (?)", (subjects[selector_int][0],)).fetchall()}
                        if subjects[selector_int][0] in changed_display_enable:
                            display_enabled = changed_display_enable[subjects[selector_int][0]]
                        else:
                            display_enabled = True if cur.execute('SELECT enabled FROM Subject WHERE ID = (?)', (subjects[selector_int][0],)).fetchone()[0] == 1 else False
                correct_time_format_display(normal_time_result)
                correct_time_format_display(extra_time_result)
                while 1:
                    if start_date == end_date:
                        one_day_course = True
                        n = 6
                    else:
                        one_day_course = False
                        n = 8
                    day_line = '\n4. Add Day\n5. Remove Day' if one_day_course is False else ''
                    print(f"\n--Edit Subject {changed_names[subjects[selector_int][0]] if subjects[selector_int][0] in indexes_of_changed_names else subjects[selector_int][1]}--\ne(X)it to previous menu\n(S)ave changes\n1. Name\n2. Start Date\t\t{datetime.strptime(start_date, '%Y-%m-%d').date().strftime('%d/%m/%Y')}\n3. End Date\t\t{datetime.strptime(end_date, '%Y-%m-%d').date().strftime('%d/%m/%Y')}{day_line}\n6. Remove from Normal Tally\t{normal_time_result[0]}h {normal_time_result[1]}m\n7. Remove from Extra Tally\t{extra_time_result[0]}h {extra_time_result[1]}m\n8. Display\t{'Enabled' if display_enabled else 'Disabled'}\n::Edit a Day")
                    for d, hour in days_dict.items():
                        n += 1
                        print(f"{n}. {weekdays[int(d)]}\t\t{hour} Hour{'' if hour == 1 else 's'} ")
                    selector = input("Field to edit:").upper()
                    if selector == 'X':
                        break
                    elif selector == 'S':
                        if unsaved_changes:
                            log_tools.tprint(f"Saving changes to {subjects[selector_int][1]} to Database")
                            with closing(sqlite3.connect(database_path)) as db_con:
                                with closing(db_con.cursor()) as cur:
                                    if subjects[selector_int][0] in indexes_of_changed_names:
                                        db_trans_change_subject_name(cur, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), changed_names[subjects[selector_int][0]])
                                        changed_names.pop(subjects[selector_int][0])
                                        indexes_of_changed_names.remove(subjects[selector_int][0])
                                        subjects = cur.execute("SELECT ID, subjectName FROM Subject").fetchall()
                                    if subjects[selector_int][0] in changed_start_date.keys():
                                        db_trans_change_date_range_date(cur, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), changed_start_date[subjects[selector_int][0]], "startDate")
                                        changed_start_date.pop(subjects[selector_int][0])
                                        this_field_unsaved_changes = True  # var repurposed to need to change timeType column
                                    if subjects[selector_int][0] in changed_end_date.keys():
                                        db_trans_change_date_range_date(cur, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), changed_end_date[subjects[selector_int][0]], "endDate")
                                        changed_end_date.pop(subjects[selector_int][0])
                                        this_field_unsaved_changes = True
                                    if subjects[selector_int][0] in changed_normal_time.keys():
                                        # now_time = datetime.now()
                                        now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        one_day_course = True  # repurposed to indicate if now_time has been generated
                                        db_trans_remove_frm_time_tally(cur, now_time_str, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 0", (subjects[selector_int][0],)).fetchone()], changed_normal_time[subjects[selector_int][0]], 0)
                                        changed_normal_time.pop(subjects[selector_int][0])
                                    if subjects[selector_int][0] in changed_extra_time.keys():
                                        if not one_day_course:
                                            # now_time = datetime.now()
                                            now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        db_trans_remove_frm_time_tally(cur, now_time_str, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), [time_data_filter(x) for x in cur.execute(f"SELECT sum(hour), sum(minute) FROM WorkLog WHERE subjectID = (?) AND timeType = 1", (subjects[selector_int][0],)).fetchone()], changed_extra_time[subjects[selector_int][0]], 1)
                                        changed_extra_time.pop(subjects[selector_int][0])
                                    if subjects[selector_int][0] in changed_days.keys():
                                        db_trans_change_subject_days(cur, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), changed_days[subjects[selector_int][0]])
                                        changed_days.pop(subjects[selector_int][0])
                                    if subjects[selector_int][0] in changed_display_enable.keys():
                                        db_trans_change_display_setting(cur, subjects[selector_int][0], get_name_frm_subjects_list(subjects[selector_int][0], subjects), changed_display_enable[subjects[selector_int][0]])
                                        changed_display_enable.pop(subjects[selector_int][0])
                                    if this_field_unsaved_changes:
                                        results = cur.execute("SELECT startDate, endDate FROM Subject WHERE ID = (?)", (subjects[selector_int][0],)).fetchone()
                                        cur.execute("UPDATE WorkLog SET timeType = IIF(logTimestamp >= (?) AND logTimestamp <= (?), 0, 1) WHERE subjectID = (?)", (results[0] + ' 00:00:00', results[1] + ' 23:59:59', subjects[selector_int][0]))
                                    db_con.commit()
                            if not (indexes_of_changed_names or changed_start_date or changed_end_date or changed_normal_time or changed_display_enable or changed_extra_time or changed_days):
                                unsaved_changes = False
                    else:
                        if validate_selector(selector, n + 1):
                            field = int(selector)
                            if (not one_day_course and field > 8) or (one_day_course and field > 6):
                                d = [*days_dict.keys()][field - 7 if one_day_course else field - 9]
                                while 1:
                                    day_name = weekdays[d]
                                    print(f"\n--Edit {subjects[selector_int][1]} {day_name}--\n--X to exit.")
                                    num = input("Number of hours:").upper()
                                    if num.isdecimal():
                                        old = days_dict[d]
                                        new_amount = int(num)
                                        if old != new_amount:
                                            days_dict[d] = new_amount
                                            changed_days[subjects[selector_int][0]] = days_dict
                                            unsaved_changes = True
                                            log_tools.tprint(f"Changed {subjects[selector_int][1]} {day_name} time from {old} to {new_amount}. (Not Saved:DB Mode)")
                                        break
                                    elif num == "X":
                                        break
                                    else:
                                        print("Number must be a decimal number.")
                            else:
                                if field == 1:  # Change Name
                                    if subjects[selector_int][0] in indexes_of_changed_names:
                                        old = changed_names[subjects[selector_int][0]]
                                        print(f"Note: Name unsaved name is {old}, name in DB is {get_name_frm_subjects_list(subjects[selector_int][0], subjects)}")
                                    else:
                                        old = get_name_frm_subjects_list(subjects[selector_int][0], subjects)
                                        print(f'Name in DB is {old}')
                                    name = input(f"\nNew name of Subject:")
                                    if len(name) > 0:
                                        this_field_unsaved_changes = True  # repurposed to indicate a duplicate name found, True = none found
                                        for subj in subjects:
                                            if subj[0] in indexes_of_changed_names and changed_names[subj[0]] == name or subj[1] == name:
                                                this_field_unsaved_changes = False
                                                print(f'Duplicate name "{name}" found, pick another name.')
                                                break
                                        if this_field_unsaved_changes:
                                            changed_names[subjects[selector_int][0]] = name
                                            indexes_of_changed_names.append(subjects[selector_int][0])
                                            unsaved_changes = True
                                            log_tools.tprint(f"Renamed {old} to {changed_names[subjects[selector_int][0]]}. (Not Saved:DB Mode)")
                                    else:
                                        print("Name must be at least 1 character.")
                                if field == 2:  # Change start date
                                    while 1:
                                        v_old = get_subjects_date('startDate', subjects[selector_int][0], database_path)
                                        if subjects[selector_int][0] in changed_start_date.keys():
                                            old = changed_start_date[subjects[selector_int][0]]
                                            this_field_unsaved_changes = True
                                            print(f"\nStart Date, format - dd/mm/yyyy. Unsaved date: {datetime.strptime(old, '%Y-%m-%d').date().strftime('%d/%m/%Y')}, Date in DB: {datetime.strptime(v_old, '%Y-%m-%d').date().strftime('%d/%m/%Y')}")
                                        else:
                                            this_field_unsaved_changes = False
                                            print(f"\nStart Date, format - dd/mm/yyyy. Date in DB: {datetime.strptime(v_old, '%Y-%m-%d').date().strftime('%d/%m/%Y')}")
                                        new_date = get_date()
                                        new_date_obj = datetime.strptime(new_date, '%d/%m/%Y').date()
                                        if subjects[selector_int][0] in changed_end_date:
                                            end_date_obj = datetime.strptime(changed_end_date[subjects[selector_int][0]], '%Y-%m-%d').date()
                                        else:
                                            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                                        if end_date_obj < new_date_obj:
                                            print(f"Start date must be before or the same as the end date ({end_date_obj.strftime('%d/%m/%Y')}).")
                                        else:
                                            break
                                    old_date_obj = datetime.strptime(old if this_field_unsaved_changes else v_old, '%Y-%m-%d').date()
                                    if old_date_obj != new_date_obj:
                                        new_days_dict = check_date_new_days_dict((end_date_obj - new_date_obj).days + 1, new_date_obj, end_date_obj, days_dict)
                                        if subjects[selector_int][0] in changed_days.keys():
                                            if new_days_dict != changed_days[subjects[selector_int][0]]:
                                                changed_days[subjects[selector_int][0]] = new_days_dict
                                        else:
                                            if days_dict != new_days_dict:
                                                changed_days[subjects[selector_int][0]] = new_days_dict
                                        new_date = new_date_obj.strftime('%Y-%m-%d')
                                        changed_start_date[subjects[selector_int][0]] = new_date
                                        start_date = new_date
                                        unsaved_changes = True
                                        log_tools.tprint(f"Changed Start Date from {old_date_obj.strftime('%d/%m/%Y')} to {new_date_obj.strftime('%d/%m/%Y')}. (Not Saved:DB Mode)")
                                    else:
                                        print(f'No change made to Start Date: New Date is same as Old Date {new_date}')
                                elif field == 3:  # Change end date
                                    while 1:
                                        v_old = get_subjects_date('endDate', subjects[selector_int][0], database_path)
                                        if subjects[selector_int][0] in changed_end_date.keys():
                                            old = changed_end_date[subjects[selector_int][0]]
                                            this_field_unsaved_changes = True
                                            print(f"\nEnd Date, format - dd/mm/yyyy. Unsaved date: {datetime.strptime(old, '%Y-%m-%d').date().strftime('%d/%m/%Y')}, Date in DB: {datetime.strptime(v_old, '%Y-%m-%d').date().strftime('%d/%m/%Y')}")
                                        else:
                                            this_field_unsaved_changes = False
                                            print(f"\nEnd Date, format - dd/mm/yyyy. Date in DB: {datetime.strptime(v_old, '%Y-%m-%d').date().strftime('%d/%m/%Y')}")
                                        new_date = get_date()
                                        new_date_obj = datetime.strptime(new_date, '%d/%m/%Y').date()
                                        if subjects[selector_int][0] in changed_start_date:
                                            start_date_obj = datetime.strptime(changed_start_date[subjects[selector_int][0]], '%Y-%m-%d').date()
                                        else:
                                            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                                        if start_date_obj > new_date_obj:
                                            print(f"End date must be after or the same as the start date ({new_date}).")
                                        else:
                                            break
                                    old_date_obj = datetime.strptime(old if this_field_unsaved_changes else v_old, '%Y-%m-%d').date()
                                    if old_date_obj != new_date_obj:
                                        new_days_dict = check_date_new_days_dict((new_date_obj - start_date_obj).days + 1, start_date_obj, new_date_obj, days_dict)
                                        if subjects[selector_int][0] in changed_days.keys():
                                            if new_days_dict != changed_days[subjects[selector_int][0]]:
                                                changed_days[subjects[selector_int][0]] = new_days_dict
                                        else:
                                            if days_dict != new_days_dict:
                                                changed_days[subjects[selector_int][0]] = new_days_dict
                                        new_date = new_date_obj.strftime('%Y-%m-%d')
                                        changed_end_date[subjects[selector_int][0]] = new_date
                                        end_date = new_date
                                        unsaved_changes = True
                                        log_tools.tprint(f"Changed End Date from {old_date_obj.strftime('%d/%m/%Y')} to {new_date_obj.strftime('%d/%m/%Y')}. (Not Saved:DB Mode)")
                                    else:
                                        print(f'No change made to End Date: New Date is same as Old Date {new_date}')
                                elif field == 4:  # Add days
                                    s_day_options, length = setup_day_options(changed_start_date[subjects[selector_int][0]] if subjects[selector_int][0] in changed_start_date.keys() else start_date, changed_end_date[subjects[selector_int][0]] if subjects[selector_int][0] in changed_end_date.keys() else end_date)
                                    if subjects[selector_int][0] in changed_days.keys():
                                        this_field_unsaved_changes = True
                                        for d in changed_days[subjects[selector_int][0]].keys():
                                            n = s_day_options.rfind(day_options[int(d)])
                                            s_day_options = s_day_options[:n] + s_day_options[n + 1:]
                                    else:
                                        this_field_unsaved_changes = False
                                        for d in days_dict.keys():
                                            n = s_day_options.rfind(day_options[int(d)])
                                            s_day_options = s_day_options[:n] + s_day_options[n + 1:]
                                    changed_days[subjects[selector_int][0]], day_list = create_days_dict(s_day_options, length, True, changed_days[subjects[selector_int][0]] if this_field_unsaved_changes else days_dict)
                                    log_output = str()
                                    for d in day_list:
                                        n = int(d)
                                        log_output += f'{weekdays[n]} {changed_days[subjects[selector_int][0]][n]} hour{"" if changed_days[subjects[selector_int][0]][n] == 1 else "s"}, '
                                    unsaved_changes = True
                                    log_tools.tprint(f"Added to {subjects[selector_int][1]} - {log_output[:-2]}. (Not Saved:DB Mode)")
                                elif field == 5:  # Remove a day
                                    print(f"\n--Remove a day from {subjects[selector_int][1]}--")
                                    if subjects[selector_int][0] in changed_days:
                                        this_field_unsaved_changes = True
                                        days = [*changed_days[subjects[selector_int][0]].keys()]
                                    else:
                                        this_field_unsaved_changes = False
                                        days = [*days_dict.keys()]
                                    while 1:
                                        n = 0
                                        for d, hour in (changed_days[subjects[selector_int][0]] if this_field_unsaved_changes else days_dict).items():
                                            n += 1
                                            print(f"{n}. {weekdays[d]}\t Hour{'' if hour == 1 else 's'}: {hour}")
                                        selector = input("Field to edit:").upper()
                                        if selector == 'X':
                                            break
                                        elif validate_selector(selector, n + 1):
                                            n = int(selector) - 1
                                            if not this_field_unsaved_changes:
                                                changed_days[subjects[selector_int][0]] = days_dict
                                            changed_days[subjects[selector_int][0]].pop(days[n])
                                            unsaved_changes = True
                                            log_tools.tprint(f"Removed {weekdays[int(days[n])]} from {subjects[selector_int][1]}. (Not Saved:DB Mode)")
                                            break
                                elif field == 6:  # Edit Normal Tally
                                    this_field_unsaved_changes = True if subjects[selector_int][0] in changed_normal_time.keys() else False
                                    new_time_list = [time_data_filter(x) for x in edit_time_tally_db(subjects[selector_int][1], "Normal", normal_time_result[0], normal_time_result[1])]
                                    if new_time_list:
                                        check_time_tally_change(new_time_list, changed_normal_time, normal_time_result, subjects[selector_int][0], this_field_unsaved_changes)
                                        if normal_time_result != changed_normal_time[subjects[selector_int][0]]:
                                            unsaved_changes = True
                                            normal_time_result = changed_normal_time[subjects[selector_int][0]].copy()
                                            log_tools.tprint(f"Decreased Subject {subjects[selector_int][1]} Normal time by {new_time_list[0]}h {new_time_list[1]}m. (Not Saved:DB Mode)")
                                elif field == 7:  # Edit Extra Tally
                                    this_field_unsaved_changes = True if subjects[selector_int][0] in changed_extra_time.keys() else False
                                    new_time_list = [time_data_filter(x) for x in edit_time_tally_db(subjects[selector_int][1], "Extra", extra_time_result[0], extra_time_result[1])]
                                    if new_time_list:
                                        check_time_tally_change(new_time_list, changed_extra_time, extra_time_result, subjects[selector_int][0], this_field_unsaved_changes)
                                        if extra_time_result != changed_extra_time[subjects[selector_int][0]]:
                                            unsaved_changes = True
                                            extra_time_result = changed_extra_time[subjects[selector_int][0]].copy()
                                            log_tools.tprint(f"Decreased Subject {subjects[selector_int][1]} Extra time by {new_time_list[0]}h {new_time_list[1]}m. (Not Saved:DB Mode)")
                                elif field == 8:  # Enable/Disable Display
                                    selector = input(f'\nT to {"Disable" if display_enabled else "Enable"}:').upper()
                                    if selector == 'T':
                                        if subjects[selector_int][0] in changed_display_enable.keys():
                                            changed_display_enable[subjects[selector_int][0]] = not changed_display_enable[subjects[selector_int][0]]
                                        else:
                                            changed_display_enable[subjects[selector_int][0]] = not display_enabled
                                        unsaved_changes = True
                                        display_enabled = changed_display_enable[subjects[selector_int][0]]
                                        log_tools.tprint(f'{"Enabled" if display_enabled else "Disabled"} Subject {subjects[selector_int][1]}. (Not Saved:DB Mode)')
    else:
        print("No subjects found in DB")

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
                    for d, hour in data['subjects'][subject_choice][1].items():
                        n += 1
                        print(f"{n}. {weekdays[int(d)]}\t\t{hour} Hour{'' if hour == 1 else 's'} ")
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
                                d = [*data['subjects'][subject_choice][1].keys()][field - 6 if one_day_course else field - 8]
                                while 1:
                                    day_name = weekdays[int(d)]
                                    print(f"\n--Edit {data['subjects'][subject_choice][0]} {day_name}--\n--X to exit.")
                                    num = input("Number of hours:").upper()
                                    if num.isdecimal():
                                        old = data['subjects'][subject_choice][1][d]
                                        data['subjects'][subject_choice][1][d] = int(num)
                                        log_tools.tprint("Changed {} {} time from {} to {}. (Not Saved)".format(data['subjects'][subject_choice][0], day_name, str(old), str(data['subjects'][subject_choice][1][d])))
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
                                    while 1:
                                        print("\nStart Date, format - dd/mm/yyyy. Current Date ({})".format(data['subjects'][subject_choice][2]))
                                        new_date = get_date()
                                        new_date_obj = datetime.strptime(new_date, '%d/%m/%Y').date()
                                        end_date_obj = datetime.strptime(data['subjects'][subject_choice][3], '%d/%m/%Y').date()
                                        if end_date_obj < new_date_obj:
                                            print("Start date must be before the end date ({}).".format(data['subjects'][subject_choice][3]))
                                        else:
                                            break
                                    change_date_json(subject_choice, 2, "start", (end_date_obj - new_date_obj).days + 1, new_date_obj, end_date_obj, new_date)
                                elif field == 3:  # Change end date
                                    new_date = validate_end_date(data['subjects'][subject_choice][2])
                                    start_date_obj = datetime.strptime(data['subjects'][subject_choice][2], '%d/%m/%Y').date()
                                    new_date_obj = datetime.strptime(new_date, '%d/%m/%Y').date()
                                    change_date_json(subject_choice, 3, "end", (new_date_obj - start_date_obj).days + 1, start_date_obj, new_date_obj, new_date)
                                elif field == 4:  # Add days
                                    s_day_options, length = setup_day_options(data['subjects'][subject_choice][2], data['subjects'][subject_choice][3])
                                    for d in data['subjects'][subject_choice][1].keys():
                                        n = s_day_options.rfind(day_options[int(d)])
                                        s_day_options = s_day_options[:n] + s_day_options[n + 1:]
                                    print(s_day_options)
                                    data['subjects'][subject_choice][1], day_list = create_days_dict(s_day_options, length, True, data['subjects'][subject_choice][1])
                                    log_output = str()
                                    for d in day_list:
                                        log_output += "{} {} hour{s}, ".format(weekdays[int(d)], str(data['subjects'][subject_choice][1][d]), s="" if data['subjects'][subject_choice][1][d] == 1 else "s")
                                    log_tools.tprint("Added to {} - {}. (Not Saved)".format(data['subjects'][subject_choice][0], log_output[:-2]))
                                elif field == 5:  # Remove a day
                                    print("\n--Remove a day from {}--".format(data['subjects'][subject_choice][0]))
                                    days = [*data['subjects'][subject_choice][1].keys()]
                                    while 1:
                                        n = 0
                                        for d, hour in data['subjects'][subject_choice][1].items():
                                            n += 1
                                            print("{}. {}\t Hour{a}: {b}".format(str(n), weekdays[int(d)], a="" if hour == 1 else "s", b=str(hour)))
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

# def add_to_daily_tally(hour, minute):
#     pass

def add_hour_minute(subject: int, time_category: int, hour: int, minute: int) -> None:
    old_hour = data['subjects'][subject][time_category][0]
    old_minute = data['subjects'][subject][time_category][1]
    data['subjects'][subject][time_category][0] += hour
    data['subjects'][subject][time_category][1] += minute
    correct_time_format_for_pos_minute(data['subjects'][subject][time_category])
    ## add daily tally here
    log_tools.tprint("Increased {}{a} Hours from {b}h {c}m to {d}h {e}m.".format(data['subjects'][subject][0], a=" During Course Range" if time_category == 4 else " Outside Course Range", b=str(old_hour), c=str(old_minute), d=str(data['subjects'][subject][time_category][0]), e=str(data['subjects'][subject][time_category][1])))

def time_convert_str(sec: float) -> str:
    mins = sec // 60
    return f"{int(mins // 60):02d}:{int(mins % 60):02d}:{int(sec % 60):02d}"

'''Found this getwch() method in getpass.py @ https://github.com/python/cpython/blob/3.8/Lib/getpass.py'''
def thread_timer_cancel() -> None:
    global timer_running
    while 1:
        c = getwch()
        if c == '\r' or c == '\n':
            timer_running = False
            print('\n')
            break
        if c == '\003':
            raise KeyboardInterrupt

def timer_control(subject_name: str, use_live_update_timer: bool):
    global timer_running
    if use_live_update_timer:
        x = threading.Thread(target=thread_timer_cancel)
    print("\nAdding to Tally of " + subject_name)
    print('NOTE: Time spans lower than 1 minute will not be saved.')
    while 1:
        c = input('\nPress Enter to start or X to Exit:').upper()
        if c == 'X':
            return 0, 0
        elif c == '':
            start_time = time.time()
            log_tools.tprint(f"Timer for {subject_name} started")
            if use_live_update_timer:
                x.start()
                print('Press Enter to stop timer')
                while timer_running:
                    current_time = time.time()
                    sys.stdout.write('\rTime Lapsed = ' + time_convert_str(current_time - start_time))
                    sys.stdout.flush()
                    time.sleep(0.5)
            else:
                while timer_running:
                    c = input('Press Enter to stop timer')
                    if c == '':
                        timer_running = False
                    else:
                        print('Invalid command.')
            current_time = time.time()
            current_time = current_time - start_time  # current_time repurposed to length of time span
            current_time = int(current_time // 60)  # current_time repurposed to minutes
            hours = current_time // 60
            current_time = current_time % 60
            print('Timer stopped at {}\n'.format('{0} minute{s}'.format(current_time, s='' if current_time == 1 else 's') if hours == 0 else '{0} hour{s} {m}'.format(hours, s=' ' if hours == 1 else 's ', m='{0} minute{s}'.format(current_time, s='' if current_time == 1 else 's'))))
            return hours, current_time

def db_trans_commit_WorkLog(new_tally: list, subject_id: int, entry_type: int) -> None:
    now_time = datetime.now()
    correct_time_format_for_pos_minute(new_tally)
    with closing(sqlite3.connect(database_path)) as db_con:
        with closing(db_con.cursor()) as cur:
            result = cur.execute(f"SELECT endDate FROM Subject WHERE ID = (?)", (subject_id,)).fetchone()
            cur.execute("INSERT INTO WorkLog (subjectID, logTimestamp, timeType, hour, minute, entryType) VALUES (?, ?, ?, ?, ?, ?)", (subject_id, now_time.strftime('%Y-%m-%d %H:%M:%S'), 1 if now_time > datetime.strptime(result[0], '%Y-%m-%d') else 0, *new_tally, entry_type))
            db_con.commit()

def timer_tally() -> bool:
    global timer_running, last_past_hours_update
    if settings['useDB']:
        subjects = get_enabled_subjects(database_path)
        length = len(subjects)
        if length > 0:
            while 1:
                n = 0
                print("\n\t--TIMER MENU--")
                for subj in subjects:
                    n += 1
                    print(f"\t{n} - {subj[1]}")
                selector = input("Subject to add tally to:").upper()
                if selector == 'X':
                    break
                elif validate_selector(selector, length + 1, 1):
                    selector = int(selector) - 1
                    new_tally = list(timer_control(subjects[selector][1], use_live_update_timer))
                    timer_running = True
                    if new_tally[1] != 0 or new_tally[0] != 0:
                        db_trans_commit_WorkLog(new_tally, subjects[selector][0], 2)
                        log_tools.tprint(f"DB Add: WorkLog - Timer Tally - subjectID: {subjects[selector][0]} - subjectName:{subjects[selector][1]} - {new_tally[0]}h {new_tally[1]}m")
                        if settings['useRecentHoursDisplay']:
                            check_fix_daily_progress()
                            past_hours['day1Tally'][0] += new_tally[0]
                            past_hours['day1Tally'][1] += new_tally[1]
                            correct_time_format_for_pos_minute(past_hours['day1Tally'])
        else:
            print("No subjects found in Database")
    else:
        if "subjects" in data and len(data['subjects']) > 0:
            while 1:
                print("\n\t--TIMER MENU--")
                n = display_subject_list()
                selector = input("Subject to add tally to:").upper()
                if selector == "X":
                    break
                elif validate_selector(selector, n):
                    selector = int(selector)
                    time_category = 5 if datetime.strptime(log_tools.run_date, '%d-%m-%Y').date() > datetime.strptime(data['subjects'][selector][3], '%d/%m/%Y').date() else 4
                    hour, minute = timer_control(data['subjects'][selector][0], use_live_update_timer)
                    timer_running = True
                    if minute != 0 or hour != 0:
                        add_hour_minute(selector, time_category, hour, minute)
                        save_json(data, data_path + 'study_tally_data.json', "Data")
                    else:
                        log_tools.tprint(f'Time span for {data["subjects"][selector][0]} was less than 1 minute, nothing saved.')
        else:
            print("Subject list in empty.")

def get_tally_digits():
    return get_time_digit('hour') if settings['tallyEditHour'] else 0, get_time_digit('minute') if settings['tallyEditMinute'] else 0

def add_to_tally() -> bool:
    global last_past_hours_update
    if settings['useDB']:
        subjects = get_enabled_subjects(database_path)
        length = len(subjects)
        if length > 0:
            while 1:
                n = 0
                print("\n\t--TALLY MENU--")
                for subj in subjects:
                    n += 1
                    print(f"\t{n} - {subj[1]}")
                selector = input("Subject to add tally to:").upper()
                if selector == 'X':
                    break
                elif validate_selector(selector, length + 1, 1):
                    selector = int(selector) - 1
                    print("Adding to Tally of " + subjects[selector][1])
                    new_tally = list(get_tally_digits())
                    if new_tally[1] != 0 or new_tally[0] != 0:
                        # get time from begining of day
                        # if new tally + day1Tally > minutes of this day split time log
                        # add to yesterdays time, correct yesterday
                        db_trans_commit_WorkLog(new_tally, subjects[selector][0], 1)
                        log_tools.tprint(f"DB Add: WorkLog Manual Tally - subjectID: {subjects[selector][0]} - subjectName:{subjects[selector][1]} - {new_tally[0]}h {new_tally[1]}m")
                        if settings['useRecentHoursDisplay']:
                            check_fix_daily_progress()
                            past_hours['day1Tally'][0] += new_tally[0]
                            past_hours['day1Tally'][1] += new_tally[1]
                            correct_time_format_for_pos_minute(past_hours['day1Tally'])
                        break
                    else:
                        print("No time recorded because no data entered")
        else:
            print("No subjects found in Database")
    else:
        if "subjects" in data and len(data['subjects']) > 0:
            while 1:
                print("\n\t--TALLY MENU--")
                n = display_subject_list()
                selector = input("Subject to add tally to:").upper()
                if selector == "X":
                    break
                elif validate_selector(selector, n):
                    selector = int(selector)
                    time_category = 5 if datetime.strptime(log_tools.run_date, '%d-%m-%Y').date() > datetime.strptime(data['subjects'][selector][3], '%d/%m/%Y').date() else 4
                    print("Adding to Tally of " + data['subjects'][selector][0])
                    add_hour_minute(selector, time_category, *get_tally_digits())
                    save_json(data, data_path + 'study_tally_data.json', "Data")
                    break
        else:
            print("Subject list in empty.")

def holiday_menu_db() -> None:
    unsaved_change = False
    changed_names = dict()
    changed_start_date = dict()
    changed_end_date = dict()
    removed = list()
    with closing(sqlite3.connect(database_path)) as db_con:
        with closing(db_con.cursor()) as cur:
            holidays_list = cur.execute("SELECT ID, holidayName, startDate, endDate FROM Holiday").fetchall()
            last_id = cur.execute('SELECT MAX(ID) FROM Holiday').fetchone()[0]
    if holidays_list:
        id_to_range = dict()
        num_to_id = dict()
        id_to_name = dict()
        n = 0
        for item in holidays_list:
            id_to_range[item[0]] = [datetime.strptime(item[2], '%Y-%m-%d').date().strftime('%d/%m/%Y'), datetime.strptime(item[3], '%Y-%m-%d').date().strftime('%d/%m/%Y')]
            num_to_id[n] = item[0]
            id_to_name[item[0]] = item[1]
            n += 1
    while 1:
        if n > 0:
            holiday_names = [*changed_names.values()]
            for key, val in id_to_name.items():
                if key not in changed_names.keys():
                    holiday_names.append(val)
            display_holiday_list_db(False, id_to_name, id_to_range, removed, changed_names, changed_start_date, changed_end_date)
            num_options = True
            print("\n\t--HOLIDAY MENU--\n\tExit and (S)ave Changes\n\te(X)it without saving\n\t1. Add Holiday\n\t2. Remove Holiday\n\t3. Edit Holiday")
        else:
            print('\nNo holidays saved.')
            holiday_names = list()
            num_options = False
            print('\n\t--HOLIDAY MENU--\n\tExit and (S)ave Changes\n\te(X)it without saving\n\t1. Add Holiday\n')
        selector = input(("Option:" if num_options else "Field to edit:")).upper()
        if menu_char_check(selector, 'SX' + ('1' if num_options is False else '123')):
            if selector == '1':  # Add
                last_id += 1
                name = get_name('Holiday', holiday_names)
                print("\nStart Date, format - dd/mm/yyyy.")
                start_date = get_date()
                end_date = validate_end_date(start_date)
                changed_names[last_id] = name
                changed_start_date[last_id] = start_date
                changed_end_date[last_id] = end_date
                num_to_id[n] = last_id
                unsaved_change = True
                log_tools.tprint(f'Added {name} to Saved Holidays. (Not Saved).')
                n += 1
            elif selector == '2':  # Remove
                while 1:
                    print('\n\t--REMOVE HOLIDAY MENU--\n\te(X)it\n')
                    n = display_holiday_list_db(True, id_to_name, id_to_range, removed, changed_names, changed_start_date, changed_end_date)
                    field = input('Holiday to remove:').upper()
                    if field == "X":
                        break
                    elif validate_selector(field, n):
                        num = int(field)
                        removed.append(num_to_id[num])
                        unsaved_change = True
                        log_tools.tprint(f"Removed {changed_names[num_to_id[num]] if num_to_id[num] in changed_names.keys() else id_to_name[num_to_id[num]]} from Saved Holidays. (Not Saved)")
                        break
            elif selector == '3':
                while 1:
                    print('\n\t--EDIT HOLIDAY MENU--\n\te(X)it\n')
                    n = display_holiday_list_db(True, id_to_name, id_to_range, removed, changed_names, changed_start_date, changed_end_date)
                    field = input('Holiday to edit:').upper()
                    if field == 'X':
                        break
                    elif validate_selector(field, n):
                        num = int(field)
                        while 1:
                            end_date = changed_end_date[num_to_id[num]] if num_to_id[num] in changed_end_date.keys() else id_to_range[num_to_id[num]][1]
                            start_date = changed_start_date[num_to_id[num]] if num_to_id[num] in changed_start_date else id_to_range[num_to_id[num]][0]
                            name = changed_names[num_to_id[num]] if num_to_id[num] in changed_names.keys() else id_to_name[num_to_id[num]]
                            print(f"\n\t--EDIT HOLIDAY {name}--\n\te(X)it to previous menu\n\t(S)ave changes\n\t1. Name\n\t2. Start Date\t{start_date}\n\t3. End Date\t{end_date}")
                            field = input('Field to edit:').upper()
                            if field == '1':  # Edit Name
                                selector = get_name('holiday', holiday_names)
                                old = id_to_name[num_to_id[num]]
                                changed_names[num_to_id[num]] = selector
                                unsaved_change = True
                                log_tools.tprint(f"Renamed holiday - {old} to {selector}. (Not Saved:DB Mode)")
                                break
                            elif field == '2':  # Edit Start Date
                                changed_start_date[num_to_id[num]] = validate_start_date(end_date, start_date)
                                unsaved_change = True
                                log_tools.tprint(f"Changed holiday Start Date - {name} from {start_date} to {changed_start_date[num_to_id[num]]}. (Not Saved:DB Mode)")
                                break
                            elif field == '3':  # Edit End Date
                                changed_end_date[num_to_id[num]] = validate_end_date(start_date, end_date)
                                unsaved_change = True
                                log_tools.tprint(f"Changed holiday End Date - {name} from {end_date} to {changed_end_date[num_to_id[num]]}. (Not Saved:DB Mode)")
                                break
                            elif field == 'X':
                                break
                            else:
                                print("Invalid input.")
            elif selector == 'X':
                break
            elif selector == 'S':  # Save
                if unsaved_change:
                    if removed:
                        field = ''
                        while field not in ['Y', 'N']:
                            for id in removed:
                                print(f'{changed_names[id] if id in changed_names.keys() else id_to_name[id]}')
                            field = input("WARNING: Found items in remove list, (Y) to confirm that you want these items removed from the Database, (N) to cancel removal:").upper()
                    with closing(sqlite3.connect(database_path)) as db_con:
                        with closing(db_con.cursor()) as cur:
                            if field == 'Y':
                                for id in removed:
                                    if id in id_to_name.keys():
                                        cur.execute("DELETE FROM Holiday WHERE ID = (?)", (id,))
                                        log_tools.tprint(f"Deleted from Database Holiday Name: {id_to_name[id]}, Start Date: {id_to_range[id][0]}, End Date: {id_to_range[id][1]}")
                                        if id in changed_names.keys():
                                            changed_names.pop(id)
                                        if id in changed_start_date.keys():
                                            changed_start_date.pop(id)
                                        if id in changed_end_date.keys():
                                            changed_end_date.pop(id)
                                    else:
                                        name = changed_names.pop(id)
                                        start_date = changed_start_date.pop(id)
                                        end_date = changed_end_date.pop(id)
                                        log_tools.tprint(f"Deleted Unsaved Holiday Name: {name}, Start Date: {start_date}, End Date: {end_date}")
                            removed = list()
                            for id, name in changed_names.items():
                                if id not in id_to_name.keys():
                                    cur.execute("INSERT INTO Holiday (holidayName, startDate, endDate) VALUES (?, ?, ?)", (name, datetime.strptime(changed_start_date[id], '%d/%m/%Y').date().strftime('%Y-%m-%d'), datetime.strptime(changed_end_date[id], '%d/%m/%Y').date().strftime('%Y-%m-%d')))
                                    log_tools.tprint(f"Saved to DB: New Holiday - Name: {name}, Start Date: {changed_start_date[id]}, End Date: {changed_end_date[id]}")
                                    removed.append(id)
                            for id in removed:
                                changed_names.pop(id)
                                changed_start_date.pop(id)
                                changed_end_date.pop(id)
                            if changed_names:
                                for id, val in changed_names.items():
                                    cur.execute("UPDATE Holiday SET holidayName = (?) WHERE ID = (?)", (val, id))
                                    log_tools.tprint(f"Saved to DB: Holiday Name {id_to_name[id]} ID={id} changed to {val}")
                            if changed_start_date:
                                for id, val in changed_start_date.items():
                                    cur.execute("UPDATE Holiday SET startDate = (?) WHERE ID = (?)", (datetime.strptime(val, '%d/%m/%Y').date().strftime('%Y-%m-%d'), id))
                                    log_tools.tprint(f"Saved to DB: Holiday Name {changed_names[id] if id in changed_names.keys() else id_to_name[id]} changed Start Date from {id_to_range[id][0]} to {val}")
                            if changed_end_date:
                                for id, val in changed_end_date.items():
                                    cur.execute("UPDATE Holiday SET endDate = (?) WHERE ID = (?)", (datetime.strptime(val, '%d/%m/%Y').date().strftime('%Y-%m-%d'), id))
                                    log_tools.tprint(f"Saved to DB: Holiday Name {changed_names[id] if id in changed_names.keys() else id_to_name[id]} changed End Date from {id_to_range[id][1]} to {val}")
                            db_con.commit()
                    break
                else:
                    print("No changed saved because non where found.")

def holiday_menu() -> bool:
    while 1:
        if len(data['holidays']) > 0:
            holiday_names = [*data['holidays'].keys()]
            display_holiday_list()
            num_options = True
            print("\n\t--HOLIDAY MENU--\n\tExit and (S)ave Changes\n\te(X)it without saving\n\t1. Add Holiday\n\t2. Remove Holiday\n\t3. Edit Holiday")
        else:
            print('\nNo holidays saved.')
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
                log_tools.tprint(f'Added {name} to Saved Holidays. (Not Saved).')
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
                        log_tools.tprint(f"Removed {old_name} from Saved Holidays. (Not Saved)")
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
                            print(f"\n\t--EDIT HOLIDAY {holiday_names[num]}--\n\te(X)it to previous menu\n\t(S)ave changes\n\t1. Name\n\t2. Start Date\t{data['holidays'][holiday_names[num]][0]}\n\t3. End Date\t{data['holidays'][holiday_names[num]][1]}")
                            field = input('Field to edit:').upper()
                            if field == '1':
                                selector = get_name('holiday', holiday_names)
                                old = holiday_names[num]
                                data['holidays'][selector] = data['holidays'].pop(old)
                                holiday_names.pop(num)
                                holiday_names.append(selector)
                                log_tools.tprint(f"Renamed holiday - {old} to {selector}")
                                break
                            elif field == '2':
                                old = data['holidays'][holiday_names[num]][0]
                                data['holidays'][holiday_names[num]][0] = validate_start_date(data['holidays'][holiday_names[num]][1], data['holidays'][holiday_names[num]][0])
                                log_tools.tprint(f"Changed holiday Start Date - {holiday_names[num]} from {old} to {data['holidays'][holiday_names[num]][0]}")
                                break
                            elif field == '3':
                                old = data['holidays'][holiday_names[num]][1]
                                data['holidays'][holiday_names[num]][1] = validate_end_date(data['holidays'][holiday_names[num]][0], data['holidays'][holiday_names[num]][1])
                                log_tools.tprint(f"Changed holiday End Date - {holiday_names[num]} from {old} to {data['holidays'][holiday_names[num]][1]}")
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
    log_tools.tprint(f'Changed Tally Usage - from {old} to {get_description_of_tally_setting()} (Not Saved)')

def toggle_boolean_setting(setting_key: str) -> None:
    old_setting = settings[setting_key]
    settings[setting_key] = not settings[setting_key]
    log_tools.tprint(f'Changed {setting_key} - from {old_setting} to {settings[setting_key]} (Not Saved)')

def settings_menu() -> bool:
    global database_path
    global data
    while 1:
        print(f"\n\t--CURRENT SETTINGS--\n\t-Main Menu Display-\n\t1. {'Display Completed Percent:':<{33}}{settings['display completed %']}\n\t2. {'Display extra completed:':<{33}}{settings['display extra completed']}\n\t3. {'Display extra Completed Percent:':<{33}}{settings['display extra completed %']}\n\t4. {'Display Recent Activity:':<{33}}{settings['useRecentHoursDisplay']}")
        print(f'\n\t-Usage-\n\t{"(E)dit tallies by:":<{36}}' + get_description_of_tally_setting())
        print(f'\n\t-Storage-\n\t{"S(T)orage Mode":<{36}}{"Database" if settings["useDB"] else "JSON"}')
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
        elif selector == '4':
            toggle_boolean_setting('useRecentHoursDisplay')
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
        elif selector == 'T':
            old_setting = settings['useDB']
            while 1:
                if old_setting != settings['useDB']:
                    print("WARNING--Storage Setting has changed.")
                print(f'--Change Storage Mode ({"Database" if settings["useDB"] else "JSON"} Mode)--')
                field = input(f'(C) to change Option {"JSON" if settings["useDB"] else "Database"} Mode:').upper()
                if field == 'C':
                    toggle_boolean_setting('useDB')
                    if settings['useDB']:
                        database_path = data_path + 'study_tally.db'
                        check_and_create_db(True)
                        break
                    else:
                        print("Keeping this setting will return your data to the state before your previous data was copied to the Database.\nNew data will not be migrated from the Database to JSON.")
                        data, menu_mode = load_data_json(data_path + 'study_tally_data.json')
                        break
                elif field == 'X':
                    break
        else:
            print("Invalid input.")

def check_for_backup(name: str, file_path: str) -> None:
    log_tools.tprint(f'{name} file ({path.abspath(file_path)}) empty or corrupt.')
    if path.isfile(file_path[:-4] + 'old'):
        log_tools.tprint("Backup file (.old) is present.")
        print("\t\tIt is likely you have suffered some data loss.\t\tConsider renaming old file to JSON.")
    else:
        if path.isfile(file_path[:-4] + 'old2'):
            log_tools.tprint("Backup file (.old2) is present.")
            print("\t\tIt is highly likely you have suffered some data loss.\t\tConsider renaming old2 file to JSON.")
        else:
            log_tools.tprint(f"No backup {name} file found.")

def check_and_create_db(second_attempt=False) -> chr:
    if path.isfile(database_path):
        print("Database Found")
        if second_attempt:
            with closing(sqlite3.connect(database_path)) as db_con:
                with closing(db_con.cursor()) as cur:
                    if not cur.execute("SELECT * FROM Subject").fetchone():
                        print('No data found in Subject Table')
                    if not cur.execute("SELECT * FROM Holiday").fetchone():
                        print('No data found in Holiday Table')
            if path.isfile(data_path + 'study_tally_data.json'):
                with open(data_path + 'study_tally_data.json', 'r') as open_file:
                    try:
                        a_json = json.load(open_file, parse_int=int)
                        if a_json:
                            if input("\nOld JSON found do you want to upgrade to database?").upper() == 'Y':
                                copy_json_to_db(a_json)
                    except json.decoder.JSONDecodeError:
                        log_tools.tprint("Error wile checking JSON for DB conversion: Data JSON could be corrupt")
                        check_for_backup("Data", data_path + 'study_tally_data.json')
    else:
        print("Creating Database")
        with closing(sqlite3.connect(database_path)) as db_con:
            with closing(db_con.cursor()) as cur:
                cur.execute("CREATE TABLE Subject (ID INTEGER PRIMARY KEY NOT NULL, subjectName VARCHAR(120), startDate DATE, endDate DATE, enabled INTEGER)")
                cur.execute("CREATE TABLE Holiday (ID INTEGER PRIMARY KEY NOT NULL, holidayName VARCHAR(120), startDate DATE, endDate DATE)")
                cur.execute("CREATE TABLE SubjectDay (subjectID INTEGER NOT NULL, dayCode INTEGER NOT NULL, hours INTEGER, PRIMARY KEY(subjectID, dayCode), FOREIGN KEY(subjectID) REFERENCES Subject(ID))")
                cur.execute("CREATE TABLE LogEntryType (ID INTEGER PRIMARY KEY NOT NULL, entryName VARCHAR(20))")
                cur.execute("CREATE TABLE TimeType (ID INTEGER PRIMARY KEY NOT NULL, entryName VARCHAR(40))")
                cur.execute("CREATE TABLE WorkLog (subjectID INTEGER NOT NULL, logTimestamp TIMESTAMP NOT NULL, timeType INTEGER NOT NULL, hour INTEGER, minute INTEGER, entryType INTEGER NOT NULL, PRIMARY KEY (subjectID, logTimestamp, timeType), FOREIGN KEY(subjectID) REFERENCES Subject(ID), FOREIGN KEY(timeType) REFERENCES TimeType(ID), FOREIGN KEY(entryType) REFERENCES LogEntryType(ID))")
                cur.execute("INSERT INTO LogEntryType (ID, entryName) VALUES (0, 'JSON Import'), (1, 'Manual Tally'), (2, 'Timer Tally'), (3, 'Edit')")
                cur.execute("INSERT INTO TimeType (ID, entryName) VALUES (0, 'During Course Range'), (1, 'Outside Course Range (before exam)'), (2, 'Outside Course Range (after exam)')")
                db_con.commit()
        log_tools.tprint("Database Created")
        if path.isfile(data_path + 'study_tally_data.json'):
            with open(data_path + 'study_tally_data.json', 'r') as open_file:
                try:
                    a_json = json.load(open_file, parse_int=int)
                    if a_json:
                        if input("Old JSON found do you want to upgrade to database?").upper() == 'Y':
                            copy_json_to_db(a_json)
                            if not second_attempt:
                                save_json(settings, settings_json_path, "Settings")
                                print("Database Mode Enabled")
                        else:
                            settings['useDB'] = False
                            save_json(settings, settings_json_path, "Settings")
                            print("Storage option can be changed between JSON and Database in the Settings Menu.")
                            return 'd'
                except json.decoder.JSONDecodeError:
                    log_tools.tprint("Error wile checking JSON for DB conversion: Data JSON could be corrupt")
                    check_for_backup("Data", data_path + 'study_tally_data.json')
                    return 'e'
    return 'm'

def copy_json_to_db(json_data) -> None:
    num_subjects = num_worklog = num_holiday = num_days = 0
    now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with closing(sqlite3.connect(database_path)) as db_con:
        with closing(db_con.cursor()) as cur:
            for subject in json_data['subjects']:
                cur.execute("INSERT INTO Subject (subjectName, startDate, endDate, enabled) VALUES (?, ?, ?, 1)", (subject[0], datetime.strptime(subject[2], '%d/%m/%Y').strftime('%Y-%m-%d'), datetime.strptime(subject[3], '%d/%m/%Y').strftime('%Y-%m-%d')))
                cur.execute("SELECT ID FROM Subject WHERE subjectName IS (?)", (subject[0],))
                subject_name = cur.fetchone()[0]
                for day, hours in subject[1].items():
                    cur.execute("INSERT INTO SubjectDay (subjectID, dayCode, hours) VALUES (?, ?, ?)", (subject_name, int(day), hours))
                    num_days += 1
                if subject[4][1] != 0 or subject[4][0] != 0:
                    cur.execute("INSERT INTO WorkLog (subjectID, logTimestamp, timeType, hour, minute, entryType) VALUES (?, ?, 0, ?, ?, 0)", (subject_name, now_time_str, subject[4][0], subject[4][1]))
                    num_worklog += 1
                if subject[5][1] != 0 or subject[5][0] != 0:
                    cur.execute("INSERT INTO WorkLog (subjectID, logTimestamp, timeType, hour, minute,  entryType) VALUES (?, ?, 1, ?, ?, 0)", (subject_name, now_time_str, subject[5][0], subject[5][1]))
                    num_worklog += 1
                num_subjects += 1
            for holiday_name, dates in json_data['holidays'].items():
                cur.execute("INSERT INTO Holiday (holidayName, startDate, endDate) VALUES (?, ?, ?)", (holiday_name, datetime.strptime(dates[0], '%d/%m/%Y').strftime('%Y-%m-%d'), datetime.strptime(dates[1], '%d/%m/%Y').strftime('%Y-%m-%d')))
                num_holiday += 1
            db_con.commit()
    log_tools.tprint(f"JSON Import complete, includes {num_subjects} Subjects, {num_worklog} Work Logs, {num_days} Day settings, {num_holiday} Holidays.")
    if path.isfile(data_path + 'study_tally_data_before_database.json'):
        print(f'JSON file from previous Database upgrade exists. - Please check {data_path}')
    else:
        log_tools.tprint(f'Created backup of study_tally_data.json as study_tally_data_before_database.json')
    save_json(json_data, data_path + 'study_tally_data_before_database.json', "Pre Database JSON")

def load_data_json(json_path):
    if path.isfile(json_path):
        with open(json_path, 'r') as open_file:
            try:
                return json.load(open_file, parse_int=int), 'm'
            except json.decoder.JSONDecodeError:
                check_for_backup("Data", json_path)
                return None, 'e'
    else:
        print('No Data file found')
        return dict(), 'm'

def get_past_hours(now_time):
    blank_time = " 00:00:00"
    one_day = timedelta(days=1)
    output_dict = dict()
    records_dict = dict()
    # temp_list = daily_progress_keys[0:-1]
    with closing(sqlite3.connect(database_path)) as db_connection:
        with closing(db_connection.cursor()) as cur:
            records_dict[daily_progress_keys[-1]] = cur.execute('SELECT logTimestamp, SUM(hour), SUM(minute) FROM WorkLog WHERE logTimestamp >= (?) ORDER BY logTimestamp', (now_time.strftime('%Y-%m-%d') + blank_time,)).fetchone()
            for i in daily_progress_keys[-2::-1]:
                end_time_str = now_time.strftime('%Y-%m-%d') + blank_time
                now_time -= one_day
                records_dict[i] = cur.execute('SELECT logTimestamp, SUM(hour), SUM(minute) FROM WorkLog WHERE logTimestamp >= (?) AND logTimestamp < (?) ORDER BY logTimestamp', (now_time.strftime('%Y-%m-%d') + blank_time, end_time_str)).fetchone()
    for t in daily_progress_keys:
        if t in records_dict and records_dict[t][0]:
            output_dict[t] = [records_dict[t][1], records_dict[t][2]]
            correct_time_format_for_pos_minute(output_dict[t])
    if 'day1Tally' not in output_dict:
        output_dict['day1Tally'] = [0, 0]
    return output_dict

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
    timer_running = True
    day_options = 'MTWHFSU'
    data_path = ".\\data\\"
    settings_json_path = r'.\data\study_tally_settings.json'
    weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    menu_weekdays = ("(M)onday", "(T)uesday", "(W)ednesday", "T(H)ursday", "(F)riday", "(S)aturday", "S(U)nday")

    print("Study Time Tally\n\tBy Michael Fulcher\nSend Donations to - PayPal: mjfulcher58@gmail.com or Bitcoin: 3DXiJxie6En3wcyxjmKZeY2zFLEmK8y42U -- Suggested Donation: $1.50USD\nOther donation options @ http://michaelfulcher.yolasite.com/\n\n")
    if not path.isdir(r'.\data'):
        from os import makedirs
        makedirs('data')
        log_tools.tprint("Data directory created.")
        del makedirs
    if path.isfile(settings_json_path):
        with open(settings_json_path, 'r') as open_file:
            try:
                settings = json.load(open_file, parse_int=int)
                if 'useDB' not in settings:
                    settings['useDB'] = True
                if 'useRecentHoursDisplay' not in settings:
                    settings['useRecentHoursDisplay'] = True
            except json.decoder.JSONDecodeError:
                check_for_backup("Settings", settings_json_path)
                menu_mode = 'e'
    else:
        settings = {'display completed %': True, 'display extra completed': False, 'display extra completed %': False, 'tallyEditHour': True, 'tallyEditMinute': True, 'useDB': True}
    if settings['useDB']:
        database_path = data_path + 'study_tally.db'
        daily_progress_keys = ['day7Tally', 'day6Tally', 'day5Tally', 'day4Tally', 'day3Tally', 'day2Tally', 'day1Tally']
        if (menu_mode := check_and_create_db()) == 'd':
            data, menu_mode = load_data_json(data_path + 'study_tally_data.json')
        last_past_hours_update = datetime.now().date()
        past_hours = get_past_hours(last_past_hours_update)
    else:
        data, menu_mode = load_data_json(data_path + 'study_tally_data.json')
    while menu_mode not in ['X', 'e']:
        if menu_mode == 'm':
            menu_mode = main_menu()
        elif menu_mode == 'T':
            add_to_tally()
            menu_mode = 'm'
        elif menu_mode == 'I':
            timer_tally()
            menu_mode = 'm'
        elif menu_mode == 'A':
            if settings['useDB']:
                add_menu_db()
            else:
                if 'subjects' not in data:
                    data['subjects'] = list()
                data['subjects'].append(add_menu())
                save_json(data, data_path + 'study_tally_data.json', "Data")
            menu_mode = 'm'
        elif menu_mode == 'R':
            remove_menu()
            menu_mode = 'm'
        elif menu_mode == 'E':
            if settings['useDB']:
                edit_menu_db()
            elif edit_menu():
                save_json(data, data_path + 'study_tally_data.json', "Data")
            menu_mode = 'm'
        elif menu_mode == 'H':
            if settings['useDB']:
                holiday_menu_db()
            else:
                if 'holidays' not in data:
                    data['holidays'] = dict()
                if holiday_menu():
                    save_json(data, data_path + 'study_tally_data.json', "Data")
            menu_mode = 'm'
        elif menu_mode == 'S':
            if settings_menu():
                save_json(settings, settings_json_path, "Settings")
            menu_mode = 'm'
    if menu_mode == 'e':
        print("\nExited on error.")
    else:
        print("\nBye.")
