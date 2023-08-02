"""Pytest entry point for the TabulaR CLI noparse subcommand"""

from click.testing import CliRunner

from tests.data import templates_path, targets_txt_path, tables_path
from tabular import tacl


table = tables_path / "bookstore.csv"

template = templates_path / "books.j2"
# template_table = templates_path / "books_table.j2"
# template_row = templates_path / "books_row.j2"

target = targets_txt_path / "books.txt"
with open(target) as f:
    target_content_lines = f.readlines()


def test_cli_noparse_books_table():
    """Test for the tacl CLI.

    The following shell command is tested:
    'tacl bookstore.csv books.j2'.
    """
    runner = CliRunner()

    result = runner.invoke(
        tacl.tacl,
        [
            "noparse",
            str(table),
            str(template),
        ]
    )

    ...


def test_cli_noparse_books_row():
    """Test for the tacl CLI.

    The following shell command is tested:
    'tacl bookstore.csv books_table.j2 --render-by-row'."""
    ...
