"""Pytest entry point for TemplateConverter tests."""

from tabular import TemplateConverter

from tests.data import (
    bookstore_df,
    bookstore_target,
    bookstore_template,
    books_row_template,
    books_table_template
)


def test_templateconverter_bookstore():
    """Test for the TemplateConverter class.

    Generates a rendering and compares it to target content.
    """
    bookstore_template_converter = TemplateConverter(
        dataframe=bookstore_df,
        template=bookstore_template
    )

    bookstore_table = bookstore_template_converter.render()

    # minor rstrip cheat..
    assert bookstore_table == bookstore_target.rstrip()


def test_temlateconverter_books():
    """Test for the TemplateConverter class.

    Generates and compares renderings from render and render_by_row.
    """
    books_row_template_converter = TemplateConverter(
        dataframe=bookstore_df,
        template=books_row_template
    )

    books_table_template_converter = TemplateConverter(
        dataframe=bookstore_df,
        template=books_table_template
    )

    books_row = "".join(books_row_template_converter.render_by_row())
    # note: whitespace stripped from template: https://stackoverflow.com/a/36871283/6455731
    books_table = books_table_template_converter.render()

    assert books_row == books_table



##################################################

## todo

import pathlib

import pandas as pd
from tabular import TemplateConverter

table = [
    {
        'category': 'programming',
        'title': 'Fluent Python',
        'author': 'Luciano Ramalho',
        'year': 2022,
        'price': 50.99
    },
    {
        'category': 'web',
        'title': 'Learning XML',
        'author': 'Erik T. Ray',
        'year': 2003,
        'price': 39.95
    }
]

df = pd.DataFrame(data=table)

templates_path = pathlib.Path("/home/upgrd/projects/python-projects/tabular/tests/data/templates/")

table_converter = TemplateConverter(
    dataframe=df,
    # template="./tests/data/templates/table_template.j2"
    template = templates_path / "table_template.j2"
)

# print(table_converter.render())

row_converter = TemplateConverter(
    dataframe=df,
    template= templates_path / "row_template.j2"
)

# print("".join(row_converter.render_by_row()))
