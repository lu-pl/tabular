"""DataFrame utilites for the TabulaR CLI."""

from typing import Any

import pandas as pd


def partition_table(dataframe: pd.DataFrame,
                    column: str,
                    rows: tuple[Any, ...]
                    ) -> pd.DataFrame:
    """Generate table partition of a pd.DataFrame.

    A partition is defined by a column reference
    and a set of 1+ row reference(s).
    """

    def _rows(rows: tuple[Any, ...]):
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
