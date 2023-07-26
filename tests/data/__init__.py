"""Module interface for test data."""

import importlib
import importlib.resources


templates_path = importlib.resources.files("tests.data.templates")
targets_graphs_path = importlib.resources.files("tests.data.targets.graphs")
targets_xml_path = importlib.resources.files("tests.data.targets.xml")
targets_txt_path = importlib.resources.files("tests.data.targets.txt")
tables = importlib.import_module("tests.data.table_data", "tabular")
