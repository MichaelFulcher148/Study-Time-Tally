'''How I got this to work properly as an import-
Source: https://stackoverflow.com/questions/15959534/visibility-of-global-variables-in-imported-modules'''
from time import strftime, localtime
from code_tools import countup, countdown
## from sys import maxunicode
global run_date, script_id, html_output_file, log_file_name

def initialize(enable_html: bool = True) -> None:
    if enable_html:
        global html_output_file
        html_output_file = list()
    from os import path
    if not path.isdir(r'.\logs'):
        from os import makedirs
        makedirs('logs')
        tprint("Log directory created.\n")
        del makedirs
    del path
    ## move log name creation to here
##, non_bmp_map
##non_bmp_map = dict.fromkeys(range(0x10000, maxunicode + 1), 0xfffd)

'''Print a string with a timestamp'''
def tprint(*args: str, html: bool = False, **kwargs: str) -> None:
    if len(kwargs) == 0:
        kwargs = {'sep': '', 'end': '\n'}
    else:
        if 'sep' not in kwargs:
            kwargs['sep'] = ''
        if 'end' not in kwargs:
            kwargs['end'] = '\n'
    output = strftime('%d-%m-%Y %H:%M:%S', localtime()) + " - "
    for x in args:
        output += x
    add_to_txt_log(output + kwargs['end'])
    if html:
        add_to_html_log(output + kwargs['end'])
    print(output, sep=kwargs['sep'], end=kwargs['end'])

def add_to_txt_log(string: str, add_date: bool = False) -> None:
    if string[-1] != '\n':
        string += '\n'
    if not script_id or script_id == '':
        f_txt_log = open('logs\\log_{}.txt'.format(run_date), 'a', encoding="utf-8")
##        f_txt_log = open('logs\log_' + run_date + '.txt', 'ta', encoding="ascii", errors="surrogateescape")
    else:
        f_txt_log = open('logs\\{}_log_{}.txt'.format(script_id, run_date), 'a', encoding="utf-8")
##        f_txt_log = open('logs\\' + script_id + '_log_' + run_date + '.txt', 'ta', encoding="ascii", errors="surrogateescape")
    if add_date:
        string = "{} - {}".format(strftime('%d-%m-%Y %H:%M:%S', localtime()), string)
    try:
        f_txt_log.write(string)
##        f_txt_log.write(string.translate(non_bmp_map))
    except UnicodeEncodeError:
        print("Error with line writing line:\n" + string)
##        f_txt_log.write(string.translate(non_bmp_map) + '::except(UnicodeEncodeError) handled\n')
##        ##f_txt_log.write(str(string.encode('utf-8')) + '::except(UnicodeEncodeError) handled\n')
##        ##check open() method, since addition of new .translate to UnicodeEncodeError handler
    finally:
        f_txt_log.close()

'''Convert screen outputs from tprint into html for log file'''
def add_to_html_log(string: str) -> None:
    output = string.split('\n')
    list_length = len(output)
    superfluous = list()
    for x in countup(list_length):
        if len(output[x]) == 0:
            superfluous.append(x)
    superfluous_length = len(superfluous)
    for i in countdown(superfluous_length - 1):
        output.pop(superfluous[i])
    list_length -= superfluous_length
    for x in countup(list_length):
        html_output_file.append(output[x] + '<br>')
