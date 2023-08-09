"""CLI for TabulaRDF Template conversions."""

import pathlib

from typing import Any, Callable

import click

from tabulardf import TemplateConverter, TemplateGraphConverter

from tabulardf.tabulardf_types import (
    _ClickPath,
    _GraphFormatOptions,
    _GraphFormatOptionsChoice
)

from tabulardf.cli.click_custom import (
    RequiredIf,
    RequiredMultiOptions,
    DefaultCommandGroup
)
from tabulardf.cli.converter_setup import initialize_converter
from tabulardf.cli.docs import docs


_common_options = [
    click.argument("table",
                   type=_ClickPath),
    click.argument("template",
                   type=_ClickPath),
    click.option("-c", "--column",
                 type=str,
                 cls=RequiredIf,
                 required_if="rows",
                 help=docs.column),
    click.option("-r", "--rows",
                 type=tuple,
                 cls=RequiredMultiOptions,
                 required_if="column",
                 help=docs.rows),

    click.option("--context-module",
                 type=_ClickPath,
                 help=docs.context_module,
                 required=False)
]


def common_options(f: Callable) -> Callable:
    """Stacks click.arguments/click.options in a single place.

    Used as an aggegrate for shared subcommand options.
    Note: it is of utmost importance to reverse the argument/options iterable;
    else arguments succession will be inverted!
    """
    for option in reversed(_common_options):
        f = option(f)
    return f


@click.group(cls=DefaultCommandGroup)
def tacl():  # noqa: D403
    """TabulaRDF CLI.

    Command-line interface for converting tabular data
    using Jinja2 templating.
    """
    pass


@tacl.command()
@common_options
@click.option("--render-by-row",
              type=bool,
              default=False,
              is_flag=True,
              help=docs.render_by_row)
def noparse(table: pathlib.Path,
            template: pathlib.Path,
            column: str,
            rows: tuple[Any, ...],
            context_module: pathlib.Path | None = None,
            render_by_row: bool = False):
    """Generate Jinja2 renderings without prior parsing.

    \b
    TABLE: A file holding tabular data, e.g. an Excel or csv file.
    TEMPLATE: A Jinja2 template file.
    """
    # get converter
    converter = initialize_converter(
        converter_type=TemplateConverter,
        table=table,
        template=template,
        column=column,
        rows=rows,
        context_module=context_module
    )

    # render according to strategy (table or row)
    if render_by_row:
        click.echo(converter.render_by_row())
    else:
        click.echo(converter.render())


@tacl.command()
@common_options
@click.option("-f", "--format",
              type=_GraphFormatOptionsChoice,
              default="ttl",
              help=docs.format)
def graph(table: pathlib.Path,
          template: pathlib.Path,
          column: str,
          rows: tuple[Any, ...],
          context_module: pathlib.Path | None = None,
          # https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
          format: _GraphFormatOptions = "ttl"):
    """Generate and parse Jinja2 renderings into an rdflib.Graph.

    \b
    TABLE: A file holding tabular data, e.g. an Excel or csv file.
    TEMPLATE: A Jinja2 template file.
    """
    # get converter
    converter = initialize_converter(
        converter_type=TemplateGraphConverter,
        table=table,
        template=template,
        column=column,
        rows=rows,
        context_module=context_module
    )

    # serialize from rdflib.Graph instance according to format
    click.echo(converter.serialize(format=format))


if __name__ == "__main__":
    tacl()
