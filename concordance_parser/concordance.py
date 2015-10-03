# encoding=utf8
import nltk
import re
from collections import defaultdict


class Concordance(nltk.text.ConcordanceIndex):

    def __init__(self, tokens, key=lambda x:x, params={}):
        self._tokens = tokens
        self._key = key
        self._offsets = defaultdict(list)
        for index, word in enumerate(tokens):
            word = self._key(word)
            self._offsets[word].append(index)
        self._params = params
        self._regex_is_char = re.compile(unicode(self._params["regex_is_char"]), re.UNICODE)
        self.text = u""

    @classmethod
    def get_key_func(cls):
        return lambda s:s.lower()

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
            if len(tokens) == 1 and not left:
                regex_pattern += unicode(
                    self._params["regex_start_right_one_token_concordance"]).format(word, token_escaped)
            elif i == 0 and not left:
                regex_pattern += unicode(
                    self._params["regex_start_right_concordance"]).format(word, token_escaped)
            elif i == last_token and left:
                regex_pattern += unicode(
                    self._params["regex_end_left_concordance"]).format(token_escaped, word)
            elif i == last_token and not left:
                regex_pattern += unicode(
                    self._params["regex_end_right_concordance"]).format(token_escaped)
            else:
                regex_pattern += unicode(
                    self._params["regex_other_concordance"]).format(token_escaped)
        return regex_pattern

    def _get_text(self, regex_pattern):
        regex_find = re.compile(regex_pattern, re.UNICODE)
        match = regex_find.search(unicode(self.text))
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


class ConcordanceSentences(Concordance):

    def __init__(self, tokens, key=lambda x:x, params={}):
        super(ConcordanceSentences, self).__init__(tokens=tokens, key=key, params=params)

    def _is_end_sentence_token(self, token):
        return token in [u".", u"!", u"?"]

    def _get_tokens_until_start(self, i, extra_sentences=0):
        keep_going = True
        sentence_count = 0
        tokens = []
        while keep_going:
            i -= 1
            if i < 0:
                break
            token = self._tokens[i]
            if self._is_end_sentence_token(token) and sentence_count < extra_sentences:
                sentence_count += 1
                tokens.append(token)
            elif self._is_end_sentence_token(token):
                keep_going = False
            else:
                tokens.append(token)
        tokens.reverse()
        return tokens

    def _get_tokens_until_end(self, i, extra_sentences=0):
        keep_going = True
        sentence_count = 0
        tokens = []
        while keep_going:
            i += 1
            if i >= len(self._tokens):
                break
            token = self._tokens[i]
            tokens.append(token)
            if self._is_end_sentence_token(token) and sentence_count < extra_sentences:
                sentence_count += 1
            elif self._is_end_sentence_token(token):
                keep_going = False
        return tokens

    def _get_side_sentences(self):
        return (self._params["sentences"] - 1) / 2

    def get_concordances(self, word):
        offsets = self.offsets(word)
        extra_sentences = self._get_side_sentences()

        concordances = []
        if offsets:
            for i in offsets:
                token = self._tokens[i]

                tokens_left = self._get_tokens_until_start(i, extra_sentences)
                tokens_right = self._get_tokens_until_end(i, extra_sentences)
                regex_pattern_left = self._get_regex_pattern(token, tokens_left, left=True)
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


class ConcordanceWidth(Concordance):

    def __init__(self, tokens, key=lambda x:x, params={}):
        super(ConcordanceWidth, self).__init__(tokens, key, params)

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
            if i < 0:
                return 0
            char = unicode(text[i])
            if not self._regex_is_char.search(char):
                return i
            i += 1
        raise Exception("Could not locate boundary!")

    def _find_breakpoint_right(self, text, half_width):
        i = half_width - 1
        while i >= 0:
            if i >= len(text):
                return len(text)
            char = unicode(text[i])
            if not self._regex_is_char.search(char):
                return i + 1
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
                tokens_right = self._tokens[i+1:boundary_right+1]
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
