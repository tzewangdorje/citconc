# encoding=utf8
from action import Action


class ActionPickle(Action):
    def run(self):
        regex_string = unicode(self._config.params["pickle-report"]["regex_extract_list_word"])
        self._regex_extract_list_word = re.compile(regex_string, re.UNICODE)
        word_lists = {}
        file_list = self._make_file_list()
        for (idx, f) in file_list.items():
            word_lists[idx] = self._read_file(f)
        with open("word_lists.pickled", 'wb') as handle:
            pickle.dump(word_lists, handle)

    def _make_file_list(self):
        number_of_lists = int(self._config.params["pickle-report"]["number_of_lists"])
        file_list = {}
        for i in range(1, number_of_lists+1):
            index = unicode(i)
            filename = self._config.params["pickle-report"]["pattern"].format(index)
            file_list[index] = self._config.params["pickle-report"]["word_list_folder"] + "/" + filename
        return file_list

    def _read_file(self, filepath):
        lines = []
        with open(filepath, encoding=self._config.encoding) as f:
            # line is a unicode string, i.e.: u'TEXT 0\n'
            for line in f:
                words = self._regex_extract_list_word.findall(line)
                if len(words) == 1:
                    word = words[0].lower()
                    lines.append(word)
        return lines
