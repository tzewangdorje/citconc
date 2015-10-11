# encoding=utf8
import unittest
from concordance_parser.text import Text
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class TestText(unittest.TestCase):
    def test_make_regex(self):
        regex_string = "[A-ZÊ]+"  # test we can handle a unicode character here.
        reg = Text.make_regex(regex_string)
        self.assertTrue(isinstance(reg, re._pattern_type))

    def test_prepare_white_space(self):
        text_windows = "I am a test case.\r\nMy carriage returns  and\twhite \tspace shopuld be changed."
        text_linux = "I am a test case.\nMy carriage returns\n\nand\twhite   space shopuld be changed."
        success = u"I am a test case. My carriage returns and white space shopuld be changed."
        self.assertEqual(success, Text.prepare(text_windows))
        self.assertEqual(success, Text.prepare(text_linux))

    def test_prepare_punctuation_and_white_space(self):
        text = "I am a test case.My formatting is sloppy...I keep leaving out a space after a full stop,my email is python@coding.net."
        success = u"I am a test case. My formatting is sloppy... I keep leaving out a space after a full stop, my email is python@coding.net."
        self.assertEqual(success, Text.prepare(text))

    def test_get_citations_list(self):
        concordances = [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten"
        ]
        result_top = ["one", "two", "three"]
        result_bottom = ["seven", "eight", "nine", "ten"]
        self.assertEquals(result_top, Text.get_citations_list(concordances, "top", 3))
        self.assertEquals(result_bottom, Text.get_citations_list(concordances, "bottom", 4))
