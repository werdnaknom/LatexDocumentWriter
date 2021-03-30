import json
import typing as t
import configparser
from pathlib import Path
import re

from app.BaseWriterClass import BaseWriterClass

from app.printers import *


class TextProcessor():
    '''
    Takes in a text document and turns it into LaTeX
    '''
    VARIABLE_PATTERN: str = "\[ITEM-FIGURE[0-9]+\]|\[ITEM-LIST[0-9]+\]|\[" \
                            "ITEM-TABLE[0-9]+\]"
    text_printer: TextPrinter
    pattern_printers: t.List[Printer]
    cfg: configparser.ConfigParser

    def __init__(self):
        self.text_printer = TextPrinter()
        self.pattern_printers = [FigurePrinter(), TablePrinter(), ListPrinter()]

    def _find_variable_patterns(self, text: str):
        found_patterns = re.findall(pattern=self.VARIABLE_PATTERN, string=text)
        self.__validate_patterns(found_patterns)
        return found_patterns

    def __validate_patterns(self, patterns: t.List[str]):
        CHECK_PATTERN = "\[ITEM-"
        for pattern in patterns:
            found = re.findall(CHECK_PATTERN, pattern)
            #assert len(found) <= 1, f"{pattern} found is invalid! There
            # should only be one [ITEM] per line"

    def _find_text_to_print(self, text: str, pattern: str, start: int) -> t.Tuple[str, int]:
        text_end_loc = text.find(pattern)
        text_to_print = text[start:text_end_loc].strip()
        next_start = text_end_loc + len(pattern)
        return text_to_print, next_start

    def find_pattern_printer(self, pattern: str):
        for printer in self.pattern_printers:
            if printer.compare_pattern(pattern):
                return printer
        raise TypeError(f"Pattern {pattern} did not match any pattern printers!")

    def process_text(self, text: str) -> str:
        patterns = self._find_variable_patterns(text)

        if not patterns:  # There was no ITEMs to print
            yield self.text_printer, text
        else:
            start = 0
            for pattern in patterns:
                text_to_print, start = self._find_text_to_print(text=text, pattern=pattern, start=start)
                yield self.text_printer, text_to_print
                pattern_printer = self.find_pattern_printer(pattern)
                yield pattern_printer, pattern[6:-1] #[6:1] removes the [ITEM- and ] for the pattern
        return text
