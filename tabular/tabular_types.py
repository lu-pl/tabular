"""Type definition for tabuler"""

from collections.abc import Callable, MutableMapping
from typing import Any, Literal as PyLiteral

from rdflib import Graph, URIRef, Literal

_Rule = Callable[[Any, Any, MutableMapping], Graph]
_RulesMapping = MutableMapping[str, _Rule]

_TripleObject = URIRef | Literal
_Triple = tuple[URIRef, URIRef, _TripleObject]

_RenderStrategy = PyLiteral["table", "row"]
