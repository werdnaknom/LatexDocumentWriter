from pathlib import Path
import typing as t
import configparser
import json
import os
import re
from pylatex.base_classes import Environment, CommandBase, Arguments
from pylatex.package import Package
from pylatex import Document, Section, UnsafeCommand
from pylatex.utils import NoEscape

import pylatex

from text_proprocessor import TextPreProcessor


class SectionWriter():
    ITEM_PATTERN = '\[ITEM-.*\]'
    TABLE_PATTERN = '\[ITEM-TABLE[0-9]*\]'
    LIST_PATTERN = '\[ITEM-LIST[0-9]*\]'
    INTERNAL_PATTERN = '[INTERNAL]'
    VALIDATION_PATTERN = '[VALIDATION]'
    path: Path
    cfg: configparser.ConfigParser

    def __init__(self, section_header: str, section_path: Path, text_processor: TextPreProcessor):
        self.section_header = section_header
        self.path = section_path
        self.cfg = configparser.ConfigParser()
        self.cfg.optionxform = str
        self.cfg.read(self.path.joinpath("section_config.ini"))
        self.processor = text_processor

    def write(self, doc: pylatex.Document):
        with doc.create(pylatex.Section(self.section_header)):
            self.interpret_ini(doc=doc)

        doc.append(pylatex.NewPage())

    def _get_text(self) -> str:
        text = self.cfg.get("SECTION_TEXT", "text")
        return text

    def _return_tables_from_text(self, text: str) -> t.List[str]:
        ''' Searching the text string and returns a list that matches the pattern'''

        tables = re.findall(self.TABLE_PATTERN, text)
        return tables

    def _return_lists_from_text(self, text: str) -> t.List[str]:
        ''' Searching the text string and returns a list that matches the pattern'''

        tables = re.findall(self.LIST_PATTERN, text)
        return tables

    def __read_table_json(self, table_name: str) -> dict:
        table_name = table_name[6:-1]  # Removes [ITEM- and the trailing ]
        table_json_path = self.path.joinpath(f"{table_name}.json")
        with open(table_json_path, 'r') as jsonfile:
            table_json = json.loads(jsonfile.read())
        return table_json

    def __read_list_json(self, list_name: str) -> dict:
        list_name = list_name[6:-1]  # Removes [ITEM- and the trailing ]
        list_json_past = self.path.joinpath(f"{list_name}.json")
        with open(list_json_past, 'r') as jsonfile:
            list_json = json.loads(jsonfile.read())
        return list_json

    def _replace_lists_and_print(self, doc, text, lists):
        for list in lists:
            initial_text = text[:text.find(list)]
            doc.append(initial_text)
            # Add the list
            list_json = self.__read_list_json(list_name=list)
            with doc.create(pylatex.Itemize()) as itemized:
                for item in list_json['list_items']:
                    itemized.add_item(self.processor.process_text(item))

    def _replace_tables_and_print(self, doc, text, tables):
        for table in tables:
            # Write any text before the table
            initial_text = text[:text.find(table)]
            doc.append(initial_text)
            # Add the table
            table_json = self.__read_table_json(table_name=table)
            with doc.create(pylatex.Center()) as centered:
                num_headers = len(table_json["headers"])
                table_spec = table_json.get("table_spec", "|" + "X[c] | " * num_headers)
                table_spread = table_json.get("table_spread", "40pt")
                hlines = table_json.get("horizontal_lines", True)
                with centered.create(pylatex.Tabu(table_spec, spread=table_spread)) as data_table:
                    if hlines:
                        data_table.add_hline()
                    if num_headers > 0:
                        data_table.add_row(table_json["headers"], mapper=[pylatex.utils.bold])
                        data_table.add_hline()
                    for data in table_json["table_data"]:
                        for i, item in enumerate(data):
                            if isinstance(item, str):
                                data[i] = self.processor.process_text(item)
                        data_table.add_row(data)
                        if hlines:
                            data_table.add_hline()

    def interpret_ini(self, doc: pylatex.Document):
        raw_text = self._get_text()
        raw_text = self.processor.process_text(raw_text)
        tables = self._return_tables_from_text(text=raw_text)
        if tables:
            self._replace_tables_and_print(doc, raw_text, tables)
        lists = self._return_lists_from_text(text=raw_text)
        if lists:
            self._replace_lists_and_print(doc, raw_text, lists)
        doc.append(raw_text)

        for subsection, text in self.cfg["SUBSECTIONS"].items():
            with doc.create(pylatex.Subsection(subsection)):
                doc.append(self.processor.process_text(text))
