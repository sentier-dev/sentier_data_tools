# sentier_data_tools

[![PyPI](https://img.shields.io/pypi/v/sentier_data_tools.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/sentier_data_tools.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/sentier_data_tools)][pypi status]

[![Read the documentation at https://sentier_data_tools.readthedocs.io/](https://img.shields.io/readthedocs/sentier_data_tools/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/sentier-dev/sentier_data_tools/actions/workflows/python-test.yml/badge.svg)][tests]

[pypi status]: https://pypi.org/project/sentier_data_tools/
[read the docs]: https://sentier_data_tools.readthedocs.io/
[tests]: https://github.com/sentier-dev/sentier_data_tools/actions?workflow=Tests

## Introduction

`sentier_data_tools`, in combination with the common vocabularies at https://vocab.sentier.dev/, for a proof of concept for the next generation of sustainability assessment that [Départ de Sentier](https://www.d-d-s.ch/) is building.

* Instead of linear system and fixed single coefficients, we have computational models which gather data vectors from a data store
* Instead of a custom taxonomy, we build on existing standards in an [open and collaborative fashion](https://github.com/sentier-dev/sentier_vocab)

`sentier_data_tools` provides:

* A local data store backend for storing LCA, MFA, industrial ecology, and other data
* A set of classes to interact with the Sentier online vocabulary, including graph traversal and unit conversion
* A base class for models which will be deployed to the `sentier.dev` platform
* A complete example with electrolysis; see {TBD}

## Installation

You can install _sentier_data_tools_ via [pip] from [PyPI]:

```console
$ pip install sentier_data_tools
```

It is also available on [anaconda](https://anaconda.org/cmutel/sentier_data_tools).

## Dataframes

`sentier_data_tools` assumes that all *data* is stored in Pandas DataFrames. Because we store additional metadata about column units, comments, and assemblies using [pandas_flavor](https://github.com/pyjanitor-devs/pandas_flavor), the use of other DataFrame alternatives probably won't work.

There are several kinds of dataframes which can be stored in the local data store:

### All column labels are IRIs in https://vocab.sentier.dev/

This is an absolute requirement of `sentier_data_tools` - we need to know what each column means, and that data must be stored in our common vocabulary. An IRI is like a long URL - for example, our IRI for "Ferro-silico-magnesium" is `http://data.europa.eu/xsp/cn2024/720299300080`. This looks unwieldy, and you certainly don't want to type it by hand. But this resource identifier allows us to [learn a lot about this product](https://vocab.sentier.dev/products/en/page/?uri=http%3A%2F%2Fdata.europa.eu%2Fxsp%2Fcn2024%2F720299300080), including its label in many languages, links to IRIs for the same concept in other taxonomies, and its tariff codes. And we're just getting started - here's [the kind of data we aspire to](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI%3A28112).

To make working with these concepts easier `sentier_data_tools` allows you to specify aliases in your models.

### `DataframeKind.PARAMETERS`

This is the most common kind of dataframe. It provides technical performance specifications or other input values needed to run functions. These dataframes are often wide, with 20 or more columns, and their columns will commonly refer to modelling terms instead of products or processes.

Here are some examples:

* Model-specific electrolyzer performance values such as output pressure, electrical efficiency, maintenance period, and required input water quality
* Waste treatment stage material recovery fractions by material, treatment stage, and treatment plant
* The maximum power generation, net annual generation, and beneficial owner of every coal-fired power plant on Earth

`PARAMETERS` are **not** intended to be used in proportion to another number. They do require specifying a spatial and temporal validity context (default is Earth and last five years to next five years), as well as a product. Because the `sentier.dev` vocabulary is hierarchical, this product can be general or very specific. We use this product value to find the data we need for a given model.

### `DataframeKind.BROAD`

Broad data about society and economy, including future scenarios. Can include installed capacities or other data which can be used directly for creating virtual markets. Can include prices.

Not intended to be used in proportion to another number. Requires a spatial and temporal context, but *doesn't* require a or preclude a product.

### `DataframeKind.BOM`

Bill of materials (including energy and services) to produce a good or assembly. **Always** given in relation to a fixed output value, such as 2 kilograms of steel per one bicycle frame.

Requires a spatial and temporal context and a product.

### `DataframeKind.COMPOSITION`

Specific data on composition on composition of goods and wastes. Different than model parameters in that these can be individual elements (e.g. for MFA), but are related to a given output (product or economic sector). Not completely developed yet.

## Model template

`sentier.dev` models should inherit `sentier_data_tools.SentierModel` for the time being.

Making good choices when building models is hard! We want power and simplicity at the same time.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_sentier_data_tools_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://sentier_data_tools.readthedocs.io/en/latest/usage.html
[License]: https://github.com/sentier-dev/sentier_data_tools/blob/main/LICENSE
[Contributor Guide]: https://github.com/sentier-dev/sentier_data_tools/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/sentier-dev/sentier_data_tools/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yaml
```

activating the environment

```bash
conda activate sphinx_sentier_data_tools
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
