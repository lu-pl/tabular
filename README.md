![<img src="lodkit.png" width=10% height=10%>](https://raw.githubusercontent.com/lu-pl/tabular/main/tabulardf_logo_small.png)

# TabulaRDF
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

TabulaRDF - Functionality for DataFrame to RDF conversions.

Although TabulaRDF was primarily designed for table to RDF conversions, the `TemplateConverter` class should be general enough to allow conversions to basically any target format.

Just like the `TemplateGraphConverter` class parses renderings into an `rdflib.Graph` instance, renderings could e.g. also get parsed into an `lxml.etree`.

## Requirements

* python >= 3.11




## Usage
<!-- TabulaR provides two main approaches for table conversions, a template-based approach using the [Jinja2](https://jinja.palletsprojects.com/) templating engine and a pure Python/callable-based approach. -->

<!-- ### Template converters -->

<!-- Template converters are based on the generic `TemplateConverter` class which allows to iterate over a dataframe and pass table data to Jinja renderings. -->

<!-- Two different render strategies are available through the `render` method and the `render_by_row` method respectively. -->

<!-- - With the `render` method, every template gets passed the entire table data as "table_data";  -->
<!--   this means that iteration must be done in the template. -->
<!-- - With the `render_by_row` method, for every row iteration the template gets passed the current row data (as "row_data") only; -->
<!--   so iteration is done at the Python level, not in the template. -->
  
<!-- #### Example -->

<!-- The following templates are designed to produce the same result using different rendering strategies. -->

<!-- Here the table iteration is done in the template: -->
<!-- ```jinja -->
<!-- {# table_template.j2 #} -->

<!-- {% for row in table_data %} -->
<!-- <book category="{{ row['category'] }}"> -->
<!--   <title>{{ row["title"] }}</title> -->
<!--   <author>{{ row["author"] }}</author> -->
<!--   <year>{{ row["year"] }}</year> -->
<!--   <price>{{ row["price"] }}</price> -->
<!-- </book> -->
<!-- {% endfor %} -->
<!-- ``` -->

<!-- This template on the other hand depends on external iteration: -->
<!-- ```jinja -->
<!-- {# row_template.j2 #} -->

<!-- <book category="{{ row_data['category'] }}"> -->
<!--   <title>{{ row_data["title"] }}</title> -->
<!--   <author>{{ row_data["author"] }}</author> -->
<!--   <year>{{ row_data["year"] }}</year> -->
<!--   <price>{{ row_data["price"] }}</price> -->
<!-- </book> -->
<!-- ``` -->

<!-- Below, `table_converter` uses the `table_template.j2` template and the `render` method and `row_converter` uses the `row_template.j2` template and the `render_by_row` method. -->

<!-- Both converters yield the same result. -->

<!-- ```python -->
<!-- table = [ -->
<!--     { -->
<!--         'category': 'programming', -->
<!--         'title': 'Fluent Python', -->
<!--         'author': 'Luciano Ramalho', -->
<!--         'year': 2022, -->
<!--         'price': 50.99 -->
<!--     }, -->
<!--     { -->
<!--         'category': 'web', -->
<!--         'title': 'Learning XML', -->
<!--         'author': 'Erik T. Ray', -->
<!--         'year': 2003, -->
<!--         'price': 39.95 -->
<!--     } -->
<!-- ] -->

<!-- df = pd.DataFrame(data=table) -->


<!-- table_converter = TemplateConverter( -->
<!--     dataframe=df, -->
<!--     template="./table_template.j2" -->
<!-- ) -->

<!-- print(table_converter.render()) -->

<!-- row_converter = TemplateConverter( -->
<!--     dataframe=df, -->
<!--     template="./row_template.j2" -->
<!-- ) -->

<!-- print("".join(row_converter.render_by_row())) -->
<!-- ``` -->

<!-- Note that `TemplateConverter` produces *plain text* which in this case happens to be XML. A custom converter subclassing `TemplateConverter` can parse renderings into arbitrary object abstractions - see the `TemplateGraphConverter` class which parses renderings into an `rdflib.Graph` instance. -->

<!-- > Obviously valid XML requires a root element; while it is easy to generate valid XML with the "table" render strategy (using the `render` method), the root element must be added externally (e.g. by passing the converter renderings to another template containing the root node or by embedding the `render_by_row` generator in another Iterable) if the "row" render strategy (using the `render_by_row` method) is used. -->

<!-- ### Python/callable converters -->
<!-- [todo] -->

<!-- ## Contribution -->

<!-- Please feel free to open issues or pull requests. -->
