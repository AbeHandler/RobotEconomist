import json


class Config(object):

    '''
    What labels will you use for the various variables?
    '''

    def __init__(self, config_file: str = "config/config.json") -> None:
        with open(config_file, "r") as inf:
            config = json.load(inf)
        self.instrument = config["vertexes"]["instrument"]
        self.outcome = config["vertexes"]["outcome"]
        self.regressor = config["vertexes"]["regressor"]
        self.instruments_label = config["edges"]["instruments_label"]
        self.affects_label = config["edges"]["affects_label"]
