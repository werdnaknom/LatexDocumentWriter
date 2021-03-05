import pylatex
import configparser
import os
from pathlib import Path


class BaseWriterClass():
    '''
    Writes Latex Documents
    '''

    def __init__(self, configuration_file: str):
        self.cfg = configparser.ConfigParser()
        path = Path(configuration_file)
        assert path.exists(), "The configuration file does not exist!"
        self.cfg.read(configuration_file)
        self.cfg.optionxform = str

