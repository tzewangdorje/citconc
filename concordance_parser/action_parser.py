# encoding=utf8
import nltk
from io import open
import random
import os
from action import Action
from text import Text
from concordance import Concordance


class ActionParser(Action):
    def run(self):
        regex_string = self._config.params["pickle_report"]["regex_extract_list_word"]
        prep_file_name = self._config.params["general"]["prepfile"]
        errors_file_name = self._config.params["general"]["errorsfile"]
        self._regex_extract_list_word = Text.make_regex(regex_string)
        # 1) open files
        print "Reading corpus file..."
        corpus = open(self._config.corpus, mode="rb")
        errors = open(errors_file_name, mode="wb")
        print "...DONE."
        prepared = open(prep_file_name, mode="wb")
        # 2) read, line by line, and write to new "cleaned" file
        text = u""
        print "Preparing corpus..."
        lines_read = 0
        encoding_errors = 0
        for line in corpus:
            try:
                text = Text.prepare(line)
            except UnicodeDecodeError as e:
                encoding_errors += 1
                errors.write(line)
                line = line.decode('utf-8', 'ignore').encode('utf-8')
                text = Text.prepare(line)
            prepared.write(text)
            lines_read += 1
        corpus.close()
        prepared.close()
        print "...{0} lines read...".format(lines_read)
        print "...{0} encoding errors sent to {1}".format(
            encoding_errors,
            errors_file_name)
        print "...DONE."
        # 3) read prepared file and get tokens
        print "Reading prepared corpus..."
        with open(prep_file_name, 'rb') as prepared:
            text = prepared.read().decode("utf-8")
        os.remove(prep_file_name)
        print "...DONE."
        print "Starting tokenization..."
        tokens = nltk.word_tokenize(text)
        num_tokens = len(tokens)
        print "...{0} tokens found...".format(num_tokens)
        print "...DONE."
        # 4) Create the correct kind of concordance index, pre-loaded with the required data/text
        if self._config.params["general"]["concordance_mode"] == "concordance_sentences":
            from concordance import ConcordanceSentences
            params = self._config.params["concordance"].copy()
            params.update(self._config.params["concordance_sentences"])
            conc = ConcordanceSentences(
                tokens=tokens,
                params=params)
        else:
            from concordance import ConcordanceWidth
            params = self._config.params["concordance"].copy()
            params.update(self._config.params["concordance_width"])
            conc = ConcordanceWidth(
                tokens=tokens,
                params=params)
        num_partitions = int(self._config.params["general"]["partitions"])
        print "Partitioning text into {0}...".format(num_partitions)
        conc.load_text(text, num_partitions=num_partitions)
        print "...DONE."
        # 4) generate the concordances and output as citations
        print "Locating offsets..."
        offsets = conc.get_offsets(self._config.word)
        print "...{0} offsets found".format(len(offsets))
        print "...DONE."
        print "Generating concordances..."
        out_file_name = self._config.params["general"]["parser_output"]
        with open(out_file_name, mode="wb") as out_file:
            num_concordances = 0
            for concordance in conc.get_concordances(self._config.word, offsets):
                num_concordances += 1
                concordance["citation"] = self._config.params["general"]["citation_format"].format(concordance["citation"])
                out_file.write(unicode(concordance["citation"]) + unicode(os.linesep))
        print "...{0} concordances found".format(num_concordances)
        if conc.partition_misses:
            misses = 100 / ((num_concordances * 2) / conc.partition_misses)
        else:
            misses = 0.0
        print "...there were {0}% partition misses".format(misses)
        print "...DONE."
        print "Output to file '{0}' complete.".format(out_file_name)
