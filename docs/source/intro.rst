.. _intro:

Introduction
============

Functions Arranged as a Graph
-----------------------------

The ``async-graph-data-flow`` package provides a framework for arranging
functions in a directed acyclic graph (DAG).

.. mermaid::

    flowchart LR

    A[func1] --> B[func2]
    B --> C[func3]
    B --> D[func4]
    C --> E[func5]
    D --> E

Each function must be an asynchronous generator function,
which means it is defined with the ``async`` keyword
and yields something.

.. code-block:: python

    async def func1(arg1, arg2):
        ...
        yield output

For two nodes to be connected correctly in terms of function definition,
the source node's function must yield what the destination node's function
expects as input.

.. mermaid::

    flowchart LR

    START[ ] -.-> A
    B -.-> STOP[ ]
    A["async def func2(...):\n&nbsp;&nbsp;&nbsp;&nbsp;...\n&nbsp;&nbsp;&nbsp;&nbsp;yield <strong>foo, bar</strong>"] --> B["async def func3(<strong>foo, bar</strong>):\n&nbsp;&nbsp;&nbsp;&nbsp;...\n&nbsp;&nbsp;&nbsp;&nbsp;yield ..."]
    style A text-align:left
    style B text-align:left
    style START fill-opacity:0, stroke-opacity:0;
    style STOP  fill-opacity:0, stroke-opacity:0;


Queues and Tasks
----------------
