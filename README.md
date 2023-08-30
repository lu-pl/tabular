![<img src="lodkit.png" width=10% height=10%>](https://raw.githubusercontent.com/lu-pl/tabular/main/tabulardf_logo_small.png)

# TabulaRDF
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/tabulardf.svg)](https://badge.fury.io/py/tabulardf)

TabulaRDF - Functionality for DataFrame to RDF conversions.

Although TabulaRDF was primarily designed for table to RDF conversions, the `TemplateConverter` class should be general enough to allow conversions to basically any target format.

Just like the `TemplateGraphConverter` class parses renderings into an `rdflib.Graph` instance, renderings could e.g. also get parsed into an `lxml.etree`.

## Requirements

* python >= 3.11

## Installation

TabulaRDF is available on PyPI:
```shell
pip install tabulardf
```

Also the TaCL CLI can be installed with [pipx](https://pypa.github.io/pipx/):
```shell
pipx install tabulardf
```

For installation from source either use [poetry](https://python-poetry.org/) or run `pip install .` from the package folder.

## Usage
TabulaRDF provides two main approaches for table conversions, a template-based approach using the [Jinja2](https://jinja.palletsprojects.com/) templating engine and a pure Python/callable-based approach.

Also a CLI for template conversions is available, see [TaCL](https://github.com/lu-pl/tabulardf#tacl) below.

### Template converters

Template converters are based on the generic `TemplateConverter` class which allows to iterate over a dataframe and pass table data to Jinja renderings.

Two different render strategies are available through the `render` method and the `render_by_row` method respectively.

- With the `render` method, every template gets passed the entire table data as "table_data";
  this means that iteration must be done in the template.
- With the `render_by_row` method, for every row iteration the template gets passed the current row data (as "row_data") only;
  so iteration is done at the Python level, not in the template.
  
The `TemplateGraphConverter` class uses the `render_by_row` method and parses renderings into an `rdflib.Graph` instance.

```python
import pandas as pd

from jinja2 import Template
from tabulardf import TemplateGraphConverter

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

dataframe = pd.DataFrame(data=table)

template = Template(
    """
    @prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    {% set acronym_lower = row_data['id'] | lower %}

    <https://{{acronym_lower}}.clscor.io/entity/appellation/1> a crm:E41_Appellation ;
        crm:P2_has_type <https://core.clscor.io/entity/type/appellation_type/full_title> ;
        rdf:value "{{row_data['full_title']}}" .
    """
)

converter = TemplateGraphConverter(
    dataframe=dataframe,
    template=template
)

print(converter.serialize())
```

Output:

```turtle
@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<https://rem.clscor.io/entity/appellation/1> a crm:E41_Appellation ;
    crm:P2_has_type <https://core.clscor.io/entity/type/appellation_type/full_title> ;
    rdf:value "Reference corpus Middle High German" .

<https://swedracor.clscor.io/entity/appellation/1> a crm:E41_Appellation ;
    crm:P2_has_type <https://core.clscor.io/entity/type/appellation_type/full_title> ;
    rdf:value "Swedish Drama Corpus" .
```

This is not a simple text rendering (note that the prefix declarations are not repeated) but an `rdflib` serialization! 
`TemplateGraphConverter.serialize` is a proxy for `rdflib.Graph.serialze`, so any serialization format can be generated.


### Callable converters
TabulaRDF provides two main approaches for pure Python/callable based table to RDF conversions, the `RowGraphConverter` class and `FieldGraphConverter` class.

`RowGraphConverter` takes a dataframe and a Python callable which takes a dict parameter and is responsible for returning a graph instance;
for every row iteration over the dataframe this callable gets passed the row data as a dictionary; the generated subgraphs ("row graphs") are merged into a main graph.

```python
import pandas as pd

from jinja2 import Template
from tabulardf import RowGraphConverter

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF

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

dataframe = pd.DataFrame(data=table)


def row_rule(row_data: dict) -> Graph:
    crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    subject_uri = URIRef(f"https://{row_data['id'].lower()}.clscor.io/entity/appellation/1")

    triples = [
        (
            subject_uri,
            RDF.type,
            crm["E41_Appellation"]
        ),
        (
            subject_uri,
            crm["P2_has_type"],
            URIRef("https://core.clscor.io/entity/type/appellation_type/full_title")
        ),
        (
            subject_uri,
            RDF.value,
            Literal(row_data["full_title"])
        )
    ]

    graph = Graph()

    for triple in triples:
        graph.add(triple)

    return graph


converter = RowGraphConverter(
    dataframe=dataframe,
    row_rule=row_rule)

print(converter.serialize())
```

`FieldGraphConverter` on the other hand iterates over every field for every row in a dataframe; it applies callables to every field according to a mapping of column header names and callables responsible for returning a subgraph per field ("field graphs") which are then merged into a main graph.
Callables in such are rule mapping are of arity 3, they receive 
- `subject_field` (according to the `FieldGraphConverter`'s `subject_column` parameter), 
- `object_field` (i.e. the value of the current field) and 
- `store` (a class level dictionary for caching data).

```python
import pandas as pd

from jinja2 import Template
from tabulardf import FieldGraphConverter

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF

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

dataframe = pd.DataFrame(data=table)


def id_rule(subject_field, object_field, store) -> Graph:
    subject_uri = URIRef(f"https://{subject_field}.clscor.io/entity/appellation/1")
    crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

    triples = [
        (
            subject_uri,
            RDF.type,
            crm["E41_Appellation"]
        ),
        (
            subject_uri,
            crm["P2_has_type"],
            URIRef("https://core.clscor.io/entity/type/appellation_type/full_title")
        )
    ]

    graph = Graph()

    for triple in triples:
        graph.add(triple)

    return graph


def full_title_rule(subject_field, object_field, store) -> Graph:
    subject_uri = URIRef(f"https://{subject_field}.clscor.io/entity/appellation/1")

    graph = Graph()
    graph.add((subject_uri, RDF.value, Literal(object_field)))

    return graph


column_rules = {
    "id": id_rule,
    "full_title": full_title_rule
}


converter = FieldGraphConverter(
    dataframe=dataframe,
    subject_column="id",
    subject_rule=str.lower,
    column_rules=column_rules)

print(converter.serialize())
```

If `subject_rule` is supplied, `subject_field` in a `column_rule` callable will be what `subject_rule` computes it to be.
As mentioned, `store` is a class level attribute for sharing state between callables.

Both RowgraphConverter and FieldGraphConverter produce the same output.


### TaCL
TaCL is a humble CLI for tabulaRDF template conversions.
[todo: description + examples]
