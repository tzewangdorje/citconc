# encoding=utf8
import re
from io import open
import os
import pickle
import nltk
import math
from action import Action


class ActionReport(Action):
    def run(self):
        self._word_lists = {}
        with open('word_lists.pickled', 'rb') as handle:
            self._word_lists = pickle.load(handle)
        f = open('report.csv', encoding=self._encoding, mode="w")
        filename = self._config.params["general"]["filename"]
        with open(filename, encoding=self._encoding, mode="r") as concordances:
            number_of_lists = int(self._config.params["pickle_report"]["number_of_lists"])
            regex_string = unicode(self._config.params["pickle_report"]["regex_is_word"])
            regex_is_word = re.compile(regex_string, re.UNICODE)
            headers = self._get_report_headers(number_of_lists)
            line = self._make_line(headers)
            f.write(line)
            for concordance in concordances:
                concordance = concordance.replace('\n', '').replace('\r', '')
                concordance = re.sub("\s\s+", " ", concordance)
                tokens = [token for token in nltk.word_tokenize(concordance) if regex_is_word.findall(token) != []]
                tokens = self._process_report_tokens(tokens)
                scores, words, total, difficulty = self._get_scores(tokens, number_of_lists)
                fields = [concordance, total, difficulty] + scores + words
                no_line_endings = [unicode(field).rstrip() for field in fields]
                line = self._make_line(no_line_endings)
                f.write(line)
        f.close()

    def _get_report_headers(self, number_of_lists):
        scores = [u"Score" + unicode(i+1) for i in range(0, number_of_lists)]
        scores += [u"Other"]
        words = [u"Word" + unicode(i+1) for i in range(0, number_of_lists)]
        words += [u"Other"]
        return [u"Citation", u"Total", u"Difficulty"] + scores + words

    def _make_line(self, parts):
        if self._config.params["general"]["target"] == "windows":
            line_ending = u"\r\n"
        elif self._config.params["general"]["target"] == "linux":
            line_ending = u"\n"
        else:
            line_ending = os.linesep
        parts[0] = parts[0].replace(u'"', u'""')
        parts[0] = u'"' + parts[0] + u'"'
        line = u",".join(parts)
        return unicode(line + line_ending)

    def _process_report_tokens(self, tokens):
        exclusions = self._config.params["pickle_report"]["exclusion_tokens"].split(",")
        strip = lambda s:s.replace("'", "").replace("_", "")
        return [strip(t) for t in tokens if t not in exclusions]

    def _get_scores(self, tokens, number_of_lists):
        scores = [0] * (number_of_lists+1)
        words = [u""] * (number_of_lists+1)
        for token in tokens:
            matched = False
            for i in range(0, number_of_lists):
                index = unicode(i + 1)
                lowered = token.lower()
                try:
                    lowered = unicode(lowered, errors='replace')
                except:
                    pass
                if lowered in self._word_lists[index]:
                    scores[i] += 1
                    words[i] += (lowered + u" ")
                    matched = True
                    break
            if not matched:
                # it wasn't in the word lists, so add it to "other"
                scores[number_of_lists] += 1
                words[number_of_lists] += (lowered + u" ")
        total = sum(scores)
        difficulty = self._get_difficulty(total, words)
        return scores, words, total, difficulty

    def _get_difficulty(self, total, word_lists):
        threshold_total = total * float(self._config.params["pickle_report"]["difficulty_threshold"])
        word_number = int(math.ceil(threshold_total))
        count = 0
        list_number = 0
        for words in word_lists:
            list_number += 1
            word_list = words.split()
            if (count + len(word_list)) >= word_number:
                return list_number
            else:
                count += len(word_list)
