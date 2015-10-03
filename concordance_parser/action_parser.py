# encoding=utf8
import nltk
from io import open
import random
from action import Action
from text import Text
from concordance import Concordance


class ActionParser(Action):
    def run(self):
        regex_string = self._config.params["pickle_report"]["regex_extract_list_word"]
        self._regex_extract_list_word = Text.make_regex(regex_string)
        # 1) open and read file
        f = open(self._config.corpus, encoding=self._encoding)
        text = f.read()
        f.close()
        # 2) Prepare the text
        text = Text.prepare(text)
        # 3) Get tokens
        tokens = nltk.word_tokenize(text)
        # 4) Create the correct kind of concordance index, pre-loaded with the required data/text
        if self._config.params["general"]["concordance_mode"] == "concordance_sentences":
            from concordance import ConcordanceSentences
            params = self._config.params["concordance"].copy()
            params.update(self._config.params["concordance_sentences"])
            conc = ConcordanceSentences(
                tokens=tokens,
                key=Concordance.get_key_func(),
                params=params)
        else:
            from concordance import ConcordanceWidth
            params = self._config.params["concordance"].copy()
            params.update(self._config.params["concordance_width"])
            conc = ConcordanceWidth(
                tokens=tokens,
                key=Concordance.get_key_func(),
                params=params)
        conc.text = text
        # 4) generate the concordances
        concordances = conc.get_concordances(self._config.word)
        method = self._config.params["general"]["select_citation_method"]
        num_citations = int(self._config.params["general"]["citations"])
        citations_list = Text.get_citations_list(concordances, method, num_citations)
        # 5) Output the concordance data, formatted appropriately
        if self._config.params["general"]["output"] == "file":
            self._output_file(citations_list)
        else:
            self._output_screen(citations_list)

    def _output_file(self, concordances):
        if self._config.params["general"]["target"] == "windows":
            line_ending = u"\r\n"
        elif self._config.params["general"]["target"] == "linux":
            line_ending = u"\n"
        else:
            line_ending = os.linesep
        f = open(self._config.params["general"]["filename"], encoding=self._encoding, mode="w")
        for concordance in concordances:
            f.write(unicode(concordance["citation"]) + line_ending)
        f.close()
        print "Output to file '{0}' complete.".format(self._config.params["general"]["filename"])

    def _output_screen(self, concordances):
        for concordance in concordances:
            print concordance["citation"]
