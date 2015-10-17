# encoding=utf8
import json


class Config(object):
    def __init__(self, arguments):
        self.params = json.load(open(arguments["--config"]))
        self.corpus = arguments["--corpus"]
        self.word = arguments["--word"]
        if arguments['--input']:
            self.params["general"]["report_input"] = arguments["--input"]
        if arguments['--output'] and arguments["concordance"]:
            self.params["general"]["parser_output"] = arguments["--output"]
        elif arguments['--output'] and arguments["report"]:
            self.params["general"]["report_output"] = arguments["--output"]
