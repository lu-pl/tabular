"""Type definitions for TabulaRDF."""

import os
import pathlib

from collections.abc import Callable, MutableMapping
from typing import Any, Literal as PyLiteral

import click

from jinja2.environment import Template
from rdflib import Graph, URIRef, Literal

from rdflib.plugin import plugins
from rdflib.serializer import Serializer


_Rule = Callable[[Any, Any, MutableMapping], Graph]
_RulesMapping = MutableMapping[str, _Rule]

_TripleObject = URIRef | Literal
_Triple = tuple[URIRef, URIRef, _TripleObject]

_RenderStrategy = PyLiteral["table", "row"]

_TemplateReference = str | os.PathLike | Template

_ClickPath = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    path_type=pathlib.Path
)

rdflib_graph_format_options = [
    plugin.name for plugin
    in plugins()
    if plugin.kind == Serializer
    ]

_GraphFormatOptions = PyLiteral[*rdflib_graph_format_options]
_GraphFormatOptionsChoice = click.Choice(rdflib_graph_format_options)
