# async-graph-data-flow

[![PyPI version](https://badge.fury.io/py/async-graph-data-flow.svg)](https://pypi.org/project/async-graph-data-flow/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/async-graph-data-flow.svg)](https://pypi.org/project/async-graph-data-flow/)
[![CircleCI Builds](https://circleci.com/gh/civisanalytics/async-graph-data-flow.svg?style=shield)](https://circleci.com/gh/civisanalytics/async-graph-data-flow)

## Full Documentation

Please visit https://civisanalytics.github.io/async-graph-data-flow

## License

BSD 3-Clause License. Please see `LICENSE.txt` in the GitHub source code for details.

## Setting up a Development Environment

The latest code under development is available on GitHub at
https://github.com/civisanalytics/async-graph-data-flow.
To obtain this version for experimental features or for development:

```bash
git clone https://github.com/civisanalytics/async-graph-data-flow.git
cd async-graph-data-flow
pip install -e ".[dev]"
```

To run tests and styling checks:

```bash
pytest
flake8 src tests examples
black --check src tests examples
```

## For Maintainers

To update the Sphinx documentation,
the source files that need editing are under `docs/source/`;
everything else under `docs/` is auto-generated.
After the manual updates under `docs/source/` are ready,
the HTML pages are updated as follows:

```bash
rm -r docs/_sources docs/_static && rm docs/*.html

# Run the following command *twice* -- certain HTML updates only show up after multiple `sphinx-build` runs.
sphinx-build docs/source docs
```
