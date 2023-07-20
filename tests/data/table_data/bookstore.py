"""Bookstore pd.Dataframe data."""

import importlib.resources
import pandas as pd

bookstore_xml = (
    importlib.resources
    .files("tests.data.targets.xml")
    .joinpath("bookstore.xml")
)

with open(bookstore_xml) as f:
    bookstore_df = pd.read_xml(f)
