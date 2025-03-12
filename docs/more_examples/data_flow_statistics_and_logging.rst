.. _data_flow_statistics_and_logging:

Data Flow Statistics and Logging
================================

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

.. literalinclude:: ../../examples/data_flow_logging.py
   :language: python
   :emphasize-lines: 36-38
