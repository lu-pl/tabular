"""TabulaR.

Functionality for rule-based and template-based Dataframe to Graph conversions.
"""

import functools

from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Generator,
    IO,
    Iterable,
    Optional,
)

import pandas as pd
from pandas.core.series import Series

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Template

from rdflib import Graph, URIRef, Namespace

from tabular_types import _RulesMapping


# temp import
from itertools import count


class _GraphConverter(ABC):

    @property
    def graph(self) -> Graph:
        """Getter for the internal graph component."""
        return self._graph

    @abstractmethod
    def to_graph(self) -> Graph:
        """Add triples to the Graph component and return."""
        raise NotImplementedError

    @functools.wraps(Graph.serialize)
    def serialize(self, *args, **kwargs):
        """Serialize triples from graph component.

        Proxy for rdflib.Graph.serialize.
        """
        if not self._graph:
            self._graph = self.to_graph()

        return self._graph.serialize(*args, **kwargs)


class _TemplateConverter(ABC):

    @abstractmethod
    def render(self,
               call: Callable[[str], Any] = lambda x: x) -> None:
        """Pass every row rendering to a callable.

        See the render_to_file method for an application of render.
        Note that this method is side-effect only.
        """
        raise NotImplementedError

    def render_to_file(self, file: str | IO):
        """Write renderings to a file.

        Convenience method that utilizes the more generic render method.
        For custom behavior use the render method directly.
        """
        with open(file, "w") as f:
            self.render(f.write)


class TemplateConverter(_TemplateConverter):
    """General TemplateConverter class.

    Iterate over a dataframe and pass row data to a jinja rendering.
    Row data is available as 'data' dictionary within the template.
    """

    def __init__(self,
                 dataframe: pd.DataFrame,
                 template: Template | Iterable[Template],
                 data: Optional[dict] = None
                 ) -> None:
        """Initialize a TemplateConverter."""
        self.dataframe = dataframe
        self.template = (
            template
            if isinstance(template, Iterable)
            else [template]
        )
        self.data = data or {}

    def _apply_template_to_row(self, row: Series) -> Generator[str, None, None]:
        """Generate a dict from a Series and pass it to Template.render."""
        _row_dict = row.to_dict()
        _data = {"data": _row_dict}
        self.data.update(_data)

        for template in self.template:
            yield template.render(self.data)

    def _apply_template_to_dataframe(self,
                                     dataframe: Optional[pd.DataFrame] = None
                                     ) -> Generator[str, None, None]:
        """Apply jinja renderings to every row in a dataframe."""
        dataframe = (
            self.dataframe
            if dataframe is None
            else dataframe
        )

        for _, row in dataframe.iterrows():
            yield from self._apply_template_to_row(row)

    def render(self,
               call: Callable[[str], Any] = lambda x: x) -> None:
        """Pass every row rendering to a callable.

        Note that this method is side-effect only.
        """
        for rendering in self._apply_template_to_dataframe(self.dataframe):
            call(rendering)


class TemplateGraphConverter(_GraphConverter, TemplateConverter):

    def __init__(self, *args, graph: Optional[Graph] = None, **kwargs):
        """Initialize a TemplateGraphConverter."""
        super().__init__(*args, **kwargs)
        self._graph = Graph() if graph is None else graph

    def to_graph(self) -> Graph:
        """Parse template renderings and return the graph component."""
        self.render(
            lambda data: self._graph.parse(data=data)
        )

        return self._graph


class RuleGraphConverter(_GraphConverter):
    """Rule-based pandas.DataFrame to rdflib.Graph converter.

    DFGraphConverter iterates over a dataframe and constructs RDF triples
    by constructing a generator of subgraphs ('field graphs');
    subgraphs are then merged with an rdflib.Graph component.

    For basic usage examples see https://github.com/lu-pl/rdfdf.
    """

    store: dict = dict()

    def __init__(self,
                 dataframe: pd.DataFrame,
                 *,
                 subject_column: str,
                 subject_rule: Optional[
                     Callable[[str], URIRef] | Namespace
                 ] = None,
                 column_rules: _RulesMapping,
                 graph: Optional[Graph] = None):
        """Initialize a DFGraphConverter instance."""
        self._df = dataframe
        self._subject_column = subject_column
        self._subject_rule = subject_rule
        self._column_rules = column_rules
        # bug fix: this allows also empty but namespaced graphs
        self._graph = Graph() if graph is None else graph

    def _apply_subject_rule(self, row: pd.Series) -> URIRef:
        """Apply subject_rule to the subject_column of a pd.Series row.

        Conveniently allows to also pass an rdflib.Namespace
        (or generally Sequence types) as subject_rule.
        """
        try:
            # call
            _sub_uri = self._subject_rule(row[self._subject_column])
        except TypeError:
            # getitem
            _sub_uri = self._subject_rule[row[self._subject_column]]

        return _sub_uri

    def _generate_graphs(self) -> Generator[Graph, None, None]:
        """Loop over the table rows of the provided DataFrame.

        Generates and returns a Generator of graph objects for merging.
        """
        for _, row in self._df.iterrows():

            _subject = (
                self._apply_subject_rule(row)
                if self._subject_rule
                else row[self._subject_column]
            )

            for field, rule in self._column_rules.items():
                _object = row[field]

                field_rule_result = rule(
                    _subject,
                    _object,
                    self.store
                )

                # yield only rdflib.Graph instances
                if isinstance(field_rule_result, Graph):
                    yield field_rule_result
                continue

    def _merge_to_graph_component(self, graphs: Iterable[Graph]) -> Graph:
        """Merge subgraphs to main graph.

        Loops over a graphs generator and merges every field_graph with the
        self._graph component. Returns the modified self._graph component.
        """
        # warning: this is not BNode-safe (yet)!!!
        # todo: how to do BNode-safe graph merging?
        for graph in graphs:
            self._graph += graph

        return self._graph

    def to_graph(self) -> Graph:
        """Add triples from _generate_triples and return the graph component."""
        # generate subgraphs
        _graphs_generator = self._generate_graphs()

        # merge subgraphs to graph component
        self._merge_to_graph_component(_graphs_generator)

        return self._graph




##################################################
##################################################
#### playground

table = [
    {
        "id": "rem",
        "full_title": "Reference corpus Middle High German"
    },
    {
        "id": "SweDracor",
        "full_title": "Swedish Drama Corpus"
    }
]

df = pd.DataFrame(data=table)

##################################################
#### TemplateConverter test


env = Environment(
    loader=FileSystemLoader("."),
    autoescape=select_autoescape()
)

# template = env.get_template("converter_test.j2")
template = env.get_template("converter_rdf_test.ttl")


# mutable default arg as cache!
def cntfn(cnt=count()):
    return next(cnt)

# template_converter = TemplateConverter(
template_converter = TemplateGraphConverter(
    dataframe=df,
    template=template,
    data={"fn": {"cnt": cntfn}}
)

print(template_converter.serialize(format="ttl"))
# g = template_converter.to_graph()
# print(g.serialize())

# template_converter.render(print)
# template_converter.render_to_file("./test_rendering.txt")


# template_converter = TemplateGraphConverter(df, template)

##################################################
##################################################
