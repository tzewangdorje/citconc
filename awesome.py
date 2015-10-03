# encoding=utf8
"""Awesome Parser.

Usage:
  parser.py concordance --corpus=<corpus> --word=<word> [--output=<output>] [--config=<config>] [--citations=<citations>] [--filename=<filename>]
  parser.py pickle [--config=<config>]
  parser.py report [--filename=<filename>]

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  --corpus=<corpuis>         The corpus of text to be read from file by the program.
  --word=<word>              The word to find concordances for.
  --citations=<citations>    Number of lines of citations to report back [default: 100].
  --encoding=<encoding>      The encoding of the input corpus file [default: latin-1].
  --target=<target>          Valid options are windows or linux [default: linux].
  --config=<config>          Optional path to the json confile file [default: config.json].
  --output=<ouput>           Output format - file, stdout - other options could be added [default: stdout].
  --filename=<filename>      Optional filename to write output to [default: output.txt].
  --pattern=<pattern>


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
