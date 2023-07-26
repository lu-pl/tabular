from itertools import count
from rdflib import Graph
from rdflib.compare import isomorphic

from tabular import TemplateGraphConverter
from tests.data import (
    tables,
    templates_path,
    targets_graphs_path
)


def counter(cnt=count()):
    "Wrapper for itertools.count."
    return next(cnt)


def test_cortab_name_acronym():
    """Test for the TemplateGraphConverter class.

    Generate a graph from a template
    and check for graph isomorphism against a target graph.
    """

    converter = TemplateGraphConverter(
        dataframe=tables.cortab_partial_df,
        template=templates_path / "template_cortab_name_acronym.ttl",
        data={"utils": {"counter": counter}}
    )

    converted_graph = converter.to_graph()
    target_graph = Graph().parse(source=targets_graphs_path / "cortab_name_acronym.ttl")

    assert isomorphic(converted_graph, target_graph)
