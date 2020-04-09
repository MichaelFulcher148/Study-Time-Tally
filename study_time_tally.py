"""Study Time Tally
    By Michael Fulcher

    Send Donations (recommended $1.50USD) to -
    PayPal: mjfulcher58@gmail.com
    Bitcoin: 3EjKSBQka7rHaLqKMXKZ8t7sHDa546GWAd
    Other options @ http://michaelfulcher.yolasite.com/
"""
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

print("Study Time Tally\n\tBy Michael Fulcher\nSend Donations to - PayPal: mjfulcher58@gmail.com or Bitcoin: 3EjKSBQka7rHaLqKMXKZ8t7sHDa546GWAd\nOther donation options @ http://michaelfulcher.yolasite.com/\n\n")

if not path.isdir(r'.\data'):
    from os import makedirs
    makedirs('data')
    log_tools.tprint("Data directory created.")
    del makedirs


if path.isfile(data_json_path):
    with open(data_json_path, 'r') as open_file:
        settings = json.load(open_file, parse_int = int)
else:
    settings = dict()

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

'''[0] Name of Subject
    [1] Days to iterate required hours up and Amount of hours per day in
    [2] Start date
    [3] End Date
    [4] Hours done'''

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
        date = input(":")
        if validate_date(date):
            return date

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

def tally_hours(start_date, end_date, day_dict):
    date_start = datetime.strptime(start_date, '%d/%m/%Y').date()
    date_today = datetime.today().date()
    if date_today < date_start:
        return 0
    date_end = datetime.strptime(end_date, '%d/%m/%Y').date()
    if date_end < date_today:
        date_today = date_end
    days = (date_today - date_start).days + 1
    weeks = days // 7
    days = days % 7
    weeks_hours = 0
    for hour in day_dict.values():
        weeks_hours += hour
    hours = weeks * weeks_hours
    if days != 0:
        weeks = date_today.weekday()
        while days >= 0:
            sch = str(weeks)
            if sch in day_dict.keys():
                hours += day_dict[sch]
            days -= 1
            if weeks == 0:
                weeks = 6
            else:
                weeks -= 1
    return hours

def main_menu():
    valid_option = False
    if "subjects" in settings and len(settings["subjects"]) > 0:
        items_present = True
        tabs = list()
        t_width = 0
        n = 0
        for subject in settings['subjects']:
            tabs.append(len(subject[0]))
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
    else:
        items_present = False
    while not valid_option:
        if items_present:
            print('\nTally totals:\nName' + '\t'*t_width + (' ' if add_space else '') + 'Hours Oweing\tHours Competed')
            n = 0
            for subject in settings["subjects"]:
                print(subject[0] + '\t'*tabs[n] + (' ' if add_space else '') + str(tally_hours(subject[2], subject[3], subject[1])) + '\t\t' + str(subject[4][0]) + 'h ' + str(subject[4][1]) + 'm')
                n += 1
        else:
            print("Subject list is empty.")
        print('\n--MAIN MENU--\n\tAdd to (T)ally\n\t(A)dd\n\t(R)emove\n\t(E)dit\n\te(X)it')
        menu_option = input("Choose Option:").upper()
        valid_option = menu_char_check(menu_option, 'TXARE')
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
                n = s_day_options.rfind(selector)
                s_day_options = s_day_options[:n] + s_day_options[n + 1:]
    for day in days:
        if not days[day]:
            days[day] = get_hour(int(day))
    if returnDayList:
        return days, dayList
    else:
        return days

def add_menu():
    name_list = [x[0] for x in settings['subjects']]
    print('\n--ADD SUBJECT MENU--')
    while(1):
        name = input("Name of Subject:")
        if len(name) > 0:
            if name not in name_list:
                break
            else:
                print("Name " + name + " already exists.")
        else:
            print("Name must be atleast 1 character.")
    print("\nStart Date, format - dd/mm/yyyy.")
    start_date = get_date()
    end_date = validate_end_date(start_date)
    days = create_days_dict(*setup_day_options(start_date, end_date))
    log_tools.tprint("Added Subject - " + name)
    return [name, days, start_date, end_date]

def display_subject_list():
    t = 0
    for subject in settings["subjects"]:
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
    if "subjects" in settings and len(settings['subjects']) > 0:
        while(1):
            print("\n--REMOVE MENU--")
            n = display_subject_list()
            selector = input("Subject to remove:").upper()
            if selector == "X":
                return False
            elif validate_selector(selector, n):
                old = settings["subjects"].pop(int(selector))[0]
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
        settings['subjects'][subject][1].pop(i)

def change_date(subject, date2change, dateWordStr, length, new_start_date_obj, new_end_date_obj, newDate):
    if length < 7:
        day_range_change, dayList = check_day_range(new_start_date_obj, new_end_date_obj, [*settings['subjects'][subject][1].keys()])
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
                        old = settings['subjects'][subject][date2change]
                        settings['subjects'][subject][date2change] = newDate
                        if dayOfWeekStr in settings['subjects'][subject][1].keys():
                            remove_days_from_dict(subject, dayList)
                            log_tools.tprint("Changed " + settings['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + settings['subjects'][subject][date2change] + " and removed " + logOutput[:-2] + ". (Not Saved)")
                        else:
                            remove_days_from_dict(subject, dayList)
                            settings['subjects'][subject][1][dayOfWeekStr] = get_hour(int(dayOfWeek))
                            log_tools.tprint("Changed " + settings['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + settings['subjects'][subject][date2change] + ", added " + weekDays[dayOfWeek] + " and removed " + logOutput[:-2] + ". (Not Saved)")
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
                        old = settings['subjects'][subject][date2change]
                        settings['subjects'][subject][date2change] = newDate
                        log_tools.tprint("Changed " + settings['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + settings['subjects'][subject][date2change] + " and removed " + logOutput[:-2] + ". (Not Saved)")
                        break
                    else:
                        print("Invalid input.")
    else:
        old = settings['subjects'][subject][date2change]
        settings['subjects'][subject][date2change] = newDate
        log_tools.tprint("Changed " + settings['subjects'][subject][0] + " " + dateWordStr + " date from " + old + " to " + settings['subjects'][subject][date2change] + ". (Not Saved)")

def edit_menu():
    if "subjects" in settings and len(settings['subjects']) > 0:
        while(1):
            print("\n--EDIT MENU--\nExit and (S)ave Changes\ne(X)it without saving")
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
                    if settings['subjects'][subject_choice][3] == settings['subjects'][subject_choice][2]:
                        oneDayCourse = True
                        n = 3
                    else:
                        oneDayCourse = False
                        n = 5
                    print("\n--Edit Subject " + settings['subjects'][subject_choice][0] + "--\ne(X)it to previous menu\n(S)ave changes\n1. Name\n2. Start Date\t" + settings['subjects'][subject_choice][2] + "\n3. End Date\t" + settings['subjects'][subject_choice][3] + ("\n4. Add Day\n5. Remove Day" if oneDayCourse == False else "") + "\n::Edit a Day")
                    for day, hour in settings['subjects'][subject_choice][1].items():
                        n += 1
                        print(str(n) + ". " + weekDays[int(day)] + "\t Hours: " + str(hour))
                    selector = input("Field to edit:").upper()
                    if selector == 'X':
                        break
                    elif selector == 'S':
                        log_tools.tprint("Exiting edit menu and saving changes.")
                        return True
                    else:
                        if validate_selector(selector, n + 1):
                            field = int(selector)
                            if (oneDayCourse == False and field > 5) or (oneDayCourse == True and field > 3): # Change day hours
                                day = [*settings['subjects'][subject_choice][1].keys()][field - 4 if oneDayCourse else field - 6]
                                while(1):
                                    dayName = weekDays[int(day)]
                                    print("\n--Edit " + settings['subjects'][subject_choice][0] + " " + dayName + "--")
                                    num = input("Number of hours:")
                                    if num.isdecimal():
                                        old = settings['subjects'][subject_choice][1][day]
                                        settings['subjects'][subject_choice][1][day] = int(num)
                                        log_tools.tprint("Changed " + settings['subjects'][subject_choice][0] + " " + dayName + " time from " + str(old) + " to " + str(settings['subjects'][subject_choice][1][day]) + ". (Not Saved)")
                                        break
                                    else:
                                        print("Number must be a decimal number.")
                            else:
                                if field == 1: # Change Name
                                    name = input("\nNew name of Subject:")
                                    if len(name) > 0:
                                        old = settings['subjects'][subject_choice][0]
                                        settings['subjects'][subject_choice][0] = name
                                        log_tools.tprint("Renamed " + old + " to " + settings['subjects'][subject_choice][0])
                                    else:
                                        print("Name must be atleast 1 character.")
                                elif field == 2: # Change start date
                                    old = settings['subjects'][subject_choice][2]
                                    while(1):
                                        print("\nStart Date, format - dd/mm/yyyy. Current Date (" + settings['subjects'][subject_choice][2] + ")")
                                        newDate = get_date()
                                        new_date_obj = datetime.strptime(newDate, '%d/%m/%Y').date()
                                        end_date_obj = datetime.strptime(settings['subjects'][subject_choice][3], '%d/%m/%Y').date()
                                        if end_date_obj < new_date_obj:
                                            print("Start date must be before the end date (" + settings['subjects'][subject_choice][3] + ").")
                                        else:
                                            break
                                    change_date(subject_choice, 2, "start", (end_date_obj - new_date_obj).days + 1, new_date_obj, end_date_obj, newDate)
                                elif field == 3: # Change end date
                                    newDate = validate_end_date(settings['subjects'][subject_choice][2])
                                    start_date_obj = datetime.strptime(settings['subjects'][subject_choice][2], '%d/%m/%Y').date()
                                    new_date_obj = datetime.strptime(newDate, '%d/%m/%Y').date()
                                    change_date(subject_choice, 3, "end", (new_date_obj - start_date_obj).days + 1, start_date_obj, new_date_obj, newDate)
                                elif field == 4: # Add days
                                    s_day_options, length = setup_day_options(settings['subjects'][subject_choice][2], settings['subjects'][subject_choice][3])
                                    for day in settings['subjects'][subject_choice][1].keys():
                                        n = s_day_options.rfind(day_options[int(day)])
                                        s_day_options = s_day_options[:n] + s_day_options[n + 1:]
                                    print(s_day_options)
                                    settings['subjects'][subject_choice][1], dayList = create_days_dict(s_day_options, length, True, settings['subjects'][subject_choice][1])
                                    logOutput = str()
                                    for day in dayList:
                                        logOutput += weekDays[int(day)] + " " + str(settings['subjects'][subject_choice][1][day]) + " hour" + ("" if settings['subjects'][subject_choice][1][day] == 1 else "s") + ", "
                                    log_tools.tprint("Added to " + settings['subjects'][subject_choice][0] + " - " + logOutput[:-2] + ". (Not Saved)")
                                elif field == 5: # Remove a day
                                    print("\n--Remove a day from " + settings['subjects'][subject_choice][0] + '--')
                                    days = [*settings['subjects'][subject_choice][1].keys()]
                                    while(1):
                                        n = 0
                                        for day, hour in settings['subjects'][subject_choice][1].items():
                                            n += 1
                                            print(str(n) + ". " + weekDays[int(day)] + "\t Hour" + ("" if hour == 1 else "s") + ": " + str(hour))
                                        selector = input("Field to edit:").upper()
                                        if selector == 'X':
                                            break
                                        elif validate_selector(selector, n + 1):
                                            n = int(selector) - 1
                                            settings['subjects'][subject_choice][1].pop(days[n])
                                            log_tools.tprint("Removed " + weekDays[int(days[n])] + " from " + settings['subjects'][subject_choice][0] + ". (Not Saved)")
                                            break
    else:
        print("\nSubject list is empty.")
    return False  

def add_hourAndminute(subject, hour, minute):
    settings['subjects'][subject][4][0] += hour
    settings['subjects'][subject][4][1] += minute
    while settings['subjects'][subject][4][1] > 59:
        settings['subjects'][subject][4][1] -= 60
        settings['subjects'][subject][4][0] += 1

def add_to_tally():
    if "subjects" in settings and len(settings['subjects']) > 0:
        while(1):
            print("\n--TALLY MENU--")
            n = display_subject_list()
            selector = input("Subject to add tally to:").upper()
            if selector == "X":
                return False
            elif validate_selector(selector, n):
                selector = int(selector)
                while(1):
                    print(settings['subjects'][selector][0])
                    number = get_time_digit('hour')
                    old = settings['subjects'][selector][4][0]
                    break
                while(1):
                    minute = get_time_digit('minute')
                    old_minute = settings['subjects'][selector][4][1]
                    break
                add_hourAndminute(selector, number, minute)
                log_tools.tprint("Increased " + settings['subjects'][selector][0] + " from " + str(old) + 'h ' + str(minute) + "m to " + str(settings['subjects'][selector][4][0]) + 'h ' + str(settings['subjects'][selector][4][1]) + 'm.')
                return True
    print("Subject list in empty.")
    return False

while menu_mode != 'X':
    if menu_mode == 'm':
        menu_mode = main_menu()
    elif menu_mode == 'T':
        if add_to_tally() == True:
            save_json(settings, data_json_path, "Settings")
        menu_mode = 'm'
    elif menu_mode == 'A':
        if 'subjects' not in settings:
            settings['subjects'] = list()
        settings['subjects'].append(add_menu() + [[0,0]])
        save_json(settings, data_json_path, "Settings")
        menu_mode = 'm'
    elif menu_mode == 'R':
        if remove_menu() == True:
            save_json(settings, data_json_path, "Settings")
        menu_mode = 'm'
    elif menu_mode == 'E':
        if edit_menu() == True:
            save_json(settings, data_json_path, "Settings")
        menu_mode = 'm'
print("\nBye.")
