.. _accessing_and_raising_an_exception:

Accessing and Raising an Exception
==================================

While it's possible to halt the graph execution due to unhandled exceptions
(see :ref:`halting_graph_execution_upon_exceptions`),
these exceptions are not raised from within the :func:`~async_graph_data_flow.AsyncExecutor.execute` call.
Instead, :class:`~async_graph_data_flow.AsyncExecutor`'s :attr:`~async_graph_data_flow.AsyncExecutor.exceptions`
allows access to the exceptions from the nodes,
and you can determine what to do with this information
(e.g., raise an exception on your own).

.. literalinclude:: ../../examples/raising_an_exception.py
   :language: python
   :emphasize-lines: 24-27
