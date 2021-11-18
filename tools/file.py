import _pickle as pickle
import json
from os import path, remove as file_del, rename as file_rename
from tools import log_tools

def pickle_objects(filename: str, a_list: list) -> None:
    json_path_old = filename[:-3] + 'old'
    json_path_old2 = json_path_old + '2'
    if path.isfile(filename):
        if path.isfile(json_path_old):
            if path.isfile(json_path_old2):
                file_del(json_path_old2)
            file_rename(json_path_old, json_path_old2)
        file_rename(filename, json_path_old)
    with open(filename, 'wb') as f:
        for i in a_list:
            pickle.dump(i, f, -1)
    log_tools.tprint(f'{filename} saved.')

def get_pickled_objects(filename) -> None:
    with open(filename, 'rb') as f:
        while 1:
            try:
                yield pickle.load(f)
            except EOFError:
                break

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