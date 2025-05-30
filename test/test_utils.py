import pytest
from time import time
from os import path, remove
from tools import log_tools

# From Windows Copilot - "pycharm: i have a function to test that has a logging function how can I deal with log file creation in my tests"
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    # Set up the logging configuration
    log_tools.script_id = "StudyTimeTally_test"
    log_tools.run_date = time.strftime('%d-%m-%Y', time.localtime())
    file_name = f'logs\\{log_tools.script_id}_log_{log_tools.run_date}.txt'
    log_tools.initialize(False)
    yield
    # Remove the log file after each test
    if path.exists(file_name):
        remove(file_name)
