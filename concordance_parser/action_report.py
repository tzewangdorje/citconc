# encoding=utf8
import re
from io import open
import os
import pickle
import nltk
import math
import random
from action import Action
from report import Report


class ActionReport(Action):
    def run(self):
        self._word_lists = {}
        out_file_name = self._config.params["general"]["report_output"]
        report = open(out_file_name, mode="wb")
        pickle_file_name = self._config.params["pickle_report"]["pickle_file_name"]
        difficulty_threshold = self._config.params["pickle_report"]["difficulty_threshold"]
        print "Reading pickle file..."
        with open(pickle_file_name, 'rb') as handle:
            self._word_lists = pickle.load(handle)
        print "...DONE"
        in_file_name = self._config.params["general"]["report_input"]
        number_of_lists = int(self._config.params["pickle_report"]["number_of_lists"])
        regex_string = unicode(self._config.params["pickle_report"]["regex_is_word"])
        regex_is_word = re.compile(regex_string, re.UNICODE)
        headers = self._get_report_headers(number_of_lists)
        line = self._make_line(headers)
        report.write(line)
        concordances = []
        print "Reading citations..."
        in_file = open(in_file_name, mode="rb")
        for line in in_file:
            concordances.append(line.decode("utf-8"))
        in_file.close()
        print "...DONE"
        concordances = self._get_citations_list(concordances)
        print "Concordance processing started..."
        for concordance in concordances:
            concordance = concordance.replace('\n', '').replace('\r', '')
            concordance = re.sub("\s\s+", " ", concordance)
            cleaned = concordance.replace(u"\u2018", "``")
            cleaned = cleaned.replace(u"\u2019", "''")
            tokens = [token for token in nltk.word_tokenize(cleaned) if regex_is_word.findall(token) != []]
            scores, words, total, difficulty = Report.get_scores(
                tokens,
                number_of_lists,
                self._word_lists,
                difficulty_threshold)
            fields = [concordance, total, difficulty] + scores + words
            no_line_endings = [unicode(field).rstrip() for field in fields]
            line = self._make_line(no_line_endings)
            report.write(line)
        report.close()
        print "...DONE"

    def _get_citations_list(self, concordances):
        method = self._config.params["general"]["select_citation_method"]
        if method == "all":
            return concordances
        num_citations = int(self._config.params["general"]["citations"])
        if method == "random":
            selection = []
            limit = min(num_citations, len(concordances))
            for i in range(0, limit):
                selection.append(random.choice(concordances))
            return selection
        elif method == "bottom":
            slice_index = 0 - num_citations
            return concordances[slice_index:]
        else:
            # assume must be top
            return concordances[0:num_citations]

    def _get_report_headers(self, number_of_lists):
        scores = [u"Score" + unicode(i+1) for i in range(0, number_of_lists)]
        scores += [u"Other"]
        scores += [u"Proper Nouns"]
        words = [u"Word" + unicode(i+1) for i in range(0, number_of_lists)]
        words += [u"Other"]
        words += [u"Proper Nouns"]
        return [u"Citation", u"Total", u"Difficulty"] + scores + words

    def _make_line(self, parts):
        parts[0] = parts[0].replace(u'"', u'""')
        parts[0] = u'"' + parts[0] + u'"'
        line = u",".join(parts)
        return unicode(line + os.linesep)
