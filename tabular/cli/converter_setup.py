"""Functionality for setting up a TemplateConverter for the TabulaR CLI."""

import pathlib

from typing import Any, Optional

from tabular import TemplateConverter
from tabular.cli.dataframe_utils import (
    get_dataframe_from_file,
    partition_dataframe
)


def initialize_converter(converter_type: type[TemplateConverter],
                         table: pathlib.Path,
                         template: pathlib.Path,
                         column: Optional[str] = None,
                         rows: Optional[tuple[Any, ...]] = None
                         ) -> TemplateConverter:
    """Initialize a TemplateConverter.

    Get and optionally partition a dataframe and initialze a
    TemplateConverter according to converter_type.
    """
    # 1. get a dataframe
    dataframe = get_dataframe_from_file(table)

    # 1.2. optional: partition a dataframe
    if column:  # column and rows are mutually dependent in the CLI
        dataframe = partition_dataframe(
            dataframe=dataframe,
            column=column,
            rows=rows
        )

    # 2. get a TemplateConverter
    converter = converter_type(
        dataframe=dataframe,
        template=template
    )

    return converter
