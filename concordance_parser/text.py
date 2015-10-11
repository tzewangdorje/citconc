# encoding=utf8
import re
import random


class Text(object):
    _regex_contract_space = None
    _regex_insert_space1 = None
    _regex_insert_space2 = None

    @classmethod
    def make_regex(cls, regex_string):
        regex_unicode = unicode(regex_string)
        return re.compile(regex_string, re.UNICODE)

    @classmethod
    def prepare(cls, text):
        # only compile these regexes once
        if not cls._regex_contract_space:
            cls._regex_contract_space = cls.make_regex(u"\\s+")
        if not cls._regex_insert_space1:
            cls._regex_insert_space1 = cls.make_regex(u"([a-z\\.])\\.([A-Z])")
        if not cls._regex_insert_space2:
            cls._regex_insert_space2 = cls.make_regex(u"(\\w),(\\w)")
        # remove all line endings / carriage returns - Linux and Windows
        text = unicode(text)
        text = text.replace(u'\\n', u' ').replace(u'\\r', u'')
        # if there are any sequences of one or more white space, reduce them to a single space
        text = cls._regex_contract_space.sub(u" ", text)
        text = cls._regex_insert_space1.sub(u"\\1. \\2", text)
        text = cls._regex_insert_space2.sub(u"\\1, \\2", text)
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
