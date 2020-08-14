def countdown(i):
    while i >= 0:
        yield i
        i -= 1

def countup(i):
    f = 0
    while f < i:
        yield f
        f += 1

def range_countup(start, end):
    while start < end:
        yield start
        start += 1

def trim(data):
    data_length = len(data)
    i = 0
    not_wanted_chars = ['\t', ' ', '\r']  # \n and \U+000B been tried
    while i < data_length:
        length = len(data[i])
        if length == 0:
            i += 1
            continue
        if data[i][0] in not_wanted_chars:
            not_wanted_char_count = 1
            x = 1
            while x < length:
                if data[i][x] in not_wanted_chars:
                    not_wanted_char_count += 1
                else:
                    break
                x += 1
            if not_wanted_char_count == length:
                data.pop(i)
                data_length -= 1
                continue
        if data[i][-1] == '\r':
            data[i] = data[i][:-1]
        i += 1
    return data

def remove_spaces(a_string):
    length = len(a_string)
    while length > 1 and a_string[0] == ' ':
        a_string = a_string[1:]
        length -= 1
    while length > 1 and a_string[-1] == ' ':
        a_string = a_string[:-1]
        length -= 1
    return a_string

def folder_name_char_check(a_string):
    non_valid_chars = '\\/?%*:|"<>.'
    for i in a_string:
        if i in non_valid_chars:
            print("{} Contains non valid character(s).\nFile and Folder names must not contain any of these characters {}.".format(a_string, non_valid_chars))
            return False
    return True
