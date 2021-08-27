import twint
import pandas
import openpyxl
import tabulate
import os
import datetime as dt
import time


class TempBool(int):
    def __call__(self):
        print("Called.")

    def __await__(self):
        print("awaited.")


class twdf(pandas.DataFrame):
    def __call__(self):
        print("Called.")

    def __await__(self):
        print("awaited.")

    def to_discord(self):
        result = self.to_markdown()
        return result

    @property
    def xlslfy(self):
        basedir = os.getcwd()
        xl_dlr = "data/Excel"
        xl_dlr = os.path.join(basedir, xl_dlr)
        now = dt.datetime.now()
        filename = '.'.join([now.strftime("%Y_%m_%d_%H_%M"), "xlsx"])
        f_dir = os.path.join(xl_dlr, filename)
        self.to_excel(f_dir)
        return f_dir


class TempClass(str):
    def __call__(self):
        print("Called.")

    def __await__(self):
        print("awaited.")


class TWcfg(twint.Config):
    def __init__(self):
        self.Limit = 10
        self.Pandas = True

    def cfg(self, **kwargs):
        for key, value in kwargs.items():
            if key == "Limit":
                self.Limit = value
            elif key == "Search":
                self.Search = value

    def keyword(self, word) -> TempBool:
        self.Search = word
        result = TempBool(1)
        return result

    def output(self, word) -> twdf:
        self.Search = word
        twint.run.Search(self)
        result = twdf(twint.storage.panda.Tweets_df)
        return result

    def run(self) -> twdf:
        twint.run.Search(self)
        result = twdf(twint.storage.panda.Tweets_df)
        return result


if __name__ == "__main__":
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', None)
    pandas.set_option('display.max_colwidth', -1)
    pandas.set_option('display.max_rows', None)
