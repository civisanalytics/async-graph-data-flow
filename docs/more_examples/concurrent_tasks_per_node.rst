.. _concurrent_tasks_per_node:

Concurrent Tasks Per Node
=========================

By default, each node creates one task at a time.
To spawn multiple, concurrent tasks from a node,
set ``max_tasks`` at :func:`~async_graph_data_flow.AsyncGraph.add_node`.

.. literalinclude:: ../../examples/concurrent_tasks_per_node.py
   :language: python
   :emphasize-lines: 25
