"""DataFrame utilites for the TabulaR CLI."""

import inspect
import pathlib

from typing import Callable, Generator, Iterable, Mapping

import pandas as pd


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


def _get_pandas_read_methods() -> dict[str, Callable]:
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


# this needs thorough logging
# refactor: this should be called _get_read_method_by/from<...>
def _get_dataframe_try_hard(file: pathlib.Path) -> pd.DataFrame:
    """Try hard to get a dataframe from a pathlib.Path.

    Every pandas read method is tried, the result from the first method
    able to produce a dataframe is returned.
    """
    for read_method in _get_pandas_read_methods().values():
        try:
            dataframe = read_method(file)
            # maybe return read_method instead? probably!
            # todo: this + reflect change in get_dataframe_from_file
            return dataframe
        except Exception:
            pass

    raise Exception("Could not find applicable read method.")


def get_dataframe_from_file(file: pathlib.Path):
    """Get a dataframe from a pathlib.Path.

    First check against a mapping of extensions to determine a read method;
    if that fails try hard to get a dataframe anyway by calling one read method
    after another and going with the first that applies.
    """
    # note: if the extension mapping fails, there must extensive logging!
    ...

    extension = file.suffix.lstrip(".")

    try:
        read_method = _get_read_method_by_extension(extension)
        dataframe = read_method(file)
    except UnknownExtensionError:
        # try harder
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
    # why is this needed again?
    def _rows(rows: Iterable) -> Generator:
        """String/integer handling kludge."""
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
