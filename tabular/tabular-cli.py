"""CLI for TabulaR Template conversions."""

import os
import pathlib

from typing import Annotated

import typer
from rich import print


# https://typer.tiangolo.com/tutorial/parameter-types/path/
_TyperPath = Annotated[
    pathlib.Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
]



app = typer.Typer()

@app.command()
def tabular_cli(table_file: _TyperPath,
                template_file: _TyperPath,
                render_by_row: bool = False):
    """..."""
    print(table_file, template_file, render_by_row)


if __name__ == "__main__":
    app()
