import typing as t
from pathlib import Path
import configparser
import json

import pylatex

from app.text_processor import TextProcessor
from app.printers.printer import *
from app.BaseWriterClass import BaseWriterClass

CONFIGURATION_FILE_NAME = "section_config.ini"


class SectionWriter(BaseWriterClass):

    def __init__(self, section_header: str, section_path: Path, variable_dict: dict):
        self.section_header = section_header
        self.path = section_path
        self.processor = TextProcessor()
        self.variables = variable_dict
        configuration_file = self.path.joinpath(CONFIGURATION_FILE_NAME)
        super(SectionWriter, self).__init__(configuration_file=str(configuration_file))

    def write(self, doc: pylatex.Document):
        with doc.create(pylatex.Section(self.section_header)):
            self.interpret_ini(doc=doc)

    def interpret_ini(self, doc: pylatex.Document):
        raw_init_text = self._get_section_text()
        for printer, item in self.processor.process_text(raw_init_text):
            if isinstance(printer, TextPrinter):
                printer.write(doc, item, variables=self.variables)
            else:
                loaded_contents = self.load_file(item)
                printer.write(doc, loaded_contents, variables=self.variables)

    def _get_section_text(self) -> str:
        text = self.cfg.get("SECTION_TEXT", "text")
        return text

    def load_file(self, filename: str):
        file = self.path.joinpath(filename).with_suffix(".json")
        with open(file, 'r') as json_file:
            json_contents = json.loads(json_file.read())
        return json_contents
