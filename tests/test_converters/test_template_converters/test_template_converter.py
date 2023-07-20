"""Pytest entry point for TemplateConverter tests."""

from tabular import TemplateConverter

from tests.data import bookstore_df, bookstore_target, bookstore_template

bookstore_template_converter = TemplateConverter(
    dataframe=bookstore_df,
    template=bookstore_template
)

# bookstore_template_converter._apply_to_renderings(print)

# for item in bookstore_template_converter.render_by_row():
#     print(item)

# import xml.etree.ElementTree as et

# rendering = bookstore_template_converter.render()
# xml = et.XML(rendering)
# et.indent(xml)
# print(et.tostring(xml, encoding="unicode"))

# rendering = bookstore_template_converter.render()
# print(rendering)
