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
            "regex_other_concordance": "{0}\\s*",
            "partitons": 1
        }
        conc = ConcordanceSentences(tokens=tokens, params=params)
        conc.load_text(text)
        success = [
            {
                "citation": u"This is my sentence one about my number one.",
                "word": "number",
                "citation_length":  len("This is my sentence one about my number one.")
            },
            {
                "citation": u"Now end with number.",
                "word": "number",
                "citation_length":  len("Now end with number.")
            },
            {
                "citation": u"Number at start too.",
                "word": "number",
                "citation_length":  len("Number at start too.")
            },
            {
                "citation": u"This is my number, it does have it also.",
                "word": "number",
                "citation_length":  len("This is number 5 that does have it also.")
            }
        ]
        offsets = conc.get_offsets("number")
        i = 0
        for concordance in conc.get_concordances("number", offsets):
            self.assertTrue(success[i] == concordance)
            i += 1

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
            "regex_other_concordance": "{0}\\s*",
            "partitons": 1
        }
        conc = ConcordanceSentences(tokens=tokens, params=params)
        conc.load_text(text)
        success = [
            {
                "citation": u"This is my sentence one about my number one. Now end with number.",
                "word": "number",
                "citation_length":  len("This is my sentence one about my number one. Now end with number.")
            },
            {
                "citation": u"This is my sentence one about my number one. Now end with number. Number at start too.",
                "word": "number",
                "citation_length":  len("This is my sentence one about my number one. Now end with number. Number at start too.")
            },
            {
                "citation": u"Now end with number. Number at start too. This is sentence four that does not have it.",
                "word": "number",
                "citation_length":  len("Now end with number. Number at start too. This is sentence four that does not have it.")
            },
            {
                "citation": u"This is sentence four that does not have it. This is my number, it does have it also.",
                "word": "number",
                "citation_length":  len("This is sentence four that does not have it. This is number 5 that does have it also.")
            }
        ]
        offsets = conc.get_offsets("number")
        i = 0
        for concordance in conc.get_concordances("number", offsets):
            self.assertTrue(success[i] == concordance)
            i += 1
