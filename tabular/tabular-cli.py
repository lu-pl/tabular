"""CLI for TabulaR Template conversions."""

import pathlib

from typing import Any

import click

from cli_utils.click_custom import RequiredIf, RequiredMultiOptions


_ClickPath = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    path_type=pathlib.Path
)


@click.command()
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
def tabular_cli(table_file: pathlib.Path,
                template_file: pathlib.Path,
                column: str,
                rows: tuple[Any]):
    """.."""
    print(table_file)
    print(template_file)
    print(type(table_file))
    print(type(template_file))


if __name__ == "__main__":
    tabular_cli()
