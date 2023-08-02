"""Pytest entry point for the TabulaR CLI graph subcommand"""

from click.testing import CliRunner
from rdflib import Graph

from tests.data import templates_path, tables_path
from tabular import tacl


template = templates_path / "template_cortab_name_acronym.ttl"
table = tables_path / "corpusTable_prep.csv"


def test_cli_graph_rem():
    """Test for the tacl CLI.

    The following shell command is tested:
    'tacl corpusTable_prep.csv template_cortab_name_acronym.ttl --column id --rows 14'.# noqa E501
    """
    runner = CliRunner()

    result = runner.invoke(
        tacl.tacl,
        [
            "graph",
            str(table),
            str(template),
            "--column", "id",
            "--rows", 14
        ]
    )

    assert result.exit_code == 0
    assert result.output

    graph = Graph().parse(data=result.output)
    assert graph
