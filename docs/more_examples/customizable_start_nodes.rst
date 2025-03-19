.. _customizable_start_nodes:

Customizable Start Nodes
========================

When :class:`~async_graph_data_flow.AsyncExecutor`'s :func:`~async_graph_data_flow.AsyncExecutor.execute`
is called,
by default the start nodes (= nodes without incoming edges) of the graph are automatically detected and called.
To override this default behavior,
use the keyword argument ``start_nodes`` at :func:`~async_graph_data_flow.AsyncExecutor.execute`
to select which nodes to execute instead and/or supply the arguments to whichever nodes you've selected.

.. literalinclude:: ../../examples/custom_start_nodes.py
   :language: python
   :emphasize-lines: 34

.. literalinclude:: ../../examples/custom_start_node_args.py
   :language: python
   :emphasize-lines: 34
