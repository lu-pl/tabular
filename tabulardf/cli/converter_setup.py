"""Functionality for setting up a TemplateConverter for the TabulaRDF CLI."""

import pathlib

from typing import Any, Optional

from tabulardf import TemplateConverter
from tabulardf.cli.dataframe_utils import (
    get_dataframe_from_file,
    partition_dataframe
)
from tabulardf.cli.context_module import load_module, get_namespace_mapping


# add data parameter for TemplateConverter!!! -> --context-module flag
def initialize_converter(converter_type: type[TemplateConverter],
                         table: pathlib.Path,
                         template: pathlib.Path,
                         column: Optional[str] = None,
                         rows: Optional[tuple[Any, ...]] = None,
                         context_module: pathlib.Path | None = None,
                         ) -> TemplateConverter:
    """Initialize a TemplateConverter.

    Get and optionally partition a dataframe and initialze a
    TemplateConverter according to converter_type.
    """
    # 1. get a dataframe
    dataframe = get_dataframe_from_file(table)

    # 1.1 optional: partition a dataframe
    if column:  # column and rows are mutually dependent in the CLI
        dataframe = partition_dataframe(
            dataframe=dataframe,
            column=column,
            rows=rows
        )

    # 1.2 optional: provide a module context
    if context_module:
        module_name = context_module.stem
        # load the module
        module = load_module(context_module, module_name)
        # get a module dict
        namespace_mapping = get_namespace_mapping(module)

        data = {module_name: namespace_mapping}
    else:
        data = None

    # 2. get a TemplateConverter
    converter = converter_type(
        dataframe=dataframe,
        template=template,
        data=data
    )

    return converter
