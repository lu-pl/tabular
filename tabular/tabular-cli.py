"""CLI for TabulaR Template conversions."""

import pathlib

from typing import Any, Callable

import click

from cli.click_custom import (
    RequiredIf,
    RequiredMultiOptions,
    DefaultCommandGroup
)

from tabular_types import (
    _ClickPath,
    _GraphFormatOptions,
    _GraphFormatOptionsChoice
    )


_common_options = [
    click.argument("table",
                   type=_ClickPath),
    click.argument("template",
                   type=_ClickPath),
    click.option("-c", "--column",
                 cls=RequiredIf,
                 required_if="rows"),
    click.option("-r", "--rows",
                 cls=RequiredMultiOptions,
                 required_if="column")
]


def common_options(f: Callable) -> Callable:
    """Stacks click.arguments/click.options in a single place.

    Used as an aggegrate for shared subcommand options.
    """
    for option in _common_options:
        f = option(f)
    return f


@click.group(cls=DefaultCommandGroup)
def tabular_cli():
    """Actual CLI Docs."""
    pass


@tabular_cli.command()
@common_options
@click.option("--render-by-row",
              type=bool,
              default=False,
              is_flag=True)
def noparse(table: pathlib.Path,
            template: pathlib.Path,
            column: str,
            rows: tuple[Any, ...],
            render_by_row):
    """..."""
    # 1. get a dataframe
    # 1.2. optional: partition a dataframe

    # 2. get a TemplateConverter

    # 3. render according to strategy (table or row)
    click.echo((table, template, column, rows, render_by_row))


@tabular_cli.command()
@common_options
@click.option("-f", "--format",
              type=_GraphFormatOptionsChoice,
              default="ttl")
def graph(table: pathlib.Path,
          template: pathlib.Path,
          column: str,
          rows: tuple[Any, ...],
          format: _GraphFormatOptions):
    """..."""
    # 1. get a dataframe
    # 1.2. optional: partition a dataframe

    # 2. get a Converter

    # 3. serialize from rdflib.Graph instance according to format
    click.echo((table, template, column, rows, format))


if __name__ == "__main__":
    tabular_cli()
