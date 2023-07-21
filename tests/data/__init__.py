"""Module interface for test data."""

import importlib.resources

import pandas as pd

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rdflib import Graph


##################################################
#### bookstore data

# bookstore_df
from tests.data.table_data.bookstore import bookstore_df

# bookstore_template_path
bookstore_template_path = (
    importlib.resources
    .files("tests.data.templates")
    .joinpath("bookstore.j2")
)

bookstore_env = Environment(
    loader=FileSystemLoader(bookstore_template_path.parent),
    autoescape=select_autoescape()
)

books_row_template_path = (
    importlib.resources
    .files("tests.data.templates")
    .joinpath("books_row.j2")
)

books_row_env = Environment(
    loader=FileSystemLoader(bookstore_template_path.parent),
    autoescape=select_autoescape()
)

books_table_template_path = (
    importlib.resources
    .files("tests.data.templates")
    .joinpath("books_table.j2")
)

books_table_env = Environment(
    loader=FileSystemLoader(bookstore_template_path.parent),
    autoescape=select_autoescape()
)

bookstore_template = bookstore_env.get_template(bookstore_template_path.name)
books_row_template = books_row_env.get_template(books_row_template_path.name)
books_table_template = books_table_env.get_template(books_table_template_path.name)

# bookstore_target_path
bookstore_target_path = (
    importlib.resources
    .files("tests.data.targets.xml")
    .joinpath("bookstore.xml")
)

# bookstore_target
with open(bookstore_target_path) as f:
    bookstore_target: str = f.read()


##################################################
#### cortab data

cortab_name_acronym_template_path = (
    importlib.resources
    .files("tests.data.templates")
    .joinpath("template_cortab_name_acronym.ttl")
)

cortab_name_acronym_env = Environment(
    loader=FileSystemLoader(cortab_name_acronym_template_path.parent),
    autoescape=select_autoescape()
)

cortab_name_acronym_template = cortab_name_acronym_env.get_template(
    cortab_name_acronym_template_path.name
)

cortab_name_acronym_table = [
    {
        "corpusAcronym": "ReM",
        "corpusName": "Reference corpus Middle High German"
    },
    {
        "corpusAcronym": "SweDraCor",
        "corpusName": "Swedish Drama Corpus"
    }
]

cortab_name_acronym_df = pd.DataFrame(data=cortab_name_acronym_table)

cortab_name_acronym_path = (
    importlib.resources
    .files("tests.data.targets.graphs")
    .joinpath("cortab_name_acronym.ttl")
)

cortab_name_acronym_graph = Graph()
cortab_name_acronym_graph.parse(source=cortab_name_acronym_path)




##################################################
