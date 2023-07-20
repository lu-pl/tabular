"""Module interface for test data."""

import importlib.resources

from jinja2 import Environment, FileSystemLoader, select_autoescape


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
