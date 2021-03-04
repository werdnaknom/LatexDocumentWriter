import json
import configparser
from pathlib import Path


class TextPreProcessor():
    cfg: configparser.ConfigParser
    project_json: dict

    def __init__(self, configuration_file: str):
        self.cfg = configparser.ConfigParser()
        path = Path(configuration_file)
        assert path.exists(), "The configuration file does not exist!"
        self.cfg.read(configuration_file)
        project_json_path = self.cfg.get("CONFIGURATION", "project_json")
        with open(project_json_path, 'r') as json_file:
            read = json_file.read()
            self.project_json = json.loads(read)

        self.__post_init()

    def get_variable(self, variable: str):
        return self.project_json[variable]

    def set_variable(self, variable: str, value):
        self.project_json[variable] = value

    def __post_init(self):
        self._set_port_string(port_count=self.get_variable("port_count"))

    def process_text(self, text:str) -> str:
        output_text = text.format(**self.project_json)
        return output_text


    def _set_port_string(self, port_count: int):
        variable_name = "port_string"
        if port_count == 1:
            self.set_variable(variable_name, "SP")
        elif port_count == 2:
            self.set_variable(variable_name, "DP")
        elif port_count == 4:
            self.set_variable(variable_name, "QP")

    def get_form_factor(self):
        form_factor = self.get_variable("form_factor")
        if form_factor == "PCIe":
            height = self.get_variable("height")
            length = self.get_variable("length")
            return f"{form_factor} {height}{length}"
        else:
            return form_factor


