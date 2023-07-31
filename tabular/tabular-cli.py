"""CLI for TabulaR Template conversions."""

import pathlib

from typing import Any

import click

from cli.click_custom import (
    RequiredIf,
    RequiredMultiOptions,
    DefaultCommandGroup
)


_ClickPath = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    path_type=pathlib.Path
)


@click.group(cls=DefaultCommandGroup)
def tabular_cli():
    """..."""
    pass


@tabular_cli.command(default_command=True)
@click.argument("table_file",
                type=_ClickPath)
@click.argument("template_file",
                type=_ClickPath)
@click.option("-c", "--column",
              type=str,
              cls=RequiredIf,
              required_if="rows")
@click.option("-r", "--rows",
              type=tuple,
              cls=RequiredMultiOptions,
              required_if="column")
@click.option("--render-by-row",
              type=bool,
              default=False)
def _default(table_file: pathlib.Path,
         template_file: pathlib.Path,
         column: str,
         rows: tuple[Any, ...],
         render_by_row):
    """..."""
    # 1. get a dataframe
    # optional: partition a dataframe

    # 2. get a Converter

    # 3. render according to strategy (table or row)

    print(table_file)
    print(template_file)
    print(type(table_file))
    print(type(template_file))
    print()
    print(column)
    print(rows)


@tabular_cli.command()
@click.argument("table_file",
                type=_ClickPath)
@click.argument("template_file",
                type=_ClickPath)
@click.option("-c", "--column",
              type=str,
              cls=RequiredIf,
              required_if="rows")
@click.option("-r", "--rows",
              type=tuple,
              cls=RequiredMultiOptions,
              required_if="column")
@click.option("-f", "--format",
              type=str,
              default="ttl")
def graph(table_file: pathlib.Path,
          template_file: pathlib.Path,
          column: str,
          rows: tuple[Any, ...],
          format):
    """..."""
    print(table_file)
    print(template_file)
    print()
    print(column)
    print(rows)
    print(format)


if __name__ == "__main__":
    tabular_cli()
