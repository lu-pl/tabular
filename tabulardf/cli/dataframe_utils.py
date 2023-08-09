"""DataFrame utilites for the TabulaRDF CLI."""

import inspect
import logging
import pathlib

from typing import Callable, Generator, Iterable, Mapping
from types import FunctionType

import pandas as pd


# call basicConfig manually to create handlers
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


EXTENSION_READ_METHODS: Mapping[tuple, Callable] = {
    ("csv", ): pd.read_csv,
    ("xls", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt"): pd.read_excel
}


class UnknownExtensionError(Exception):  # noqa: D204
    """Exception type for unknown file extensions."""
    pass


def _get_read_method_by_extension(extension: str,
                                  method_mapping: Mapping[
                                      tuple, Callable
                                  ] = EXTENSION_READ_METHODS) -> Callable:
    """Try to get a pandas read method given a file extension."""
    extension = extension.lstrip(".")

    for key, value in EXTENSION_READ_METHODS.items():
        if extension in key:
            read_method = value
            return read_method

    raise UnknownExtensionError(f"Unknown extension '{extension}'.")


# FunctionType vs. Callable:
# actually dict+FunctionType is more precise here than e.g. Mapping+Callable
def _get_pandas_read_methods() -> dict[str, FunctionType]:
    """Get all pandas methods starting with 'read_'.

    For every match a mapping of method name and function object is returned.
    """
    pd_members = inspect.getmembers(pd)
    pandas_read_methods = {
        name: member for name, member
        in pd_members
        if name.startswith("read_") and inspect.isfunction(member)
    }

    return pandas_read_methods


def _get_dataframe_try_hard(file: pathlib.Path) -> pd.DataFrame:
    """Try hard to get a dataframe from a pathlib.Path.

    Every pandas read method is tried, the result from the first method
    able to produce a dataframe is returned.
    """
    for read_method in _get_pandas_read_methods().values():
        try:
            logger.info(f"Trying '{read_method.__name__}' to obtain dataframe from {file.name}.")
            dataframe = read_method(file)

            logger.info(f"Successfully obtained dataframe with '{read_method.__name__}'.")
            return dataframe
        except Exception as e:
            logger.warning(f"Unable to obtain dataframe with '{read_method.__name__}': {e}")
            pass

    logging.critical("Unable to obtain dataframe. Exiting.")
    raise Exception("Could not find applicable read method.")


def get_dataframe_from_file(file: pathlib.Path):
    """Get a dataframe from a pathlib.Path.

    First check against a mapping of extensions to determine a read method;
    if that fails try hard to get a dataframe anyway by calling one read method
    after another and going with the first that applies.
    """
    # note: if the extension mapping fails, there must extensive logging!
    extension = file.suffix.lstrip(".")

    try:
        read_method = _get_read_method_by_extension(extension)
        dataframe = read_method(file)
    except UnknownExtensionError:
        # try harder
        logger.info(f"No known pandas read method for '{extension}'.\n"
                    "Trying to determine read method by trial.")
        dataframe = _get_dataframe_try_hard(file)

    return dataframe


def partition_dataframe(dataframe: pd.DataFrame,
                        column: str,
                        rows: Iterable
                        ) -> pd.DataFrame:
    """Generate table partition of a pd.DataFrame.

    A partition is defined by a column reference
    and a set of 1+ row reference(s).
    """

    def _rows(rows: Iterable) -> Generator:
        """Handle str/integers CLI input.

        This is needed because --rows must take any type.
        """
        for value in rows:
            try:
                value = int(value)
            except ValueError:
                pass

            yield value

    table_partition = dataframe[
        dataframe[column].isin(list(_rows(rows)))
    ]

    return table_partition
