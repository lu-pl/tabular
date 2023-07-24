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

The following templates are designed to produce the same result using different rendering strategies.

Here the table iteration is done in the template:
```jinja
{# table_template.j2 #}

{% for row in table_data -%}
<book category="{{ row['category'] }}">
  <title>{{ row["title"] }}</title>
  <author>{{ row["author"] }}</author>
  <year>{{ row["year"] }}</year>
  <price>{{ row["price"] }}</price>
</book>
{%- endfor %}
```

The second template on the other hand depends on external iteration:
```jinja
{# row_template.j2 #}

<book category="{{ row_data['category'] }}">
  <title>{{ row_data["title"] }}</title>
  <author>{{ row_data["author"] }}</author>
  <year>{{ row_data["year"] }}</year>
  <price>{{ row_data["price"] }}</price>
</book>
```

Now `table_converter` uses the `table_template.j2` template and the `render` method,
while `row_converter` uses the `row_template.j2` template and the `render_by_row` method.

Both converters yield the same results.

```python
table = [
    {
        'category': 'children',
        'title': 'Harry Potter',
        'author': 'J K. Rowling',
        'year': 2005,
        'price': 29.99
    },
    {
        'category': 'web',
        'title': 'Learning XML',
        'author': 'Erik T. Ray',
        'year': 2003,
        'price': 39.95
    }
]

df = pd.DataFrame(data=table)


table_converter = TemplateConverter(
    dataframe=df,
    template="./table_template.j2"
)

print(table_converter.render())

row_converter = TemplateConverter(
    dataframe=df,
    template="./row_template.j2"
)

print(row_converter.render_by_row())
```

* Warning: It is not yet possible to pass a string representing a path to the template parameter; this shall be implemented shorty.
  For now the template parameter expects a `jinja2.Template` object.
  
### Python/callable converters


## Contribution

Please feel free to open issues or pull requests.
