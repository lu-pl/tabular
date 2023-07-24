# TabulaR
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

TabulaR - Functionality for DataFrame to RDF conversions.

Note that although TabulaR was primarily designed for table to RDF conversions, the `TemplateConverter` class should be general enough to allow conversions to basically any target format.
See e.g. the `TemplateXMLConverter` class. [todo]

## Requirements

* python >= 3.10

## Usage
TabulaR provides two main approaches for table conversions, a template-based approach using the [Jinja2](https://jinja.palletsprojects.com/) templating engine and a pure Python/callable-based approach.

### Template converters

Template converters are based on the generic `TemplateConverter` class which iterates over a dataframe and passes table data to Jinja renderings.

Two different render strategies are available through the `render` method and the `render_by_row` method respectively.

- With the `render` method, every template gets passed the entire table data as "table_data"; 
  this means that iteration must be done in the template.
- With the `render_by_row` method, for every row iteration the template gets passed the current row data only;
  so iteration is done at the Python level, not in the template.
  
#### Example

```jinja
{% for row in table_data -%}
<book category="{{ row['category'] }}">
  <title>{{ row["title"] }}</title>
  <author>{{ row["author"] }}</author>
  <year>{{ row["year"] }}</year>
  <price>{{ row["price"] }}</price>
</book>
{%- endfor %}
```

```jinja
<book category="{{ row_data['category'] }}">
  <title>{{ row_data["title"] }}</title>
  <author>{{ row_data["author"] }}</author>
  <year>{{ row_data["year"] }}</year>
  <price>{{ row_data["price"] }}</price>
</book>
```

### Python/callable converters


## Contribution

Please feel free to open issues or pull requests.
