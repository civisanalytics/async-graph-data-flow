.. _incorporating_a_synchronous_function:

Incorporating a Synchronous Function
====================================

``async-graph-data-flow`` is for asynchronous functions by design,
but what if you need to run a *synchronous* function?
Inside a node's async function,
you may grab the asyncio's running loop,
then call the synchronous function with this loop.

.. literalinclude:: ../../examples/external_sync_call.py
   :language: python
   :emphasize-lines: 27,29
