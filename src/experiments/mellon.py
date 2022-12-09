import pandas as pd  # type: ignore


class AppendixA(object):

    def __init__(self, filename="data/AppendixA.csv") -> None:
        self.df = pd.read_csv(filename)
        self.papers = self.df.paperid.to_list()

    def get_X(self, paperid):
        paperid = paperid.replace("data/rain/", "")
        return self.df.query("paperid=='{}'".format(paperid))["X"].to_list()[0]

    def get_Y(self, paperid):
        paperid = paperid.replace("data/rain/", "")
        return self.df.query("paperid=='{}'".format(paperid))["Y"].to_list()[0]
