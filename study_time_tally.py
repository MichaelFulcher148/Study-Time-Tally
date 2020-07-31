"""Study Time Tally
    By Michael Fulcher

    Send Donations (recommended $1.50USD) to -
    PayPal: mjfulcher58@gmail.com
    Bitcoin: 3EjKSBQka7rHaLqKMXKZ8t7sHDa546GWAd
    Other options @ http://michaelfulcher.yolasite.com/
"""
'''[0] Name of Subject, [1] Days to iterate required hours up and Amount of hours per day in, [2] Start date, [3] End Date, [4] Hours done'''
import time, json
from os import path, rename as file_rename, remove as file_del
from math import ceil
from datetime import date, timedelta, datetime
import log_tools
log_tools.script_id = "StudyTimeTally"
log_tools.run_date = time.strftime('%d-%m-%Y', time.localtime())
log_tools.initialize(False)
day_options = 'MTWHFSU'
weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
menu_weekDays = ("(M)onday","(T)uesday","(W)ednesday","T(H)ursday","(F)riday","(S)aturday","S(U)nday")
menu_mode = 'm'
data_json_path = r'.\data\study_tally_data.json'
settings_json_path = r'.\data\study_tally_settings.json'

print("Study Time Tally\n\tBy Michael Fulcher\nSend Donations to - PayPal: mjfulcher58@gmail.com or Bitcoin: 3EjKSBQka7rHaLqKMXKZ8t7sHDa546GWAd -- Suggested Donation: $1.50USD\nOther donation options @ http://michaelfulcher.yolasite.com/\n\n")
if not path.isdir(r'.\data'):
    from os import makedirs
    makedirs('data')
    log_tools.tprint("Data directory created.")
    del makedirs
if path.isfile(data_json_path):
    with open(data_json_path, 'r') as open_file:
        data = json.load(open_file, parse_int = int)
else:
    data = dict()
if path.isfile(settings_json_path):
    with open(settings_json_path, 'r') as open_file:
        settings = json.load(open_file, parse_int = int)
else:
    settings = dict()
    settings['display completed %'] = True
    settings['display extra completed'] = False
    settings['display extra completed %'] = False

def save_json(data, json_path, label):
    json_path_old = json_path[:-4] + 'old'
    json_path_old2 = json_path_old + '2'
    if path.isfile(json_path):
        if path.isfile(json_path_old):
            if path.isfile(json_path_old2):
                file_del(json_path_old2)
            file_rename(json_path_old, json_path_old2)
        file_rename(json_path, json_path_old)
    with open(json_path, 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=4)
    log_tools.tprint(label + ' JSON Written')

def menu_char_check(a_word, options):
    message = " is not a valid input"
    if len(a_word) == 0:
        print("Enter" + message)
    elif len(a_word) == 1 and a_word in options:
        return True
    else:
        print(a_word + message)
    return False

'''Found @: https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python#_=_'''
def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%d/%m/%Y').date()
        return True
    except ValueError:
        print(date_text + " not a valid input")
        return False

def get_date():
    while(1):
        date = input("Enter Date (dd/mm/yyyy):")
        if validate_date(date):
            return date

def validate_start_date(end_date, old):
    while(1):
        print("\nStart Date, format - dd/mm/yyyy. Current Date (" + old + ")")
        start_date = get_date()
        if datetime.strptime(end_date, '%d/%m/%Y').date() > datetime.strptime(start_date, '%d/%m/%Y').date():
            print("Start date must be before the end date (" + end_date + ").")
        else:
            return start_date

def validate_end_date(start_date, old = None):
    while(1):
        if old:
            print("\nEnd Date, format - dd/mm/yyyy. Current Date (" + old + ")")
        else:
            print("\nEnd Date, format - dd/mm/yyyy.")
        end_date = get_date()
        if datetime.strptime(end_date, '%d/%m/%Y').date() < datetime.strptime(start_date, '%d/%m/%Y').date():
            print("End date must be after the start date (" + start_date + ").")
        else:
            return end_date

'''found @: https://stackoverflow.com/questions/9044084/efficient-date-range-overlap-calculation-in-python
    requires passed vars to be datetime objects'''
def overlap_check(start_of_range1, end_of_range1, start_of_range2, end_of_range2):
    latest_start = max(start_of_range1, start_of_range2)
    earliest_end = min(end_of_range1, end_of_range2)
    delta = (earliest_end - latest_start).days + 1
    if delta > 0:
        return True
    else:
        return False

def tally_hours(start_date, end_date, day_dict):
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
            while n < rangelist_size:
    ##            holiday_start = holiday[0]
    ##            holiday_end = holiday[1]
    ##            term_end = range_list[n][1]
    ##            term_start = range_list[n][0]
                if holiday[0] > range_list[n][1] or holiday[1] < range_list[n][0]: #filter out pointless tests
                    n += 1
                    continue
                if holiday[0] <= range_list[n][0]: # holiday starts before or start of term
                    if holiday[1] >= range_list[n][1]:
                        range_list.pop(n)
                        rangelist_size -= 1
                    else:
                        range_list[n][0] = holiday[1] + one_day
                        n += 1
                else: #holiday starts after 'term' starts.
                    new_end = holiday[0] - one_day
                    if holiday[1] < range_list[n][1]:
                        range_list.append([holiday[1] + one_day, range_list[n][1]])
                        range_list[n][1] = new_end
                        rangelist_size += 1
                        break
                    else:
                        range_list[n][1] = new_end
                        n += 1
    n = 0 # n var repurposed to grand total of hours
    weeks_hours = 0
    for hour in day_dict.values():
        weeks_hours += hour
    for i in range_list:        
        weeks = i[0].weekday()
        days = (i[1] - i[0]).days + (1 if weeks == 0 else weeks - 6)
        while weeks not in [0,7]:
            sch = str(weeks)
            if sch in day_dict.keys():
                n += day_dict[sch]
            weeks += 1
        weeks = days // 7 # weeks repurposed to 'number of weeks'
        days = days % 7 # days var repurposed to length of week.
        n += weeks * weeks_hours
        if days != 0:
            weeks = i[1].weekday() # weeks repurposed to 'day of week number'
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

def tabs_list(a_list): ## generate data for correct spacing in data display coloumns
    t_width = 0
    n = 0
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

def display_holiday_list(add_numbers = False):
    t_width, add_space, tabs = tabs_list([*data['holidays'].keys()])
    print('\nSaved Holidays:\n' + ('\t' if add_numbers else '') + 'Name' + '\t'*t_width + (' ' if add_space else '') + 'Start Date\tEnd Date')
    n = 0
    for holiday,dates in data['holidays'].items():
        print((str(n) + '.\t' if add_numbers else '') + holiday + '\t'*tabs[n] + (' ' if add_space else '') + dates[0] + '\t' + dates[1])
        n += 1
    return n

def main_menu():
    valid_option = False
    if "subjects" in data and len(data["subjects"]) > 0:
        items_present = True
        t_width, add_space, tabs = tabs_list([i[0] for i in data['subjects']])
    else:
        items_present = False
    while not valid_option:
        if items_present:
            print('\nTally totals:\nName' + '\t'*t_width + (' ' if add_space else '') + 'Hours Oweing\tHours Completed' + ('\t%\t' if settings['display completed %'] == True else ('\t' if settings['display extra completed %'] == False else '')) + ('|Extra Completed' if settings['display extra completed'] == True else '\t') + (' %' if settings['display extra completed %'] == True else ''))
            n = 0
            for subject in data["subjects"]:
                hours = tally_hours(subject[2], subject[3], subject[1])
                print(subject[0] + '\t'*tabs[n] + (' ' if add_space else '') + str(hours) + '\t\t' + str(subject[4][0]) + 'h ' + str(subject[4][1]) + 'm\t' + ('\t{:.1%}'.format((subject[4][0] * 60 + subject[4][1]) / (hours * 60)) if settings['display completed %'] == True else '') + ('\t|' + str(subject[5][0]) + 'h ' + str(subject[5][1]) + 'm' if settings['display extra completed'] == True else '') + ('\t\t {:.1%}'.format(((subject[4][0] + subject[5][0]) * 60 + subject[4][1] + subject[5][1]) / (hours * 60)) if settings['display extra completed %'] == True else ''))
                n += 1
        else:
            print("Subject list is empty.")
        print('\n--MAIN MENU--\n\tAdd to (T)ally\n\t(A)dd Subject\n\t(R)emove Subject\n\t(E)dit Subject\n\t(H)olidays Menu\n\t(S)ettings Menu\n\te(X)it')
        menu_option = input("Choose Option:").upper()
        valid_option = menu_char_check(menu_option, 'TXAREHS')
    return menu_option

def print_selected_days(day_list):
    if len(day_list) > 0:
        print("\nSelected Days:")
        for i in day_list:
            print(weekDays[int(i)])
    else:
        print("No days Selected")

def setup_day_options(start_date, end_date, need_length = True):
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

def check_digit(numStr, allowEnterBeZero):
    if numStr == '':
        if allowEnterBeZero:
            return True, 0
        else:
            print('<Enter> is not valid input.')
            return False, 0
    elif numStr.isdecimal():
        return True, int(numStr)
    else:
        print("Input must be a decimal number.")
        return False, 0

def get_time_digit(time_div):
    validNum = False
    while not validNum:
        selector = input('Number of ' + time_div + '(s) to add:')
        validNum, digit = check_digit(selector, True)
    return digit

def get_hour(day_num):
    validNum = False
    while not validNum:
        selector = input("Number of hours for " + weekDays[day_num] + ":")
        validNum, digit = check_digit(selector, False)
    return digit

def create_days_dict(s_day_options, length, returnDayList = False, days = dict()):
    if length == 1:
        length = day_options.find(s_day_options)
        dayStr = str(length)
        days[dayStr] = None
        print("Course is one day, day is auto-set to " + weekDays[length])
    else:
        if returnDayList:
            dayList = list()
        day_pick_number = 0
        while(1):
            print_selected_days(days)
            output = str()
            for day in s_day_options:
                output += menu_weekDays[day_options.find(day)] + ", "
            print('\n--SELECT DAYS--\n' + output[:-2] + '\nEnter X when finnished.')
            selector = input('Option:').upper()
            if menu_char_check(selector, s_day_options + 'X'):
                if selector == "X":
                    break
                dayStr = str(day_options.find(selector))
                days[dayStr] = None
                if returnDayList:
                    dayList.append(dayStr)
                day_pick_number += 1
                if day_pick_number == length:
                    break
                n = s_day_options.rfind(selector)
                s_day_options = s_day_options[:n] + s_day_options[n + 1:]
    for day in days:
        if not days[day]:
            days[day] = get_hour(int(day))
    if returnDayList:
        return days, dayList
    else:
        return days

def get_name(type_text, name_list):
    while(1):
        name = input("Name of " + type_text + ":")
        if len(name) > 0:
            if name not in name_list:
                return name
            else:
                print("Name " + name + " already exists.")
        else:
            print("Name must be atleast 1 character.")

def add_menu():
    name_list = [x[0] for x in data['subjects']]
    print('\n--ADD SUBJECT--')
    name = get_name('Subject', name_list)
    print("\nStart Date, format - dd/mm/yyyy.")
    start_date = get_date()
    end_date = validate_end_date(start_date)
    days = create_days_dict(*setup_day_options(start_date, end_date))
    log_tools.tprint("Added Subject - " + name)
    return [name, days, start_date, end_date]

def display_subject_list():
    t = 0
    for subject in data["subjects"]:
        print(str(t) + " - " + subject[0])
        t += 1
    return t

def validate_selector(a_string, num):
    if a_string.isnumeric():
        a = int(a_string)
        if a >= 0 and a < num:
            return True
        else:
            print(a_string + " is not a valid option")
            return False

def remove_menu():
    if "subjects" in data and len(data['subjects']) > 0:
        while(1):
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
    new_day_range_list = [str(day_optins.find(x)) for x in new_day_range]
    dayList = list() #days that may be removed later
    day_range_change = False
    for day in old_day_range:
        if day not in new_day_range_list:
            day_range_change = True
            dayList.append(day)
    return day_range_change, dayList

def remove_days_from_dict(subject, remove_list):
    for i in remove_list:
        data['subjects'][subject][1].pop(i)

def change_date(subject, date2change, dateWordStr, length, new_start_date_obj, new_end_date_obj, newDate):
    if length < 7:
        day_range_change, dayList = check_day_range(new_start_date_obj, new_end_date_obj, [*data['subjects'][subject][1].keys()])
        if day_range_change:
            logOutput = str()
            questionStr = "Is this correct?\n(Y)es to make changes\n(N)o to cancel changes\n:"
            for day in dayList:
                logOutput += weekDays[int(day)] + ", "
            logOutMsg = logOutput[:-2] + " will be removed.\n"
            if length == 1:
                while(1):
                    dayOfWeek = new_start_date_obj.weekday()
                    dayOfWeekStr = str(dayOfWeek)
                    selector = input("\nDetected that your new day range is one day, day will be auto-set to " + weekDays[dayOfWeek] + ("." if len(logOutput) == 0 else " and " + logOutMsg) + questionStr).upper()
                    if selector == "N":
                        break
                    elif selector == "Y":
                        old = data['subjects'][subject][date2change]
                        data['subjects'][subject][date2change] = newDate
                        if dayOfWeekStr in data['subjects'][subject][1].keys():
                            remove_days_from_dict(subject, dayList)
                            log_tools.tprint("Changed " + data['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + data['subjects'][subject][date2change] + " and removed " + logOutput[:-2] + ". (Not Saved)")
                        else:
                            remove_days_from_dict(subject, dayList)
                            data['subjects'][subject][1][dayOfWeekStr] = get_hour(int(dayOfWeek))
                            log_tools.tprint("Changed " + data['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + data['subjects'][subject][date2change] + ", added " + weekDays[dayOfWeek] + " and removed " + logOutput[:-2] + ". (Not Saved)")
                        break
                    else:
                        print("Invalid input.")
            else:
                while(1):
                    selector = input("\nDetected that your new day range is less than the old day range.\n" + logOutMsg + questionStr).upper()
                    if selector == "N":
                        break
                    elif selector == "Y":
                        remove_days_from_dict(subject, dayList)
                        old = data['subjects'][subject][date2change]
                        data['subjects'][subject][date2change] = newDate
                        log_tools.tprint("Changed " + data['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + data['subjects'][subject][date2change] + " and removed " + logOutput[:-2] + ". (Not Saved)")
                        break
                    else:
                        print("Invalid input.")
    else:
        old = data['subjects'][subject][date2change]
        data['subjects'][subject][date2change] = newDate
        log_tools.tprint("Changed " + data['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + data['subjects'][subject][date2change] + ". (Not Saved)")

def edit_time_tally(subject_choice, time_category):
    selector = None
    print("\n--Edit " + ("Normal" if time_category == 4 else "Extra") + " Tally of " + data['subjects'][subject_choice][0] + "--\nCurrent Tally: " + str(data['subjects'][subject_choice][time_category][0]) + "h " + str(data['subjects'][subject_choice][time_category][1]) + "m\nChanges are done by subtracting, not by directed edit.")
    while selector != 'X':
        selector = input("--Field to edit:\n1. Hour\n2. Minute\ne(X)it without saving\n:").upper()
        if selector == '1':
            while(1):
                selector = input("Decrease hour by:").upper()
                if selector == 'X':
                    break
                elif selector.isdigit():
                    n = int(selector)
                    if data['subjects'][subject_choice][time_category][0] < n:
                        print("Amount to subtract cannot be larger than current hours (" + str(data['subjects'][subject_choice][time_category][0]) + "h)")
                    else:
                        old = data['subjects'][subject_choice][time_category][0]
                        data['subjects'][subject_choice][time_category][0] -= n
                        log_tools.tprint("Decreased " + data['subjects'][subject_choice][0] + " - hour by " + selector + " from " + str(old) + "h to " + str(data['subjects'][subject_choice][time_category][0]) + "h. (Not Saved).")
                        selector = 'X'
                        break
                else:
                    print("Input must be a number")
        elif selector == '2':
            while(1):
                selector = input("Decrease minutes by (can subtract greater than 59minutes):").upper()
                if selector == 'X':
                    break
                elif selector.isdigit():
                    n = int(selector)
                    old = data['subjects'][subject_choice][time_category][0] * 60 + data['subjects'][subject_choice][time_category][1]
                    if n > old:
                        print("Amount to subtract cannot be larger then current hours + minutes (" + str(data['subjects'][subject_choice][time_category][0]) + "h " + str(data['subjects'][subject_choice][time_category][1]) + "m)")
                    else:
                        old = data['subjects'][subject_choice][time_category][0]
                        old_minute = data['subjects'][subject_choice][time_category][1]
                        data['subjects'][subject_choice][time_category][1] -= n
                        while data['subjects'][subject_choice][time_category][1] < 0:
                            data['subjects'][subject_choice][time_category][1] += 60
                            data['subjects'][subject_choice][time_category][0] -= 1
                        log_tools.tprint("Decreased " + data['subjects'][subject_choice][0] + " - " + ("Normal" if time_category == 4 else "Extra") + " time by " + selector + " from " + str(old) + "h " + str(old_minute) + "m to " + str(data['subjects'][subject_choice][time_category][0]) + "h " + str(data['subjects'][subject_choice][time_category][1]) + "m. (Not Saved).")
                        selector = 'X'
                        break
                else:
                    print("Input must be a number")
        elif selector != "X":
            print("Invalid input.")

def edit_menu():
    if "subjects" in data and len(data['subjects']) > 0:
        while(1):
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
                while(1): ##if user changes dates do check on day range and incorrect days are selected then - thow error
                    if data['subjects'][subject_choice][3] == data['subjects'][subject_choice][2]:
                        oneDayCourse = True
                        n = 5
                    else:
                        oneDayCourse = False
                        n = 7
                    print("\n--Edit Subject " + data['subjects'][subject_choice][0] + "--\ne(X)it to previous menu\n(S)ave changes\n1. Name\n2. Start Date\t\t" + data['subjects'][subject_choice][2] + "\n3. End Date\t\t" + data['subjects'][subject_choice][3] + ("\n4. Add Day\n5. Remove Day" if oneDayCourse == False else "") + "\n6. Remove from Normal Tally\t" + str(data['subjects'][subject_choice][4][0]) + "h " + str(data['subjects'][subject_choice][4][1]) + "m" + "\n7. Remove from Extra Tally\t" + str(data['subjects'][subject_choice][5][0]) + "h " + str(data['subjects'][subject_choice][5][1]) + "m" + "\n::Edit a Day")
                    for day, hour in data['subjects'][subject_choice][1].items():
                        n += 1
                        print(str(n) + ". " + weekDays[int(day)] + "\t\tHours: " + str(hour))
                    selector = input("Field to edit:").upper()
                    if selector == 'X':
                        break
                    elif selector == 'S':
                        log_tools.tprint("Exiting edit menu and saving changes.")
                        return True
                    else:
                        if validate_selector(selector, n + 1):
                            field = int(selector)
                            if (oneDayCourse == False and field > 7) or (oneDayCourse == True and field > 5): # Change day hours
                                day = [*data['subjects'][subject_choice][1].keys()][field - 6 if oneDayCourse else field - 8]
                                while(1):
                                    dayName = weekDays[int(day)]
                                    print("\n--Edit " + data['subjects'][subject_choice][0] + " " + dayName + "--\n--X to exit.")
                                    num = input("Number of hours:").upper()
                                    if num.isdecimal():
                                        old = data['subjects'][subject_choice][1][day]
                                        data['subjects'][subject_choice][1][day] = int(num)
                                        log_tools.tprint("Changed " + data['subjects'][subject_choice][0] + " " + dayName + " time from " + str(old) + " to " + str(data['subjects'][subject_choice][1][day]) + ". (Not Saved)")
                                        break
                                    elif num == "X":
                                        break
                                    else:
                                        print("Number must be a decimal number.")
                            else:
                                if field == 1: # Change Name
                                    name = input("\nNew name of Subject:")
                                    if len(name) > 0:
                                        old = data['subjects'][subject_choice][0]
                                        data['subjects'][subject_choice][0] = name
                                        log_tools.tprint("Renamed " + old + " to " + data['subjects'][subject_choice][0])
                                    else:
                                        print("Name must be atleast 1 character.")
                                        break
                                elif field == 2: # Change start date
                                    old = data['subjects'][subject_choice][2]
                                    while(1):
                                        print("\nStart Date, format - dd/mm/yyyy. Current Date (" + data['subjects'][subject_choice][2] + ")")
                                        newDate = get_date()
                                        new_date_obj = datetime.strptime(newDate, '%d/%m/%Y').date()
                                        end_date_obj = datetime.strptime(data['subjects'][subject_choice][3], '%d/%m/%Y').date()
                                        if end_date_obj < new_date_obj:
                                            print("Start date must be before the end date (" + data['subjects'][subject_choice][3] + ").")
                                        else:
                                            break
                                    change_date(subject_choice, 2, "start", (end_date_obj - new_date_obj).days + 1, new_date_obj, end_date_obj, newDate)
                                elif field == 3: # Change end date
                                    newDate = validate_end_date(data['subjects'][subject_choice][2])
                                    start_date_obj = datetime.strptime(data['subjects'][subject_choice][2], '%d/%m/%Y').date()
                                    new_date_obj = datetime.strptime(newDate, '%d/%m/%Y').date()
                                    change_date(subject_choice, 3, "end", (new_date_obj - start_date_obj).days + 1, start_date_obj, new_date_obj, newDate)
                                elif field == 4: # Add days
                                    s_day_options, length = setup_day_options(data['subjects'][subject_choice][2], data['subjects'][subject_choice][3])
                                    for day in data['subjects'][subject_choice][1].keys():
                                        n = s_day_options.rfind(day_options[int(day)])
                                        s_day_options = s_day_options[:n] + s_day_options[n + 1:]
                                    print(s_day_options)
                                    data['subjects'][subject_choice][1], dayList = create_days_dict(s_day_options, length, True, data['subjects'][subject_choice][1])
                                    logOutput = str()
                                    for day in dayList:
                                        logOutput += weekDays[int(day)] + " " + str(data['subjects'][subject_choice][1][day]) + " hour" + ("" if data['subjects'][subject_choice][1][day] == 1 else "s") + ", "
                                    log_tools.tprint("Added to " + data['subjects'][subject_choice][0] + " - " + logOutput[:-2] + ". (Not Saved)")
                                elif field == 5: # Remove a day
                                    print("\n--Remove a day from " + data['subjects'][subject_choice][0] + '--')
                                    days = [*data['subjects'][subject_choice][1].keys()]
                                    while(1):
                                        n = 0
                                        for day, hour in data['subjects'][subject_choice][1].items():
                                            n += 1
                                            print(str(n) + ". " + weekDays[int(day)] + "\t Hour" + ("" if hour == 1 else "s") + ": " + str(hour))
                                        selector = input("Field to edit:").upper()
                                        if selector == 'X':
                                            break
                                        elif validate_selector(selector, n + 1):
                                            n = int(selector) - 1
                                            data['subjects'][subject_choice][1].pop(days[n])
                                            log_tools.tprint("Removed " + weekDays[int(days[n])] + " from " + data['subjects'][subject_choice][0] + ". (Not Saved)")
                                            break
                                elif field == 6: # Edit Normal Tally
                                    edit_time_tally(subject_choice, 4)
                                elif field == 7: # Edit Extra Tally
                                    edit_time_tally(subject_choice, 5)
    else:
        print("\nSubject list is empty.")
    return False  

def add_hourAndminute(subject, time_category, hour, minute):
    data['subjects'][subject][time_category][0] += hour
    data['subjects'][subject][time_category][1] += minute
    while data['subjects'][subject][time_category][1] > 59:
        data['subjects'][subject][time_category][1] -= 60
        data['subjects'][subject][time_category][0] += 1

def add_to_tally():
    if "subjects" in data and len(data['subjects']) > 0:
        while(1):
            print("\n--TALLY MENU--")
            n = display_subject_list()
            selector = input("Subject to add tally to:").upper()
            if selector == "X":
                return False
            elif validate_selector(selector, n):
                selector = int(selector)
                if datetime.strptime(log_tools.run_date, '%d-%m-%Y').date() > datetime.strptime(data['subjects'][selector][3], '%d/%m/%Y').date():
                    time_category = 5
                else:
                    time_category = 4
                while(1):
                    print(data['subjects'][selector][0])
                    number = get_time_digit('hour')
                    old = data['subjects'][selector][time_category][0]
                    break
                while(1):
                    minute = get_time_digit('minute')
                    old_minute = data['subjects'][selector][time_category][1]
                    break
                add_hourAndminute(selector, time_category, number, minute)
                log_tools.tprint("Increased " + data['subjects'][selector][0] + (" Normal" if time_category == 4 else " Extra") + " Hours from " + str(old) + 'h ' + str(old_minute) + "m to " + str(data['subjects'][selector][time_category][0]) + 'h ' + str(data['subjects'][selector][time_category][1]) + 'm.')
                return True
    print("Subject list in empty.")
    return False

def holiday_menu():
    while(1):
        if len(data['holidays']) > 0:
            holiday_names = [*data['holidays'].keys()]
            display_holiday_list()
            num_options = True
            print("\n--HOLIDAY MENU--\nExit and (S)ave Changes\ne(X)it without saving\n\t1. Add Holiday\n\t2. Remove Holiday\n\t3. Edit Holiday")
        else:
            print('\nNo holidays saved.')#make menu change when holiday list empty...
            holiday_names = list()
            num_options = False
            print('\n--HOLIDAY MENU--\nExit and (S)ave Changes\ne(X)it without saving\n\t1. Add Holiday\n')
        selector = input(("Option:" if num_options == True else "Field to edit:")).upper()
        if menu_char_check(selector, 'SX' + ('1' if num_options == False else '123')):
            if selector == '1':
                name = get_name('Holiday', holiday_names)
                print("\nStart Date, format - dd/mm/yyyy.")
                start_date = get_date()
                end_date = validate_end_date(start_date)
                holiday_names.append(name)
                data['holidays'][name] = [start_date, end_date]
                log_tools.tprint('Added ' + name + ' to Saved Holidays. (Not Saved).')
            elif selector == '2':
                while(1):
                    print('\n--REMOVE HOLIDAY MENU--\ne(X)it\n')
                    n = display_holiday_list(True)
                    field = input('Holiday to remove:').upper()
                    if selector == "X":
                        break
                    elif validate_selector(field, n):
                        num = int(field)
                        old_name = holiday_names[num]
                        data['holidays'].pop(holiday_names[num])
                        holiday_names.pop(num)
                        log_tools.tprint('Removed ' + old_name + " from Saved Holidays. (Not Saved)")
                        break
            elif selector == '3':
                while(1):
                    print('\n--EDIT HOLIDAY MENU--\ne(X)it\n')
                    n = display_holiday_list(True)
                    field = input('Holiday to edit:').upper()
                    if field == 'X':
                        break
                    elif validate_selector(field, n):
                        num = int(field)
                        while(1):
                            print('\n--EDIT HOLIDAY ' + holiday_names[num] + '--\ne(X)it to previous menu\n(S)ave changes\n\t1. Name\n\t2. Start Date\t' + data['holidays'][holiday_names[num]][0] + '\n\t3. End Date\t' + data['holidays'][holiday_names[num]][1])
                            field = input('Field to edit:').upper()
                            if field == '1':
                                selector = get_name('holiday', holiday_names)
                                old = holiday_names[num]
                                data['holidays'][selector] = data['holidays'].pop(old)
                                holiday_names.pop(num)
                                holiday_names.append(selector)
                                log_tools.tprint("Renamed holiday - " + old + " to " + selector)
                                break
                            elif field == '2':
                                old = data['holidays'][holiday_names[num]][0]
                                data['holidays'][holiday_names[num]][0] = validate_start_date(data['holidays'][holiday_names[num]][1], data['holidays'][holiday_names[num]][0])
                                log_tools.tprint('Changed holiday - ' + holiday_names[num] + ' from ' + old + ' to ' + data['holidays'][holiday_names[num]][0])
                                break
                            elif field == '3':
                                old = data['holidays'][holiday_names[num]][1]
                                data['holidays'][holiday_names[num]][1] = validate_end_date(data['holidays'][holiday_names[num]][0], data['holidays'][holiday_names[num]][1])
                                log_tools.tprint('Changed holiday - ' + holiday_names[num] + ' from ' + old + ' to ' + data['holidays'][holiday_names[num]][1])
                                break
                            elif field == 'X':
                                break
                            else:
                                print("Invalid input.")
            elif selector == 'X':
                return False
            elif selector == 'S':
                return True

def settings_menu():
    while(1):
        print("\n--CURRENT SETTINGS--" + '\n1. Display Completed Percent:\t\t' + str(settings['display completed %']) + '\n2. Display extra completed:\t\t' + str(settings['display extra completed']) + '\n3. Display extra Completed Percent:\t' + str(settings['display extra completed %']))
        print("\n--SETTINGS MENU--\nExit and (S)ave Changes\ne(X)it without saving")
        selector = input('Option to toggle, or command:').upper()
        if selector == 'X':
            return False
        elif selector == 'S':
            return True
        elif selector == '1':
            settings['display completed %'] = not settings['display completed %']
        elif selector == '2':
            settings['display extra completed'] = not settings['display extra completed']
        elif selector == '3':
            settings['display extra completed %'] = not settings['display extra completed %']
        else:
            print("Invalid input.")

while menu_mode != 'X':
    if menu_mode == 'm':
        menu_mode = main_menu()
    elif menu_mode == 'T':
        if add_to_tally() == True:
            save_json(data, data_json_path, "Data")
        menu_mode = 'm'
    elif menu_mode == 'A':
        if 'subjects' not in data:
            data['subjects'] = list()
        data['subjects'].append(add_menu() + [[0,0],[0,0]])
        save_json(data, data_json_path, "Data")
        menu_mode = 'm'
    elif menu_mode == 'R':
        if remove_menu() == True:
            save_json(data, data_json_path, "Data")
        menu_mode = 'm'
    elif menu_mode == 'E':
        if edit_menu() == True:
            save_json(data, data_json_path, "Data")
        menu_mode = 'm'
    elif menu_mode == 'H':
        if 'holidays' not in data:
            data['holidays'] = dict()
        if holiday_menu() == True:
            save_json(data, data_json_path, "Data")
        menu_mode = 'm'
    elif menu_mode == 'S':
        if settings_menu() == True:
            save_json(settings, settings_json_path, "Settings")
        menu_mode =  'm'
print("\nBye.")
