.. async-graph-data-flow documentation master file, created by
   sphinx-quickstart on Sat Dec  3 11:11:02 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

..  _index:

async-graph-data-flow
=====================

.. meta::
   :description:
        async-graph-data-flow: Data flow along a directed acyclic graph of asynchronous generator functions
   :keywords:
        asyncio, asynchronous programming, dag, directed acyclic graph,
        asynchronous generator functions

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

* **Flexible edge behaviors between nodes** 🔄

After data is yielded from a source node and before it's received by a destination node,
you can choose to transform the data or perform any other operation on it.

* **Customizable start nodes** 🧨

By default, graph execution begins with nodes that have no incoming nodes,
but you can choose to start the graph execution from any nodes.

* **Data flow statistics** ⏳

Utilities are available to keep track of data volumes at each node
and optionally log such info at a regular time interval.

* **Exception handling** 💥

Choose whether to halt execution at a specific node or any node.

* **Lightweight** 🪶

The source code is only about 600 lines!

* **Single-machine Usage** 💻

We love Big Data™ and distributed computing,
though deep down we all know that practically we accomplish a ton of work on single machines
without those big guns.

* **Pure Python** 🐍

The library is built on top of ``asyncio`` from the Python standard library, with no third-party dependencies.

Download and Install
--------------------

.. code-block:: shell

   pip install async-graph-data-flow

Usage
-----

Start with :ref:`quickstart`.
To better understand how the library works, see :ref:`technical`.
Then get inspired by and see what features are available from :ref:`more_examples`.
Don't forget to check out the :ref:`api` as well.

License
-------

BSD 3-Clause License.

Links
-----

* `Blog post <https://www.civisanalytics.com/blog/open-source-software-release-introducing-async-graph-data-flow-a-python-library-for-efficient-data-pipelines/>`_ introducing this package
* `Source code and bug tracker <https://github.com/civisanalytics/async-graph-data-flow>`_

Authors
-------

This library is authored by Samuel Asirifi, Gbolahan Okerayi, and Jackson Lee at Civis Analytics.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   quickstart
   technical
   more_examples
   api
