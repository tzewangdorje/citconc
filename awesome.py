# encoding=utf8
"""Awesome Parser.

Usage:
  awesome.py concordance --corpus=<corpus> --word=<word> [--config=<config>] [--output=<output>]
  awesome.py pickle [--config=<config>]
  awesome.py report [--config=<config>] [--input=<input>] [--output=<output>] [--word=<word>]

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  --corpus=<corpuis>         The corpus of text to be read from file by the program.
  --word=<word>              The word to find concordances for.
  --config=<config>          Optional path to the json confile file [default: config.json].
  --input=<input>            Optional filename to use as the input for the report.
  --output=<output>          Optional filename to write the output to.

"""
from docopt import docopt
from concordance_parser.config import Config
import sys
reload(sys)
sys.setdefaultencoding('utf8')


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Awesome Parser 0.2')

    # a different location can be passed via the --config option
    config = Config(arguments)

    if arguments["concordance"] is True:
        from concordance_parser.action_parser import ActionParser
        action = ActionParser(config)
    elif arguments["pickle"] is True:
        from concordance_parser.action_pickle import ActionPickle
        action = ActionPickle(config)
    else:
        from concordance_parser.action_report import ActionReport
        action = ActionReport(config)
    action.run()
