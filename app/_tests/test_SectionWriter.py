from unittest import TestCase,mock
from pathlib import Path
import os

import pylatex

from app.section_writer import SectionWriter


class TestSectionWriter(TestCase):

    def setUp(self) -> None:
        cwd = os.getcwd()
        variables = {
            "product_name": "THIS IS A PRODUCT NAME VARIABLE",
            "FILENOTFOUND": "image_404.png",
            "prd_revision": 1,
            "port_interface_speed": 10,
            "interfaces": "bob",
            "form_factor_specification": "PCIE",
            "port_interface_spec": "10",
            "silicon_datasheet": 101,
            "image404": "../../images/image_404.png"
        }
        self.writer = SectionWriter(section_header="Test", section_path=Path(cwd).joinpath("test_files"),
                                    variable_dict=variables)

    def test_load_file_list(self):
        file = self.writer.load_file(filename="LIST1")
        self.assertIsInstance(file, dict)
        self.assertIsInstance(file['list_items'], list)

    def test_load_file_figure(self):
        file = self.writer.load_file(filename="FIGURE1")
        self.assertIsInstance(file, dict)
        self.assertEqual(file["filename"], "Smile.jpg")
        self.assertEqual(file["caption"], "Revision History")

    def test_load_file_nonexistant_figure(self):
        with self.assertRaises(FileNotFoundError):
            file = self.writer.load_file(filename="FIGURE999")
        #self.assertIsInstance(file, Path)
        #self.assertEqual(file.name, "image_404.png")

    def test_load_file_table(self):
        file = self.writer.load_file(filename="TABLE1")
        self.assertIsInstance(file, dict)
        self.assertEqual(len(file.keys()), 3)

    def test_interpret_ini(self):
        ini_text = """This is text. 
                   This is a List [ITEM-LIST1]
                   This is a table [ITEM-TABLE1]
                   And finally, a figure [ITEM-FIGURE1]"""

        output = Path(os.getcwd()).joinpath("TestPDF")
        doc = pylatex.Document()
        with mock.patch.object(self.writer, '_get_section_text', return_value=ini_text):
            self.writer.interpret_ini(doc=doc)
        doc.generate_pdf(filepath=output, clean_tex=True)
