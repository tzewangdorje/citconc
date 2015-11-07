# encoding=utf8
import math
import nltk
import re


class Report(object):

    @classmethod
    def _parse_token(cls, token):
        # convert to unicode
        try:
            token = unicode(token, errors='replace')
        except TypeError:
            pass  # catch and move on if we get: "TypeError: decoding Unicode is not supported"
        return token, token.lower()

    @classmethod
    def _get_params(cls, config):
        number_of_lists = int(config.params["pickle_report"]["number_of_lists"])
        difficulty_threshold = config.params["pickle_report"]["difficulty_threshold"]
        regex_string = unicode(config.params["pickle_report"]["regex_is_word"])
        regex_is_word = re.compile(regex_string, re.UNICODE)
        return number_of_lists, difficulty_threshold, regex_is_word

    @classmethod
    def _clean(cls, concordance):
        concordance = concordance.replace('\n', '').replace('\r', '')
        concordance = re.sub("\s\s+", " ", concordance)
        concordance = concordance.replace(u"\u2018", '"')
        return concordance.replace(u"\u2019", '"')

    @classmethod
    def get_scores(cls, concordance, word_lists, config):
        number_of_lists, difficulty_threshold, regex_is_word = cls._get_params(config)
        concordance = cls._clean(concordance)
        # split hyphenated tokens into two
        tokens = [part for token in nltk.word_tokenize(concordance) for part in token.split("-") if part]
        # remove non-word tokens
        tokens = [token for token in tokens if regex_is_word.findall(token) != []]
        scores = [0] * (number_of_lists + 2)  # +2 is extra "other" + "proper noun" columns
        words = [u""] * (number_of_lists + 2)
        for token in tokens:
            proper_noun = False
            matched = False
            token, lowered = cls._parse_token(token)
            # check for numeric difficulty one
            if token.isdecimal():
                    scores[0] += 1
                    words[0] += (token + u" ")
                    matched = True
                    continue
            # check for proper nouns
            if lowered in word_lists[u"proper"]:
                proper_noun = True
                if token.istitle():  # Upper case proper noun can be handled right away
                    scores[number_of_lists + 1] += 1
                    words[number_of_lists + 1] += (lowered + u" ")
                    continue
            # look for a match in one of the word lists
            for i in range(0, number_of_lists):
                index = unicode(i + 1)
                if lowered in word_lists[index]:  # lower case word list match
                    scores[i] += 1
                    words[i] += (lowered + u" ")
                    matched = True
                    break
            if not matched and (proper_noun or token.istitle()):
                scores[number_of_lists + 1] += 1
                words[number_of_lists + 1] += (lowered + u" ")
            elif not matched:
                # it wasn't in the word lists, it's not a proper noun, so add it to "other"
                scores[number_of_lists] += 1
                words[number_of_lists] += (lowered + u" ")
        total = sum(scores[:-1])
        difficulty = cls._get_difficulty(total, words[:-1], difficulty_threshold)
        return scores, words, total, difficulty

    @classmethod
    def _get_difficulty(cls, total, word_lists, difficulty_threshold):
        threshold_total = total * float(difficulty_threshold)
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
