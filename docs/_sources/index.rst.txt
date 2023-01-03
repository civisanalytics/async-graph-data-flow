.. async-graph-data-flow documentation master file, created by
   sphinx-quickstart on Sat Dec  3 11:11:02 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

..  _index:

async-graph-data-flow
=====================

.. image:: https://badge.fury.io/py/async-graph-data-flow.svg
   :target: https://pypi.python.org/pypi/async-graph-data-flow
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/async-graph-data-flow.svg
   :target: https://pypi.python.org/pypi/async-graph-data-flow
   :alt: Supported Python versions

``async-graph-data-flow`` is a Python library for executing asynchronous functions
that pass data along a directed acyclic graph (DAG).

Features
--------

* **Functions organized as a graph** 🕸

Your asynchronous functions are nodes in the DAG.
Each node yields data to its destination nodes.

* **Let data flow along the graph** 🥂

It's like how champagne flows along a champagne tower.
Graph execution continues as long as there's still data between two connected nodes.

* **Customizable start nodes** 🧨

By default, graph execution begins with nodes that have no incoming nodes,
but you can choose to start the graph execution from any nodes.

* **Data flow statistics** ⏳

Utilities are available to keep track of data volumes at each node
and optionally log such info at a regular time interval.

* **Exception handling** 💥

Choose whether to halt execution at a specific node or any node.

* **Lightweight** 🪶

The source code is only about 400 lines!

* **Pure Python** 🐍

The library is built on top of ``asyncio`` from the Python standard library, with no third-party dependencies.

Download and Install
--------------------

.. code-block:: shell

   pip install async-graph-data-flow

Usage
-----

Start with :ref:`quickstart`, and then get inspired by :ref:`more_examples`.
Don't forget to check out the :ref:`api` as well.

Under the Hood
--------------

``async-graph-data-flow`` chains asynchronous functions together
with a :class:`~asyncio.Queue` instance between two functions in the graph.
A queue keeps track of the data items yielded from a source node and feeds them
into its destination node.

License
-------

BSD 3-Clause License.

Links
-----

* This documentation: https://civisanalytics.github.io/async-graph-data-flow
* Source code and bug tracker: https://github.com/civisanalytics/async-graph-data-flow

Authors
-------

This library is authored by Samuel Asirifi, Gbolahan Okerayi, and Jackson Lee at Civis Analytics.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   quickstart
   more_examples
   api
