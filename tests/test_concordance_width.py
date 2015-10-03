# encoding=utf8
import nltk
import unittest
from concordance_parser.concordance import Concordance
from concordance_parser.concordance import ConcordanceWidth
from concordance_parser.text import Text
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class TestConcordanceWidth(unittest.TestCase):

    def test_get_concordances_one_match_exact(self):
        text = u"Aaa bbbb ccc dddd number eeee fff ggg. Aa bbb cccc ddd."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": " ccc dddd number eeee fff ",
                "word": "number",
                "citation_length":  len(" ccc dddd number eeee fff ")
            }
        ]
        self.assertTrue(success == concordances)

    def test_get_concordances_one_match_midword_rollback(self):
        text = u"Aaa bbbb cccc dddd number eeee ffff ggg. Aa bbb cccc ddd."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": " dddd number eeee ",
                "word": "number",
                "citation_length":  len(" dddd number eeee ")
            }
        ]
        self.assertTrue(success == concordances)

    def test_get_concordances_one_match_with_punctuation(self):
        text = u"Aaa bbbb, cc dddd number eeee fff. Aa bbb cccc ddd."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": ", cc dddd number eeee fff.",
                "word": "number",
                "citation_length":  len(", cc dddd number eeee fff.")
            }
        ]
        self.assertTrue(success == concordances)

    def test_get_concordances_one_match_with_punctuation2(self):
        text = u"Aaa bbbb-ccc dddd number eeee ff. Aa bbb cccc ddd."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": " dddd number eeee ff. ",
                "word": "number",
                "citation_length":  len(" dddd number eeee ff. ")
            }
        ]
        self.assertTrue(success == concordances)

    def test_get_concordances_one_match_unicode_midword_rollback(self):
        text = u"Aaa bbbb ÊÊÊÊ dddd number eeee ffff ggg. Aa bbb cccc ddd."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": " dddd number eeee ",
                "word": "number",
                "citation_length":  len(" dddd number eeee ")
            }
        ]
        self.assertTrue(success == concordances)

    def test_get_concordances_one_match_width_extends_beyond_end_of_text_right(self):
        text = u"Aaa bbbb ccc dddd number eeee."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": " ccc dddd number eeee.",
                "word": "number",
                "citation_length":  len(" ccc dddd number eeee.")
            }
        ]
        self.assertTrue(success == concordances)

    def test_get_concordances_one_match_width_extends_beyond_end_of_text_left(self):
        text = u"Dddd number eeee fff ggg. Aa bbb cccc ddd."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "width": 26,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceWidth(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": "Dddd number eeee fff ",
                "word": "number",
                "citation_length":  len("Dddd number eeee fff ")
            }
        ]
        self.assertTrue(success == concordances)
