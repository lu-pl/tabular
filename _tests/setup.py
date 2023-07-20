"""Setup for actual testing."""

from itertools import count

from jinja2 import Environment, FileSystemLoader, select_autoescape

from table_partitions import swedracor_partition, rem_partition
from tabular import TemplateGraphConverter


env = Environment(
    loader=FileSystemLoader("."),
    autoescape=select_autoescape()
)

template = env.get_template("./templates/corpustable_template.ttl")


def counter(cnt=count()):
    """Stateful counter.

    Primitive wrapper for itertools.count.
    Note that state is maintained by default arg.
    """
    return next(cnt)


template_converter = TemplateGraphConverter(
    # dataframe=swedracor_partition,
    dataframe=rem_partition,
    template=template,
    data={"fns": {"counter": counter}}
)

print(template_converter.serialize())
