.. _shared_state_across_asynchronous_functions:

Shared State Across Asynchronous Functions
==========================================

Sharing state across the async functions is possible
if you pass the same object around them.
Such an object can be a custom class instance with methods and attributes as needed.

.. literalinclude:: ../../examples/shared_state.py
   :language: python
   :emphasize-lines: 21,23,27,30,34,44,45
