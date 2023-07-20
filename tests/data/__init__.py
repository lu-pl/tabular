"""Module interface for test data."""

import importlib.resources

from jinja2 import Environment, FileSystemLoader, select_autoescape


##################################################
#### bookstore data
## exposes:
# bookstore_df,
# bookstore_template_path,
# bookstore_template,
# bookstore_target_path,
# bookstore_target

# bookstore_df
from tests.data.table_data.bookstore import bookstore_df

# bookstore_template_path
bookstore_template_path = (
    importlib.resources
    .files("tests.data.templates")
    # .joinpath("bookstore.j2")
    .joinpath("test.j2")
)

_env = Environment(
    loader=FileSystemLoader(bookstore_template_path.parent),
    autoescape=select_autoescape()
)

bookstore_template = _env.get_template(bookstore_template_path.name)

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
