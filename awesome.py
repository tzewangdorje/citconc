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
  --config=<config>          Optional path to the config.ini file [default: config.ini].
  --output=<ouput>           Output format - file, stdout - other options could be added [default: stdout].
  --filename=<filename>      Optional filename to write output to [default: output.txt].
  --pattern=<pattern>


"""
from docopt import docopt
from ConfigParser import ConfigParser
from awesome_parser import AwesomeParser
from awesome_parser import AwesomeConfig

if __name__ == '__main__':    
    arguments = docopt(__doc__, version='Awesome Parser 0.1')
    # TODO - parse a standard .ini config file

    # default config file is config.ini relative to the parser.py file
    # a different location can be passed via the --config option 
    config_parser = ConfigParser()
    config_parser.read(arguments["--config"])
    config_general = dict(config_parser.items("general"))
    concordance_mode = config_general["concordance-mode"]
    concordance_mode_params = dict(config_parser.items(concordance_mode))
    pickle_params = dict(config_parser.items("pickle-report"))

    # TODO - create Config object here to pass to AwesomeParser
    # This will decouple of Docopt and allow us to use this code in other contexts, such as a wb application etc
    config = AwesomeConfig()
    config.citations = config_general["citations"]
    config.encoding = config_general["encoding"]
    config.output = config_general["output"]
    config.target = config_general["target"]
    config.select_citation_method = config_general["select-citation-method"]
    config.concordance_mode = concordance_mode
    config.concordance_params = concordance_mode_params
    config.pickle_params = pickle_params

    # config options are set in file first and can then be overriden from the command line 
    # TODO override config with anything set on command line
    config.corpus = arguments["--corpus"]
    config.word = arguments["--word"]
    config.citations = arguments["--citations"]
    if arguments.has_key('--filename'):
        config.filename = arguments["--filename"]

    if arguments["concordance"] == True:
        action = "concordance"
    elif arguments["pickle"] == True:
        action = "pickle"
    else:
        action = "report"

    ap = AwesomeParser(action, config)
    ap.run()
