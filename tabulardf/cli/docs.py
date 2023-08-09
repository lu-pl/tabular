"""Dataclasses for documenting CLI arguments and options."""

from dataclasses import dataclass


@dataclass
class CLIDocs:
    """Data container for TabulaR CLI documentation."""

    column: str
    rows: str
    render_by_row: str
    format: str
    context_module: str


docs = CLIDocs(

    column=(
        "Specifies a column by name for partitioning. "
        "Partitions are defined by a column and the row(s) the partition shall contain. "
        "--column is mandatory if --rows is given and vice versa."
    ),

    rows=(
        "Specifies a row by name for partitioning. "
        "This flag takes an arbitrary number of arguments (internally a TUPLE). "
        "Partitions are defined by a column and the row(s) the partition shall contain. "
        "--rows is mandatory if --column is given and vice versa."
    ),

    render_by_row=(
        "Boolean flag. If active, the render_by_row strategy is applied for rendering. "
        "For rendering strategies see <link>."
    ),

    format=(
        "Specifies a format for RDF serialization. "
        "This is a proxy for rdflib.Graph serialize."
    ),

    context_module=(
        "Load all public symbols of a Python module into the template context. "
        "Symbols will be available in a dictionary named after the module. "
        "E.g. this allows to define a set of functions for use in a template."
    )
)
