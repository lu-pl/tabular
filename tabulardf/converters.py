"""TabulaRDF converters.

Functionality for DataFrame to RDF Graph conversions.
"""

import functools
import pathlib

from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Optional,
    Self,
)

import pandas as pd
from pandas.core.series import Series

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
# from lxml.etree import XMLParser, _Element
from rdflib import Graph, URIRef, Namespace

from tabulardf.tabulardf_types import (
    _RulesMapping,
    _RenderStrategy,
    _TemplateReference
)


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

    Iterate over a dataframe and pass table data to a jinja rendering.

    Two render strategies are available:

    - "table"
      Every template gets passed the entire table data as "table_data";
      this means that iteration must be done in the template.
      See the render method.

    - "row":
      For every row iteration the template gets passed the current row data only;
      so iteration is done at the Python level, not in the template.
      Row data is available as 'row_data' dictionary within the template.
      See the render_by_row method.
    """

    def __init__(self,
                 *,
                 dataframe: pd.DataFrame,
                 template: _TemplateReference,
                 data: Optional[dict] = None
                 ) -> None:
        """Initialize a TemplateConverter."""
        self.dataframe = dataframe
        # I want kwargs only, so no *templates
        self.template = self._get_jinja_template(template)
        self.data = data or {}

    @staticmethod
    def _get_jinja_template_from_path(template_path: pathlib.Path) -> Template:
        """Get a jinja2.Template from a pathlib.Path.

        Creates a jinja2.Environment using a FileSystemLoader
        and generates a jinja2.Template from that loader instance.

        Helper for _get_jinja_template.
        """
        assert template_path.is_file(), (
            TypeError(f"'{template_path}' is not a file.")
        )

        template_folder_path = template_path.parent.absolute()
        template_file_name = template_path.name

        environment = Environment(
            loader=FileSystemLoader(template_folder_path),
            autoescape=select_autoescape()
        )

        template = environment.get_template(template_file_name)

        return template

    def _get_jinja_template(self,
                            template_reference: _TemplateReference
                            ) -> Template:
        """Get a jinja2.Template from a TemplateReference."""
        if isinstance(template_reference, Template):
            template = template_reference
        else:
            template_path = pathlib.Path(template_reference)
            template = self._get_jinja_template_from_path(template_path)

        return template

    # todo:
    @classmethod
    def initialize_template(cls) -> type[Self]:  # better: functools.partial?
        """Build a jinja2.Environment and init."""
        ...

    # maybe make this a staticmethod = reuse in RowGraphConverter?
    def _get_table_data(self) -> Generator[dict, None, None]:
        """Construct a generator of row data dictionaries.

        This is intended to provide the template data for the render method.
        """
        return (
            row.to_dict()
            for _, row
            in self.dataframe.iterrows()
        )

    def _apply_template_to_row(self, row: Series) -> str:
        """Generate a dict from a Series and pass it to Template.render."""
        _row_dict = row.to_dict()
        _data = {"row_data": _row_dict}
        self.data.update(_data)

        return self.template.render(self.data)

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
            yield self._apply_template_to_row(row)

    def _apply_to_renderings(self,
                             call: Callable[[str], Any] = lambda x: x
                             ) -> None:
        """Pass every row rendering to a callable.

        Auxiliary method for side-effect-only operations.
        For an application see e.g. the render_to_file method.
        """
        for rendering in self._apply_template_to_dataframe(self.dataframe):
            call(rendering)

    def render(self) -> str | Generator[str, None, None]:
        """Render a jinja template.

        Every template gets passed the entire table data;
        so iteration must be done in the template.
        The data passed to the template is a generator of row dictionaries
        and is accessible as 'table_data' in the template.
        """
        table_data = {"table_data": self._get_table_data()}

        # bug fix: update data also for render
        table_data.update(self.data)

        return self.template.render(table_data)

    # note: should this even be a a public method?
    # maybe run this with a strategy="row" paramter from render?
    def render_by_row(self) -> Generator[str, None, None]:
        """Render a jinja template by row.

        For every row iteration the template gets passed the current row data only;
        so iteration is done at the Python level, not in the template.
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

    Iterates over a dataframe and passes table data to a jinja rendering.
    Table data is available as "table_data" or "row_data" respectively;
    see the 'render' and 'render_by_row' methods.

    'to_graph' parses renderings with rdflib.Graph.parse
    and so merges row renderings to an rdflib.Graph component.
    """

    def __init__(self, *args, graph: Optional[Graph] = None, **kwargs):
        """Initialize a TemplateGraphConverter."""
        super().__init__(*args, **kwargs)
        self._graph = Graph() if graph is None else graph

    def to_graph(self) -> Graph:
        """Parse template row renderings and return the graph component."""
        self._apply_to_renderings(
            lambda data: self._graph.parse(data=data)
        )

        return self._graph


class RowGraphConverter(_GraphConverter):
    """Callable-based pandas.DataFrame to rdflib.Graph converter.

    Iterates over a dataframe and applies row_rule for every row.

    For every row the row_rule gets passed the row_data as dictionry
    and is responsible for returning an rdflib.Graph instance (a 'row graph');
    thus generated subgraphs are then merged into a graph component.
    """

    def __init__(self,
                 dataframe: pd.DataFrame,
                 *,
                 row_rule: Callable[[dict], Graph],
                 graph: Optional[Graph] = None) -> None:
        """Initialize a RowGraphConverter instance."""
        self._df = dataframe
        self._row_rule = row_rule
        self._graph = Graph() if graph is None else graph

    def _generate_graphs(self) -> Generator[Graph, None, None]:
        """Construct a generator of subgraphs for merging.

        Iterates over the dataframe component and passes row data
        as a dictionary to a callable which is responsible for
        generating an instance of rdflib.Graph.
        """
        for _, row in self._df.iterrows():
            row_dict = row.to_dict()
            yield self._row_rule(row_dict)

    def to_graph(self):
        """Merge triples from _generate_graphs and return graph component."""
        # generate subgraphs
        _graphs_generator = self._generate_graphs()

        for graph in _graphs_generator:
            self._graph += graph

        return self._graph


class FieldGraphConverter(_GraphConverter):
    """Callable-based pandas.DataFrame to rdflib.Graph converter.

    Iterates over a dataframe and applies a column_rule for every field.

    For every field of every row, looks up and applies a callable in column_rules;
    column_rules must be a mapping of column headers and callables of arity 3.

    Every callable gets passed
      1. the value of the current subject field
         (specified in subject_column),
      2. the value of the current field (the triple object) and
      3. the store class-level attribute, a dictionary for state retention
         (state can thus be shared between callables and also FieldGraphConverters).

    Callables of column_rules are responsible for
    returning an rdflib.Graph instance (a 'field graph');
    thus generated subgraphs are then merged into a graph component.
    """

    store: dict = dict()

    def __init__(self,
                 dataframe: pd.DataFrame,
                 *,
                 subject_column: Any,
                 subject_rule: Optional[
                     Callable[[Any], URIRef] | Namespace
                 ] = None,
                 column_rules: _RulesMapping,
                 graph: Optional[Graph] = None) -> None:
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
        """Loop over table rows of the provided DataFrame.

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
        """Merge triples from _generate_graphs and return the graph component."""
        # generate subgraphs
        _graphs_generator = self._generate_graphs()
        # merge subgraphs to graph component
        self._merge_to_graph_component(_graphs_generator)

        return self._graph
