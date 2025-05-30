import sys
from io import StringIO
import pytest
import unittest
from unittest.mock import patch
from study_time_tally import main_menu

class test_main_menu(unittest.TestCase):
    def open_main_menu(self):
        captured_text = StringIO()
        sys.stdout = captured_text
        main_menu()

if __name__ == '__main__':
    unittest.main()
