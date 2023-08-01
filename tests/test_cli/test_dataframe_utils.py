"""Pytest entry point for cli_utils tests."""

import itertools
import pytest
import uuid

from typing import Callable

import pandas as pd

from tabular.cli.dataframe_utils import (
    EXTENSION_READ_METHODS,
    UnknownExtensionError,
    get_dataframe_from_file,
    partition_dataframe,
    _get_dataframe_try_hard,
    _get_pandas_read_methods,
    _get_read_method_by_extension,
    )

from tests.data import tables_path


def test_get_read_method_by_extension():
    """Test for cli._get_read_method_by_extension.

    Run the method on every extension in the extension mapping.
    """
    all_extensions = itertools.chain(*EXTENSION_READ_METHODS.keys())

    for extension in all_extensions:
        assert _get_read_method_by_extension(
            extension=extension,
            method_mapping=EXTENSION_READ_METHODS
            )


def test_get_read_method_by_extension_expected_fail():
    """Test for cli._get_read_method_by_extension.

    Use a mock extension in _get_read_method_by_extension and fail expectedly.
    """

    mock_extension = str(uuid.uuid4())

    with pytest.raises(UnknownExtensionError):
        _get_read_method_by_extension(
            extension=mock_extension,
            method_mapping=EXTENSION_READ_METHODS
            )


def test_get_pandas_read_methods():
    pandas_read_methods = _get_pandas_read_methods()

    # check if read methods are being fetched
    assert pandas_read_methods

    # check keys
    assert all(
        lambda x: isinstance(x, str)
        for read_method
        in pandas_read_methods
        )

    # check values
    assert all(
        lambda x: isinstance(x, Callable)
        for read_method
        in pandas_read_methods
        )


# todo: this needs changing after df/method refactor!
def test_get_dataframe_try_hard():
    """..."""
    test_csv_path = tables_path / "test.csv"

    dataframe = _get_dataframe_try_hard(test_csv_path)

    assert isinstance(dataframe, pd.DataFrame)
    assert not dataframe.empty


def test_get_dataframe_from_file():
    """Test for get_dataframe_fm_file.

    Get a dataframe from both a file with a registered extension
    and an unknown extension (holding the same data).
    """
    test_csv_path = tables_path / "test.csv"
    test_txt_path = tables_path / "test.txt"

    dataframe_from_extension = get_dataframe_from_file(test_csv_path)
    dataframe_from_trial = get_dataframe_from_file(test_txt_path)

    # both dataframes should be non-empty
    assert not dataframe_from_extension.empty
    assert not dataframe_from_trial.empty

    # the difference of the two dataframes should be empty
    assert dataframe_from_extension.compare(dataframe_from_trial).empty


def test_partition_dataframe():

    test_csv_path = tables_path / "test.csv"
    dataframe = get_dataframe_from_file(test_csv_path)

    partition_by_column_1 = partition_dataframe(
        dataframe=dataframe,
        column="column 1 name",
        rows=("first row data 1", "second row data 1")
        )

    partition_by_column_2 = partition_dataframe(
        dataframe=dataframe,
        column="column 2 name",
        rows=("first row data 2", "second row data 2")
        )

    # partitions should be equal, i.e. the difference should be empty
    assert partition_by_column_1.compare(partition_by_column_2).empty
