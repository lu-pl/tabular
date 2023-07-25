"""Bookstore pd.Dataframe data."""

import importlib.resources
import pandas as pd

from tests.data import targets_xml_path


# bookstore
_bookstore_path = targets_xml_path / "bookstore.xml"

with open(_bookstore_path) as f:
    _bookstore_df = pd.read_xml(f)

# corpusTable partial
_cortab_partial = [
    {
        "corpusAcronym": "ReM",
        "corpusName": "Reference corpus Middle High German"
    },
    {
        "corpusAcronym": "SweDraCor",
        "corpusName": "Swedish Drama Corpus"
    }
]


# export
bookstore_df = _bookstore_df
cortab_partial_df = pd.DataFrame(data=_cortab_partial)
