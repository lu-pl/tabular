from itertools import count

from tabular import TemplateGraphConverter

from tests.data import (
    cortab_name_acronym_df,
    cortab_name_acronym_template,
    cortab_name_acronym_graph
)

from rdflib.compare import isomorphic


def counter(cnt=count()):
    "Wrapper for itertools.count."
    return next(cnt)


def test_cortab_name_acronym():
    """Test for the TemplateGraphConverter class.

    Generate a graph from a template
    and check for graph isomorphism against a target graph.
    """

    converter = TemplateGraphConverter(
        dataframe=cortab_name_acronym_df,
        template=cortab_name_acronym_template,
        data={"utils": {"counter": counter}}
    )

    converted_graph = converter.to_graph()
    target_graph = cortab_name_acronym_graph

    assert isomorphic(converted_graph, target_graph)
