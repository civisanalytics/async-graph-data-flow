.. _graph_with_nodes_only_and_no_edges:

Graph with Nodes only and No Edges
==================================

It is possible to execute a graph with nodes only and no edges.
In this case,
if ``start_nodes`` at :func:`~async_graph_data_flow.AsyncExecutor.execute` are not specified (see above),
then *all* nodes are start nodes (because all nodes don't have an incoming edge),
and therefore all nodes will execute concurrently upon graph execution.
The start nodes and their arguments at the beginning of the graph execution are available at
:attr:`~async_graph_data_flow.AsyncExecutor.start_nodes` of :func:`~async_graph_data_flow.AsyncExecutor.execute`.

.. literalinclude:: ../../examples/graph_with_no_edges.py
   :language: python
   :emphasize-lines: 30,39,48
