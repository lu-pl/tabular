"""TabulaR.

Functionality for rule-based and template-based Dataframe to Graph conversions.
"""

import functools

from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Literal,
    Optional,
    Self,
)

import pandas as pd
from pandas.core.series import Series

from jinja2.environment import Template
from lxml.etree import XMLParser, _Element
from rdflib import Graph, URIRef, Namespace

from tabular.tabular_types import _RulesMapping, _RenderStrategy


class _GraphConverter(ABC):
    """ABC for GraphConverter classes."""

    @property
    def graph(self) -> Graph:
        """Getter for the internal graph component."""
        return self._graph

    @abstractmethod
    def to_graph(self) -> Graph:
        """Generate and add triples to the Graph component."""
        raise NotImplementedError

    @functools.wraps(Graph.serialize)
    def serialize(self, *args, **kwargs):
        """Serialize triples from graph component.

        Proxy for rdflib.Graph.serialize.
        """
        if not self._graph:
            self._graph = self.to_graph()

        return self._graph.serialize(*args, **kwargs)


class TemplateConverter:
    """General TemplateConverter class.

    Iterate over a dataframe and pass row data to a jinja rendering.
    Row data is available as 'data' dictionary within the template.
    """

    def __init__(self,
                 *,
                 dataframe: pd.DataFrame,
                 template: Template | Iterable[Template],
                 data: Optional[dict] = None
                 ) -> None:
        """Initialize a TemplateConverter."""
        self.dataframe = dataframe
        # I want kwargs only, so no *templates
        self.template = (
            template
            if isinstance(template, Iterable)
            else [template]
        )
        self.data = data or {}

    # todo:
    @classmethod
    def initialize_template(cls) -> type[Self]:  # better: functools.partial?
        """Build a jinja2.Environment and init."""
        ...

    def _get_table_data(self) -> Generator[dict, None, None]:
        """Construct a generator of row data dictionaries.

        This is intended to provide the template data for the render method.
        """
        return (
            row.to_dict()
            for _, row
            in self.dataframe.iterrows()
        )

    def _apply_template_to_row(self, row: Series) -> Generator[str, None, None]:
        """Generate a dict from a Series and pass it to Template.render."""
        _row_dict = row.to_dict()
        _data = {"row_data": _row_dict}
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

    def _apply_to_renderings(self,
                             call: Callable[[str], Any] = lambda x: x
                             ) -> None:
        """Pass every row rendering to a callable.

        Auxiliary method for side-effect only operations.
        +For an application see e.g. the render_to_file method.+
        """
        for rendering in self._apply_template_to_dataframe(self.dataframe):
            call(rendering)

    def render(self) -> str | Generator[str, None, None]:
        """Render jinja template(s).

        Every template gets passed the entire table data;
        so looping must be done in the template.
        The data passed to the template is a generator of row dictionaries
        and is accessible as 'table_data' in the template.
        """
        table_data = {"table_data": self._get_table_data()}

        if len(self.template) > 1:
            return (
                template.render(table_data)
                for template in self.template
            )

        return self.template[0].render(table_data)

    def render_by_row(self) -> Generator[str, None, None]:
        """Render jinja template(s) by row.

        For every row iteration the template gets passed the current row data only;
        so looping is done at the Python level, not in the template.
        The data passed to the template is a dictionary representing a table row
        and is accessible as 'row_data' in the template.
        """
        return self._apply_template_to_dataframe(self.dataframe)

    @functools.wraps(open)
    def render_to_file(self,
                       *args,
                       render_strategy: _RenderStrategy = "table",
                       mode="w",
                       **kwargs) -> None:
        """Write renderings to a file.

        Signature proxied from builtins.open.
        """
        with open(*args, mode=mode, **kwargs) as f:
            match render_strategy:
                case "row":
                    self._apply_to_renderings(f.write)
                case "table":
                    f.write(self.render())
                case _:
                    raise Exception((
                        f"Unknown render strategy '{render_strategy}'. "
                        "render_strategy parameter must be either 'table' or 'row'."
                        ))


class TemplateXMLConverter(TemplateConverter):
    """Template-based pandas.DataFrame to lxml.etree converter."""
    ...


class TemplateGraphConverter(_GraphConverter, TemplateConverter):
    """Template-based pandas.DataFrame to rdflib.Graph converter.

    Iterate over a dataframe and pass row data to a jinja rendering.
    Row data is available as 'row_data' dictionary within the template.

    to_graph parses renderings with rdflib.Graph.parse
    and so merges row graphs to an rdflib.Graph component.
    """

    def __init__(self, *args, graph: Optional[Graph] = None, **kwargs):
        """Initialize a TemplateGraphConverter."""
        super().__init__(*args, **kwargs)
        self._graph = Graph() if graph is None else graph

    def to_graph(self) -> Graph:
        """Parse template renderings and return the graph component."""
        self._apply_to_renderings(
            lambda data: self._graph.parse(data=data)
        )

        return self._graph


# maybe call this 'FieldGraphConverter' and also implement a 'RowGraphConverter' class
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
