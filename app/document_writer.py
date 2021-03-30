import pylatex
import configparser
import os
import json

from pathlib import Path

from app.section_writer import SectionWriter
from app.BaseWriterClass import BaseWriterClass


class DocumentWriter(BaseWriterClass):

    def __init__(self, configuration_file: str):
        super(DocumentWriter, self).__init__(configuration_file=configuration_file)
        self.project_variables = self._read_project_variables()
        self.doc = self._create_document()

    def _read_project_variables(self) -> dict:
        project_json_path = self.cfg.get("CONFIGURATION", "project_json")
        with open(project_json_path, 'r') as json_file:
            try:
                read = json_file.read()
                json_contents = json.loads(read)
            except:
                print(read)
                raise
        return json_contents

    def _create_document(self) -> pylatex.Document:
        geometry_options = dict(self.cfg["DOCUMENT_GEOMETRY"])
        geometry_options["includeheadfoot"] = True
        doc = pylatex.Document(geometry_options=geometry_options)

        self._generate_preamble(doc)
        self._generate_title_page(doc)
        self._generate_table_of_contents(doc)

        return doc

    def _generate_preamble(self, doc: pylatex.Document):
        header_footer = self._generate_header_footer()
        doc.preamble.append(header_footer)
        doc.change_document_style("headerfooter")

    def _generate_title_page(self, doc: pylatex.Document):
        doc.preamble.append(pylatex.Command('title', self.cfg.get("TITLEPAGE", "title")))
        doc.preamble.append(pylatex.Command('author', self.cfg.get("GROUP", "design_group")))
        doc.preamble.append(pylatex.Command('date', pylatex.NoEscape(r'\today')))
        doc.append(pylatex.NoEscape(r'\maketitle'))
        doc.append(pylatex.NewPage())

    def _generate_table_of_contents(self, doc: pylatex.Document):
        doc.append(pylatex.NoEscape(r'\tableofcontents'))
        doc.append(pylatex.basic.NewPage())

    def _generate_header_footer(self) -> pylatex.PageStyle:
        pagestyle = pylatex.PageStyle("headerfooter")

        ''' LOGO ON LEFT SIDE '''
        with pagestyle.create(pylatex.Head("L")) as header_left:
            with header_left.create(
                    pylatex.MiniPage(width=pylatex.NoEscape(r"0.49\textwidth"), pos="c")) as logo_wrapper:
                logo_path_str = self._get_image_path(image_filename=self.cfg.get("CONFIGURATION", "logo"))
                logo_wrapper.append(
                    pylatex.StandAloneGraphic(image_options=f"height={self.cfg.get('DOCUMENT_GEOMETRY', 'head')}",
                                              filename=logo_path_str))
                # logo_wrapper.append(pylatex.NoEscape(r"$\vert$"))

        ''' PRODUCT TEXT IN CENTER '''
        with pagestyle.create(pylatex.Head("C")) as header_center:
            with header_center.create(
                    pylatex.MiniPage(width=pylatex.NoEscape(r"0.49\textwidth"), pos="c")) as text_wrapper:
                text_wrapper.append("NPO Hardware\n")
                text_wrapper.append("Dayton Peak Dual Port\n")
                text_wrapper.append("HLD")

        ''' FOOTER PAGE LEFT '''
        with pagestyle.create(pylatex.Foot("L")) as footer_left:
            footer_left.append(pylatex.simple_page_number())

        # pagestyle.append(pylatex.NoEscape(r"\noindent\makebox[\linewidth]{\rule{\paperwidth}{0.4pt}}"))
        pagestyle.append(pylatex.NoEscape(r'\renewcommand{\headrulewidth}{1pt}'))

        return pagestyle

    def _get_image_path(self, image_filename: str) -> str:
        image_folder = Path(os.getcwd()).joinpath(self.cfg.get("CONFIGURATION", "images_folder"))
        image_path = image_folder.joinpath(image_filename)
        if not image_path.exists():
            image_path = image_folder.joinpath(self.cfg.get("CONFIGURATION", "image_404"))
        return image_path.as_posix()

    def fill_document(self):
        """Add a section, a subsection and some text to the document.

        :param doc: the document
        :type doc: :class:`pylatex.document.Document` instance
        """
        sections = self.cfg.get("SECTIONS", "toc")
        for section in sections.split(","):
            section = section.strip()
            section_writer = self.find_section(section_name=section)
            section_writer.write(doc=self.doc)
            self.doc.append(pylatex.NewPage())

    def find_section(self, section_name: str) -> SectionWriter:
        section_path = Path(self.cfg.get("CONFIGURATION", "sections_folder")).joinpath(section_name)
        if not section_path.exists():
            self._create_missing_section(section_path=section_path)

        sectionWriter = SectionWriter(section_header=section_name, section_path=section_path,
                                      variable_dict=self.project_variables)

        return sectionWriter

    def _create_missing_section(self, section_path: Path):
        section_path.mkdir()
        section_config = configparser.ConfigParser()
        section_config_file = section_path.joinpath("section_config.ini")
        section_config["SECTION_TEXT"] = {"text": "TBD"}
        section_config["SUBSECTIONS"] = {}
        section_config["FIGURES"] = {}
        with open(section_config_file, 'w') as cfg_file:
            section_config.write(cfg_file)

    def run(self):
        filepath = Path(self.cfg["CONFIGURATION"]["output_location"]).joinpath(self.cfg["CONFIGURATION"]["output_name"])
        self.fill_document()
        self.doc.generate_pdf(filepath=filepath, clean_tex=False)
