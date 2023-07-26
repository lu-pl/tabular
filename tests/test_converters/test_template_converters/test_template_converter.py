"""Pytest entry point for TemplateConverter tests."""

import os
import pandas as pd
import pathlib

from jinja2 import Template, Environment, FileSystemLoader, select_autoescape

from tabular import TemplateConverter
from tests.data import (
    templates_path,
    targets_graphs_path,
    targets_xml_path,
    targets_txt_path,
    tables
)


def test_template_converter_str_input():
    """TemplateConverter test.

    Instantiate template parameter with string input
    and compare rendering against target.
    """
    template = str(templates_path / "books.j2")
    assert isinstance(template, str)

    converter = TemplateConverter(
        dataframe=tables.bookstore_df,
        template=template
    )

    with open(targets_txt_path / "books.txt") as f:
        target = f.read()

    rendering = converter.render()

    # minor slicing cheat..
    assert rendering[1:] == target


def test_template_converter_template_input():
    """TemplateConverter test.

    Instantiate template parameter with jinja.Template input
    and compare rendering against target.
    """
    posix_path = templates_path._paths[0]
    assert isinstance(posix_path,  pathlib.Path)

    environment = Environment(
        loader=FileSystemLoader(posix_path),
        autoescape=select_autoescape()
    )

    template = environment.get_template("books.j2")

    converter = TemplateConverter(
        dataframe=tables.bookstore_df,
        template=template
    )

    with open(targets_txt_path / "books.txt") as f:
        target = f.read()

    rendering = converter.render()

    # minor slicing cheat..
    assert rendering[1:] == target


def test_template_converter_path_input():
    """TemplateConverter test.

    Instantiate template parameter with pathlib.Path input
    and compare rendering against target.
    """
    template = templates_path / "books.j2"
    assert isinstance(template, os.PathLike)

    converter = TemplateConverter(
        dataframe=tables.bookstore_df,
        template=template
    )

    with open(targets_txt_path / "books.txt") as f:
        target = f.read()

    rendering = converter.render()

    # minor slicing cheat..
    assert rendering[1:] == target


def test_get_jinja_template_from_path():
    """Test for TemplateConverter._get_jinja_template_from_path."""
    path = templates_path / "books.j2"
    template = TemplateConverter._get_jinja_template_from_path(path)

    assert isinstance(template, Template)

def test_get_jinja_template():
    """Test for TemplateConverter._get_jinja_template."""
    template = templates_path / "books.j2"

    converter = TemplateConverter(
        dataframe=tables.bookstore_df,
        template=template
    )


    posix_path = templates_path._paths[0]

    environment = Environment(
        loader=FileSystemLoader(posix_path),
        autoescape=select_autoescape()
    )

    input_str = str(template)
    input_pathlike = template
    input_template = environment.get_template("books.j2")

    assert isinstance(converter._get_jinja_template(input_str), Template)
    assert isinstance(converter._get_jinja_template(input_pathlike), Template)
    assert isinstance(converter._get_jinja_template(input_template), Template)
