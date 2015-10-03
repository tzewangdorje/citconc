class Action(object):
    def __init__(self, config):
        self._config = config
        self._encoding = self._config.params["general"]["encoding"]
