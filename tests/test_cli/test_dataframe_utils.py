"""Pytest entry point for cli_utils tests."""

import itertools
import pytest
import uuid

from typing import Callable

import pandas as pd

from tabular.cli.dataframe_utils import (
    EXTENSION_READ_METHODS,
    UnknownExtensionError,
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
    ...


def test_partition_dataframe():
    ...


test_get_dataframe_try_hard()
