"""Pytest entry point for FieldGraphConverter tests."""

from tabulardf import FieldGraphConverter

from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import RDF

from tests.data import (
    tables,
    targets_graphs_path
)


CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
CRMCLS = Namespace("https://clscor.io/ontologies/CRMcls/")


def corpus_name_rule(subject_field, object_field, store):
    """Rule for building a field graph.

    Note that since the test table has only two columns
    only one field rule is needed for the conversion.
    """

    corpus_acronym_lower = subject_field.lower()

    corpus_uri = URIRef(f"https://{corpus_acronym_lower}.clscor.io/entity/corpus")
    appellation_1 = URIRef(f"https://{corpus_acronym_lower}.clscor.io/entity/appellation/1")
    appellation_2 = URIRef(f"https://{corpus_acronym_lower}.clscor.io/entity/appellation/2")

    triples = [
        (
            corpus_uri,
            RDF.type,
            CRMCLS["X1_Corpus"]
        ),
        (
            corpus_uri,
            CRM["P1_is_identified_by"],
            appellation_1
        ),
        (
            corpus_uri,
            CRM["P1_is_identified_by"],
            appellation_2
        ),

        (
            appellation_1,
            RDF.type,
            CRM["E41_Appellation"]
        ),
        (
            appellation_1,
            CRM["P2_has_type"],
            URIRef(
                "https://core.clscor.io/entity/type/appellation_type/full_title"
            )
        ),
        (
            appellation_1,
            RDF.value,
            Literal(object_field)
        ),

        (
            appellation_2,
            RDF.type,
            CRM["E41_Appellation"]
        ),
        (
            appellation_2,
            CRM["P2_has_type"],
            URIRef(
                "https://core.clscor.io/entity/type/appellation_type/acronym"
            )
        ),
        (
            appellation_2,
            RDF.value,
            Literal(subject_field)
        ),


    ]

    graph = Graph()

    for triple in triples:
        graph.add(triple)

    return graph


def test_row_graph_converter():
    """Test for the FieldGraphConverter class.

    Generate a graph from ...
    and check for graph isomorphism against a target graph.
    """
    converter = FieldGraphConverter(
        dataframe=tables.cortab_partial_df,
        subject_column="corpusAcronym",
        column_rules={
            "corpusName": corpus_name_rule
        }
    )

    generated_graph = converter.to_graph()
    target_graph = Graph().parse(targets_graphs_path / "cortab_name_acronym.ttl")

    assert isomorphic(generated_graph, target_graph)
