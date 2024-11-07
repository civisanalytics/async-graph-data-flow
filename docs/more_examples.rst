.. _more_examples:

More Examples
=============

While some of the examples below are meant to demonstrate the features
of the ``async-graph-data-flow`` library,
others (e.g., running a synchronous function, sharing state across functions)
show what could be possible -- we aren't limited by the implemented features!
If you have questions or would like to contribute an example of your own,
please open an issue at the
`GitHub repository <https://github.com/civisanalytics/async-graph-data-flow>`_
for discussion.

Customizable Start Nodes
------------------------

When :class:`~async_graph_data_flow.AsyncExecutor`'s :func:`~async_graph_data_flow.AsyncExecutor.execute`
is called,
by default the start nodes (= nodes without incoming edges) of the graph are automatically detected and called.
To override this default behavior,
use the keyword argument ``start_nodes`` at :func:`~async_graph_data_flow.AsyncExecutor.execute`
to select which nodes to execute instead and/or supply the arguments to whichever nodes you've selected.

.. literalinclude:: ../examples/custom_start_nodes.py
   :language: python
   :emphasize-lines: 34

.. literalinclude:: ../examples/custom_start_node_args.py
   :language: python
   :emphasize-lines: 34

Graph with Nodes only and No Edges
----------------------------------

It is possible to execute a graph with nodes only and no edges.
In this case,
if ``start_nodes`` at :func:`~async_graph_data_flow.AsyncExecutor.execute` are not specified (see above),
then *all* nodes are start nodes (because all nodes don't have an incoming edge),
and therefore all nodes will execute concurrently upon graph execution.
The start nodes and their arguments at the beginning of the graph execution are available at
:attr:`~async_graph_data_flow.AsyncExecutor.start_nodes` of :func:`~async_graph_data_flow.AsyncExecutor.execute`.

.. literalinclude:: ../examples/graph_with_no_edges.py
   :language: python
   :emphasize-lines: 30,39,48

Data Flow Statistics and Logging
--------------------------------

:class:`~async_graph_data_flow.AsyncExecutor`'s :attr:`~async_graph_data_flow.AsyncExecutor.data_flow_stats`
keeps track of data volumes and errors encountered at each node.
:attr:`~async_graph_data_flow.AsyncExecutor.data_flow_stats` is a dictionary
where a key is the name of a node,
and its value is itself a dict that maps ``{"in", "out", "err"}``
to the counts of data items coming into the node,
going out of the node,
and unhandled errors from the node, respectively.

For a long-running graph execution,
it is helpful to log such data flow information at a regular time interval.
An :class:`~async_graph_data_flow.AsyncExecutor` instance has
the method :func:`~async_graph_data_flow.AsyncExecutor.turn_on_data_flow_logging`,
which you can call to turn on and configure logging.

.. literalinclude:: ../examples/data_flow_logging.py
   :language: python
   :emphasize-lines: 36-38

Concurrent Tasks Per Node
-------------------------

By default, each node creates one task at a time.
To spawn multiple, concurrent tasks from a node,
set ``max_tasks`` at :func:`~async_graph_data_flow.AsyncGraph.add_node`.

.. literalinclude:: ../examples/concurrent_tasks_per_node.py
   :language: python
   :emphasize-lines: 25

.. _Halting Graph Execution upon Exceptions:

Halting Graph Execution upon Exceptions
---------------------------------------

By default, an unhandled exception from any node does not halt the graph execution.
This behavior can be altered in two different ways:

* To halt execution at any node, set ``halt_on_exception`` to ``True`` when initializing an :class:`~async_graph_data_flow.AsyncGraph` instance.
* To halt execution at a specific node, set ``halt_on_exception`` to ``True`` when using :func:`~async_graph_data_flow.AsyncGraph.add_node`  to add the node in question to the graph.

.. literalinclude:: ../examples/halt_on_exception_at_a_specific_node.py
   :language: python
   :emphasize-lines: 39

.. literalinclude:: ../examples/halt_on_exception_at_any_node.py
   :language: python
   :emphasize-lines: 36

Accessing and Raising an Exception
----------------------------------

While it's possible to halt the graph execution due to unhandled exceptions
(see `Halting Graph Execution upon Exceptions`_),
these exceptions are not raised from within the :func:`~async_graph_data_flow.AsyncExecutor.execute` call.
Instead, :class:`~async_graph_data_flow.AsyncExecutor`'s :attr:`~async_graph_data_flow.AsyncExecutor.exceptions`
allows access to the exceptions from the nodes,
and you can determine what to do with this information
(e.g., raise an exception on your own).

.. literalinclude:: ../examples/raising_an_exception.py
   :language: python
   :emphasize-lines: 24-27

Incorporating a Synchronous Function
------------------------------------

``async-graph-data-flow`` is for asynchronous functions by design,
but what if you need to run a *synchronous* function?
Inside a node's async function,
you may grab the asyncio's running loop,
then call the synchronous function with this loop.

.. literalinclude:: ../examples/external_sync_call.py
   :language: python
   :emphasize-lines: 27,29

Shared State Across Asynchronous Functions
------------------------------------------

Sharing state across the async functions is possible
if you pass the same object around them.
Such an object can be a custom class instance with methods and attributes as needed.

.. literalinclude:: ../examples/shared_state.py
   :language: python
   :emphasize-lines: 21,23,27,30,34,44,45
