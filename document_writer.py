import pylatex
import configparser
import os

from pathlib import Path

from section_writer import SectionWriter
from text_proprocessor import TextPreProcessor


class DocumentWriter():
    '''
    Writes documents
    '''

    def __init__(self, configuration_file: str):
        self.cfg = configparser.ConfigParser()
        path = Path(configuration_file)
        assert path.exists(), "The configuration file does not exist!"
        self.cfg.read(configuration_file)
        geometry_options = dict(self.cfg["DOCUMENT_GEOMETRY"])
        geometry_options["includeheadfoot"] = True  # self.cfg.getboolean("DOCUMENT_GEOMETRY", "includeheadfoot")
        self.doc = pylatex.Document(geometry_options=geometry_options)
        self.processor = TextPreProcessor(configuration_file=configuration_file)

        self._generate_preamble()

        self._generate_table_of_contents()

    def _generate_preamble(self):
        """
        The preamble is the first section of an input file, before the text of the document itself,
        in which you tell LaTeX the type of document, and other information LaTeX will need to
        format the document correctly.
        :return: None
        """
        header_footer = self._generate_header_footer()
        self.doc.preamble.append(header_footer)
        self.doc.change_document_style("headerfooter")
        self._generate_title_page()

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
                text_wrapper.append("NPO Hardware Example\n")
                text_wrapper.append("Dayton Peak Example\n")
                text_wrapper.append("HLD Example")

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

    def _generate_title_page(self):
        self.doc.preamble.append(pylatex.Command('title', 'Awesome Title'))
        self.doc.preamble.append(pylatex.Command('author', 'Anonymous author'))
        self.doc.preamble.append(pylatex.Command('date', pylatex.NoEscape(r'\today')))
        self.doc.append(pylatex.NoEscape(r'\maketitle'))
        self.doc.append(pylatex.NewPage())

    def _generate_table_of_contents(self):
        self.doc.append(pylatex.NoEscape(r'\tableofcontents'))
        self.doc.append(pylatex.basic.NewPage())

    def _add_HeaderFooter(self):
        pass

    def run(self):
        filepath = Path(self.cfg["CONFIGURATION"]["output_location"]).joinpath(self.cfg["CONFIGURATION"]["output_name"])
        self.fill_document()
        self.doc.generate_pdf(filepath=filepath, clean_tex=False)

    def find_section(self, section_name: str) -> SectionWriter:
        section_path = Path(self.cfg.get("CONFIGURATION", "sections_folder")).joinpath(section_name)
        if not section_path.exists():
            self._create_missing_section(section_path=section_path)

        sectionWriter = SectionWriter(section_path=section_path, section_header=section_name,
                                      text_processor=self.processor)
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
