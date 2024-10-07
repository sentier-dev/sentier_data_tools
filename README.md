# sentier_data_tools

[![PyPI](https://img.shields.io/pypi/v/sentier_data_tools.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/sentier_data_tools.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/sentier_data_tools)][pypi status]
[![License](https://img.shields.io/pypi/l/sentier_data_tools)][license]

[![Read the documentation at https://sentier_data_tools.readthedocs.io/](https://img.shields.io/readthedocs/sentier_data_tools/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/sentier-dev/sentier_data_tools/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/sentier-dev/sentier_data_tools/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/sentier_data_tools/
[read the docs]: https://sentier_data_tools.readthedocs.io/
[tests]: https://github.com/sentier-dev/sentier_data_tools/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/sentier-dev/sentier_data_tools
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _sentier_data_tools_ via [pip] from [PyPI]:

```console
$ pip install sentier_data_tools
```

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
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_sentier_data_tools
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```