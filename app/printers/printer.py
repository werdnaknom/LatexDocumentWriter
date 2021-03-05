import typing as t
from pathlib import Path

import pylatex


class Printer():
    PRINTER_TYPE: str
    pattern: str
    debug: bool = False

    def __init__(self, debug: bool = False):
        self.debug = debug

    def __repr__(self):
        return f"{self.PRINTER_TYPE} PRINTER"

    def compare_pattern(self, pattern_to_compare: str):
        return bool(self.PRINTER_TYPE in pattern_to_compare)

    def write(self, doc, item, variables: dict):
        raise NotImplementedError

    def _format_text(self, text: str, variables: dict):
        assert isinstance(text,
                          str), f"{self.__class__.__name__} is expecting text to write!"
        text_to_write = text.format(**variables)
        return text_to_write


class TextPrinter(Printer):
    PRINTER_TYPE: str = "TEXT"

    def write(self, doc, item, variables: dict):
        text = self._format_text(item, variables)
        if self.debug:
            return text
        else:
            doc.append(text)


class FigurePrinter(Printer):
    PRINTER_TYPE: str = "FIGURE"

    def write(self, doc, item, variables: dict):
        with doc.create(pylatex.Figure(position="h!")) as figure:
            filepath = item["filename"]
            if not Path(filepath).exists():
                filepath = variables["image404"]
            figure.add_image(filepath, width=item.get("width", "120px"))
            caption = item.get("caption", None)
            if caption:
                figure.add_caption(caption)


class TablePrinter(Printer):
    PRINTER_TYPE: str = "TABLE"

    def write(self, doc, item, variables: dict):
        with doc.create(pylatex.Center()) as centered:
            num_headers = len(item["headers"])
            table_spec = item.get("table_spec", "|" + "X[c] | " * num_headers)
            table_spread = item.get("table_spread", "40pt")
            hlines = item.get("horizontal_lines", True)
            with centered.create(pylatex.Tabu(table_spec,
                                              spread=table_spread)) as data_table:
                if hlines:
                    data_table.add_hline()
                if num_headers > 0:
                    data_table.add_row(item["headers"],
                                       mapper=[pylatex.utils.bold])
                    data_table.add_hline()
                for data_row in item["table_data"]:
                    print("O", data_row)
                    for i, data in enumerate(data_row):
                        if isinstance(data, str):
                            data_row[i] = self._format_text(data, variables=variables)
                    print("M", data_row)
                    data_table.add_row(data_row)
                    if hlines:
                        data_table.add_hline()


class ListPrinter(Printer):
    PRINTER_TYPE: str = "LIST"

    def write(self, doc, item, variables: dict):
        with doc.create(pylatex.Itemize()) as itemized:
            for ul in item['list_items']:
                itemized.add_item(ul.format(**variables))
