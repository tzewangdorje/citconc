# encoding=utf8
import nltk
from io import open
import re
import random
import os
import pickle
import csv
import math
import cchardet


class AwesomeConfig(object):
    def __init__(self):
        self.corpus = ""
        self.word = ""
        self.encoding = "utf-16"
        self.output = "screen"
        self.filename = "output.txt"
        self.target = "linux"
        self.concordance_mode = "width"
        self.concordance_params = {}
        self.select_citation_method = "random"
        self.pickle_params = {}

class AwesomeConcordance(nltk.text.ConcordanceIndex):

    def __init__(self, tokens, key=lambda x:x, params={}):
        super(AwesomeConcordance, self).__init__(tokens, key=lambda x:x)
        self._params = params
        self._regex_is_char = re.compile(unicode(self._params["regex_is_char"]), re.UNICODE)
        self.text = u""

    def _get_escaped_token(self, token):
        for char in self._params["regex_escape_chars"]:
            char = unicode(char)
            token = token.replace(char, u"\\"+char)
            # http://www.cis.upenn.edu/~treebank/tokenization.html
            # Treebank tokens replace " with `` and '', we need to reverse this
            token = re.sub(u"''", u'"', token)
            token = re.sub(u"``", u'"', token)
        return token

    def _get_regex_pattern(self, word, tokens, left=True, match_depth=5):
        regex_pattern = u""
        last_token = len(tokens) - 1
        for i in range(0, len(tokens)):
            token = tokens[i]
            token_escaped = self._get_escaped_token(token)
            if i == 0 and not left:
                regex_pattern += unicode(self._params["regex_start_right_concordance"]).format(word, token_escaped)
            elif i == last_token and left:
                regex_pattern += unicode(self._params["regex_end_left_concordance"]).format(token_escaped, word)
            elif i == last_token and not left:
                regex_pattern += unicode(self._params["regex_end_right_concordance"]).format(token_escaped)
            else:
                regex_pattern += unicode(self._params["regex_other_concordance"]).format(token_escaped)
        return regex_pattern

    def _get_text(self, regex_pattern):
        regex_find = re.compile(regex_pattern, re.UNICODE)
        match = regex_find.search(self.text)
        if match:
            return match.group()
        else:
            return u""

    def _create_concordance(self, word, citation):
        return {
            "word": word,
            "citation": citation, 
            "citation_length": len(citation)
        }

    def get_concordances(self, word):
        # implement in child class!
        offsets = self.offsets(word)

        concordances = []
        if offsets:
            for i in offsets:
                token = self._tokens[i]
                citation = u""
                concordance = self._create_concordance(word, citation)
                concordances.append(concordance)
        return concordances

class AwesomeConcordanceSentences(AwesomeConcordance):

    def __init__(self, tokens, key=lambda x:x, params={}):
        super(AwesomeConcordanceSentences, self).__init__(tokens, key, params)

    def _is_end_sentence_token(self, token):
        return token in [u".", u"!", u"?"]

    def _get_tokens_until_start(self, i):
        keep_going = True
        tokens = []
        while keep_going:
            i -= 1
            token = self._tokens[i]
            if self._is_end_sentence_token(token):
                keep_going = False
            else:
                tokens.append(token)         
        tokens.reverse()
        return tokens

    def _get_tokens_until_end(self, i):
        keep_going = True
        tokens = []
        while keep_going:
            i += 1
            token = self._tokens[i]
            tokens.append(token)
            if self._is_end_sentence_token(token):
                keep_going = False
        return tokens

    def get_concordances(self, word):
        offsets = self.offsets(word)

        concordances = []
        if offsets:
            for i in offsets:
                token = self._tokens[i]

                tokens_left = self._get_tokens_until_start(i)
                tokens_right = self._get_tokens_until_end(i)

                regex_pattern_left = self._get_regex_pattern(token, tokens_left)
                regex_pattern_right = self._get_regex_pattern(token, tokens_right, left=False)
                
                match_text_left = self._get_text(regex_pattern_left)
                match_text_right = self._get_text(regex_pattern_right)

                slice_left = 0 - (len(token))
                slice_right = len(token)
                side_left = match_text_left[:slice_left]
                side_right = match_text_right[slice_right:]
                citation = side_left + token + side_right

                concordance = self._create_concordance(word, citation)
                concordances.append(concordance)
        return concordances

class AwesomeConcordanceWidth(AwesomeConcordance):

    def __init__(self, tokens, key=lambda x:x, params={}):
        super(AwesomeConcordanceWidth, self).__init__(tokens, key, params)

    def _get_boundary_left(self, i, context):
        boundary = i - context
        if boundary < 0:
            return 0
        else:
            return boundary 

    def _get_boundary_right(self, i, context):
        boundary = i + context
        boundary_max = len(self._tokens) - 1 
        if boundary > boundary_max:
            return boundary_max
        else:
            return boundary

    def _find_breakpoint_left(self, text, half_width):
        i = len(text) - half_width
        while i < len(text):
            char = unicode(text[i])
            if not self._regex_is_char.search(char):
                return i
            i += 1
        raise Exception("Could not locate boundary!")

    def _find_breakpoint_right(self, text, half_width):
        i = half_width - 1
        while i >= 0:
            char = unicode(text[i])
            if not self._regex_is_char.search(char):
                return i
            i -= 1
        raise Exception("Could not locate boundary!")

    def get_concordances(self, word):
        width = int(self._params["width"])
        half_width = (width - len(word)) // 2
        context = width // 4  # approx number of words of context
        offsets = self.offsets(word)
        concordances = []
        if offsets:
            for i in offsets:
                token = self._tokens[i]
                boundary_left = self._get_boundary_left(i, context)
                boundary_right = self._get_boundary_right(i, context)
                tokens_left = self._tokens[boundary_left:i]
                tokens_right = self._tokens[i+1:boundary_right]
                regex_pattern_left = self._get_regex_pattern(token, tokens_left)
                regex_pattern_right = self._get_regex_pattern(token, tokens_right, left=False)

                match_text_left = self._get_text(regex_pattern_left)
                match_text_right = self._get_text(regex_pattern_right)
                if match_text_right == u"" or match_text_right == u"":
                    raise Exception("Failed to extract original text with regular expression.")

                slice_left = 0 - (len(token))
                slice_right = len(token)
                side_left = match_text_left[:slice_left]
                side_right = match_text_right[slice_right:]

                break_point_left = self._find_breakpoint_left(side_left, half_width)
                break_point_right = self._find_breakpoint_right(side_right, half_width)

                citation = side_left[break_point_left:] + token + side_right[:break_point_right]

                concordance = self._create_concordance(word, citation)
                concordances.append(concordance)
        return concordances


class AwesomeParser(object):
    def __init__(self, action, config):
        if action not in ["concordance", "pickle", "report"]:
            raise Exception("Could not find a valid action to run.")
        self._action = action
        # TODO validate the config option passed at this point for valid options
        self._config = config
        self._word_lists = {}
        reg = unicode(self._config.pickle_params["regex_extract_list_word"])
        self._regex_extract_list_word = re.compile(reg, re.UNICODE)

    def run(self):
        if self._action == "concordance":
            self._action_concordance()
        elif self._action == "pickle":
            self._action_pickle()
        elif self._action == "report":
            self._action_report()
        else:
            raise Exception("Could not find a valid action to run.")

    def _get_citations_list(self, concordances):
        num_citations = int(self._config.citations)
        if self._config.select_citation_method == "random":
            selection = []
            limit = min(num_citations, len(concordances))
            for i in range(0,limit):
                selection.append(random.choice(concordances))
            return selection
        elif self._config.select_citation_method == "bottom":
            slice_index = 0 - num_citations
            return concordances[slice_index:]
        else:
            # assume must be top
            return concordances[0:num_citations]

    def _output_screen(self, concordances):
        for concordance in concordances:
            print concordance["citation"]

    def _output_file(self, concordances):
        if self._config.target == "windows":
            line_ending = u"\r\n"
        elif self._config.target == "linux":
            line_ending = u"\n"
        else:
            line_ending = os.linesep
        f = open(self._config.filename, encoding=self._config.encoding, mode="w")
        for concordance in concordances:
            f.write(unicode(concordance["citation"]) + line_ending)
        f.close()
        print "Output to file '{0}' complete.".format(self._config.filename)

    def _action_concordance(self):
        # 1) open and read file
        f = open(self._config.corpus, encoding=self._config.encoding)
        t = f.read()
        f.close()
        # remove all line endings / carriage returns - Linux and Windows
        t = t.replace('\n', ' ').replace('\r', '')
        # if there are any sequences of two or more white spaces, reduce them to a single space
        t = re.sub("\s\s+", " ", t)
        # 2) Get tokens
        tokens = nltk.word_tokenize(t)
        # 3) Create the correct kind of concordance index, pre-loaded with the required data/text
        key_func = lambda s:s.lower()
        if self._config.concordance_mode == "concordance-sentences":
            conc = AwesomeConcordanceSentences(tokens, key_func, self._config.concordance_params)
        else:
            conc = AwesomeConcordanceWidth(tokens, key_func, self._config.concordance_params)
        conc.text = t
        # 4) generate the concordances
        concordances = conc.get_concordances(self._config.word)
        concordances = self._get_citations_list(concordances)
        # 5) Output the concordance data, formatted appropriately
        if self._config.output == "file":
            self._output_file(concordances)
        else:
            self._output_screen(concordances)

    def _read_file(self, filepath):
        lines = []
        with open(filepath, encoding=self._config.encoding) as f:
            # line is a unicode string, i.e.: u'TEXT 0\n'
            for line in f:
                words = self._regex_extract_list_word.findall(line)
                if len(words)==1:
                    word = words[0].lower()
                    lines.append(word)
        return lines


    def _make_file_list(self):
        number_of_lists = int(self._config.pickle_params["number_of_lists"])
        file_list = {}
        for i in range(1, number_of_lists+1):
            index = unicode(i)
            filename = self._config.pickle_params["pattern"].format(index)
            file_list[index] = self._config.pickle_params["word_list_folder"] + "/" + filename
        return file_list

    def _action_pickle(self):
        word_lists = {}
        file_list = self._make_file_list()
        for (idx, f) in file_list.items():
            word_lists[idx] = self._read_file(f)
        with open("word_lists.pickled", 'wb') as handle:
            pickle.dump(word_lists, handle)

    def _get_difficulty(self, total, word_lists):
        word_number = int(math.ceil(total * float(self._config.pickle_params["difficulty_threshold"])))
        count = 0
        list_number = 0
        for words in word_lists:
            list_number += 1
            word_list = words.split()
            if (count+len(word_list)) >= word_number:
                return list_number
            else:
                count += len(word_list)

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

    def _get_report_headers(self, number_of_lists):
        scores = [u"Score" + unicode(i+1) for i in range(0, number_of_lists)]
        scores += [u"Other"]
        words = [u"Word" + unicode(i+1) for i in range(0, number_of_lists)]
        words += [u"Other"]
        return [u"Citation", u"Total", u"Difficulty"] + scores + words

    def _process_report_tokens(self, tokens):
        strip = lambda s:s.replace("'", "").replace("_", "")
        exclusions = self._config.pickle_params["exclusion_tokens"].split(",")
        return [strip(t) for t in tokens if t not in exclusions]

    def _make_line(self, parts):
        if self._config.target == "windows":
            line_ending = u"\r\n"
        elif self._config.target == "linux":
            line_ending = u"\n"
        else:
            line_ending = os.linesep
        parts[0] = parts[0].replace(u'"', u'""')
        parts[0] = u'"' + parts[0] + u'"'
        line = u",".join(parts)
        return unicode(line + line_ending)

    def _action_report(self):
        number_of_lists = int(self._config.pickle_params["number_of_lists"])
        regex_is_word = re.compile(unicode(self._config.pickle_params["regex_is_word"]), re.UNICODE)
        with open('word_lists.pickled', 'rb') as handle:
            self._word_lists = pickle.load(handle)
        f = open('report.csv', encoding=self._config.encoding, mode="w")
        with open(self._config.filename, encoding=self._config.encoding, mode="r") as concordances:
            headers = self._get_report_headers(number_of_lists)
            #writer.writerow(headers)
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
