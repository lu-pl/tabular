"""just a test"""

from tabular import TemplateConverter
from tests.data import templates_path, tables



template_converter = TemplateConverter(
    dataframe=tables.bookstore_df,
    template=templates_path / "books_table.j2")

# print(template_converter.render())

def test_fun():

    template_converter = TemplateConverter(
        dataframe=tables.bookstore_df,
        template=templates_path / "books_table.j2")

    rendering = template_converter.render()
    print(rendering)
    assert rendering
