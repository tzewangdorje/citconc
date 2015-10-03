# encoding=utf8
import nltk
import unittest
from concordance_parser.concordance import Concordance
from concordance_parser.concordance import ConcordanceSentences
from concordance_parser.text import Text
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class TestConcordanceSentences(unittest.TestCase):

    def test_get_concordances_sentence_one(self):
        text = "This is my sentence one about  my number one.\nNow end with number. Number at start too.  This is sentence four that does not have it.\n\tThis is my number,it does have it also."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "sentences": 1,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceSentences(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": "This is my sentence one about my number one.",
                "word": "number",
                "citation_length":  len("This is my sentence one about my number one.")
            },
            {
                "citation": "Now end with number.",
                "word": "number",
                "citation_length":  len("Now end with number.")
            },
            {
                "citation": "Number at start too.",
                "word": "number",
                "citation_length":  len("Number at start too.")
            },
            {
                "citation": "This is my number, it does have it also.",
                "word": "number",
                "citation_length":  len("This is number 5 that does have it also.")
            }
        ]
        print success
        print concordances
        self.assertTrue(success == concordances)

    def test_get_concordances_sentence_three(self):
        text = "This is my sentence one about  my number one.\nNow end with number. Number at start too.  This is sentence four that does not have it.\n\tThis is my number,it does have it also."
        text = Text.prepare(text)
        tokens = nltk.word_tokenize(text)
        params = {
            "sentences": 3,
            "regex_escape_chars": "?.*$+()[]",
            "regex_is_char": "[\\w'\\-]",
            "regex_start_right_concordance": "{0}\\s*{1}\\s*",
            "regex_start_right_one_token_concordance": "{0}\\s*{1}",
            "regex_end_left_concordance": "{0}\\s*{1}",
            "regex_end_right_concordance": "{0}",
            "regex_other_concordance": "{0}\\s*"
        }
        conc = ConcordanceSentences(tokens=tokens, key=Concordance.get_key_func(), params=params)
        conc.text = text
        concordances = conc.get_concordances("number")
        success = [
            {
                "citation": "This is my sentence one about my number one. Now end with number.",
                "word": "number",
                "citation_length":  len("This is my sentence one about my number one. Now end with number.")
            },
            {
                "citation": "This is my sentence one about my number one. Now end with number. Number at start too.",
                "word": "number",
                "citation_length":  len("This is my sentence one about my number one. Now end with number. Number at start too.")
            },
            {
                "citation": "Now end with number. Number at start too. This is sentence four that does not have it.",
                "word": "number",
                "citation_length":  len("Now end with number. Number at start too. This is sentence four that does not have it.")
            },
            {
                "citation": "This is sentence four that does not have it. This is my number, it does have it also.",
                "word": "number",
                "citation_length":  len("This is sentence four that does not have it. This is number 5 that does have it also.")
            }
        ]
        print success
        print concordances
        self.assertTrue(success == concordances)
