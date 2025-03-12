# async-graph-data-flow

[![PyPI version](https://badge.fury.io/py/async-graph-data-flow.svg)](https://pypi.org/project/async-graph-data-flow/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/async-graph-data-flow.svg)](https://pypi.org/project/async-graph-data-flow/)
[![CircleCI Builds](https://circleci.com/gh/civisanalytics/async-graph-data-flow.svg?style=shield)](https://circleci.com/gh/civisanalytics/async-graph-data-flow)

## Full Documentation

Please visit https://async-graph-data-flow.readthedocs.io

Please also check out this
[blog post](https://www.civisanalytics.com/blog/open-source-software-release-introducing-async-graph-data-flow-a-python-library-for-efficient-data-pipelines/)
introducing this package.

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

## Building Documentation

We use the Sphinx framework. The documentation source files are in `docs/`.
These files can be updated as necessary.

The public documentation is accessible at https://async-graph-data-flow.readthedocs.io.
The doc build is configured by `.readthedocs.yaml`. 
Normally, even when we need to update the documentation or make a new release of async-graph-data-flow,
neither this configuration YAML file nor Civis's account on the Read the Docs site need any updates.
The builds by the Read The Docs site generate the necessary files (the HTML pages and other things)
for the public documentation. All these auto-generated files are explicitly not versioned (see `.gitignore`).

To build the documentation locally (for testing and development),
install the full doc-related dependencies: `pip install -r docs/requirements.txt`,
then run `sphinx-build -b html docs/ docs/build/`.
