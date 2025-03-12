.. _halting_graph_execution_upon_exceptions:

Halting Graph Execution upon Exceptions
=======================================

By default, an unhandled exception from any node does not halt the graph execution.
This behavior can be altered in two different ways:

* To halt execution at any node, set ``halt_on_exception`` to ``True`` when initializing an :class:`~async_graph_data_flow.AsyncGraph` instance.
* To halt execution at a specific node, set ``halt_on_exception`` to ``True`` when using :func:`~async_graph_data_flow.AsyncGraph.add_node`  to add the node in question to the graph.

.. literalinclude:: ../../examples/halt_on_exception_at_a_specific_node.py
   :language: python
   :emphasize-lines: 39

.. literalinclude:: ../../examples/halt_on_exception_at_any_node.py
   :language: python
   :emphasize-lines: 36
