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

    def __init__(self, section_header: str, section_path: Path,
                 variable_dict: dict):
        self.section_header = section_header
        self.path = section_path.absolute()
        self.processor = TextProcessor()
        self.variables = variable_dict
        self.variables['cwd'] = self.path.as_posix()
        configuration_file = self.path.joinpath(CONFIGURATION_FILE_NAME)
        super(SectionWriter, self).__init__(
            configuration_file=str(configuration_file))

    def write(self, doc: pylatex.Document):
        #Write the section header and any section text
        with doc.create(pylatex.Section(self.section_header)):
            self.interpret_ini(doc=doc)

        #Write the subsection header and any subsection text
        try:
            subsections = dict(self.cfg["SUBSECTIONS"])
            for subsection_name, content in subsections.items():
                with doc.create(pylatex.Subsection(subsection_name)):
                    self.interpret_ini(doc=doc, text=content)
        except configparser.InterpolationSyntaxError:
            print(self.cfg["SUBSECTIONS"])
            print(self.section_header)
            raise

    def interpret_ini(self, doc: pylatex.Document, text:str = None):
        raw_init_text = self._get_section_text(text=text)
        for printer, item in self.processor.process_text(raw_init_text):
            if isinstance(printer, TextPrinter):
                printer.write(doc, item, variables=self.variables)
            else:
                loaded_contents = self.load_file(item)
                printer.write(doc, loaded_contents, variables=self.variables)

    def _get_section_text(self, text:str=None) -> str:
        if text == None:
            return self.cfg.get("SECTION_TEXT", "text")
        return text

    def load_file(self, filename: str):
        file = self.path.joinpath(filename).with_suffix(".json")
        with open(file, 'r') as json_file:
            read = json_file.read()
            try:
                json_contents = json.loads(read)
            except json.decoder.JSONDecodeError:
                print(read)
                raise
        return json_contents
