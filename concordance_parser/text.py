# encoding=utf8
import re
import random


class Text(object):
    @classmethod
    def make_regex(cls, regex_string):
        regex_unicode = unicode(regex_string)
        return re.compile(regex_string, re.UNICODE)

    @classmethod
    def prepare(cls, text):
        # remove all line endings / carriage returns - Linux and Windows
        text = text.replace('\n', ' ').replace('\r', '')
        # if there are any sequences of one or more white space, reduce them to a single space
        text = re.sub("\s+", " ", text)
        text = re.sub(r"([a-z\.])\.([A-Z])", r"\1. \2", text)
        text = re.sub(r"(\w),(\w)", r"\1, \2", text)
        return text

    @classmethod
    def get_citations_list(cls, concordances, method, num_citations):
        if method == "random":
            selection = []
            limit = min(num_citations, len(concordances))
            for i in range(0, limit):
                selection.append(random.choice(concordances))
            return selection
        elif method == "bottom":
            slice_index = 0 - num_citations
            return concordances[slice_index:]
        else:  # assume must be top
            return concordances[0:num_citations]
