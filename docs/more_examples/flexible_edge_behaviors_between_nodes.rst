.. _flexible_edge_behaviors_between_nodes:

Flexible Edge Behaviors Between Nodes
=====================================

Whereas each node in the graph is defined by an asynchronous generator function,
the edge between two nodes is represented by a queue object that feeds data into
the destination node and collects data from the source nodes (see :ref:`tasks_and_queues`).
By default, this queue object spits out data items to the associated destination node one at a time,
as it becomes available from any of the source nodes,
and as efficieintly as coordinated by the async event loop.
In your application, you may want to override this default queue for custom edge behaviors
for one or more edges in the graph.

When a node is created with :func:`~async_graph_data_flow.AsyncGraph.add_node`,
custom edge behaviors can be implemented by passing in a custom queue object
to the ``queue`` parameter.
This queue object must be an instance of :class:`asyncio.Queue` or a subclass thereof.
(The default queue object is simply an instance of :class:`asyncio.Queue`.)
A custom queue object can result in a variety of edge behaviors between nodes:

* A queue pre-loaded with data items:
    At the outset of the graph execution, if you would like certain nodes
    (including non-starting nodes of the graph) to receive specific data items immediately,
    you can pass in a queue object pre-loaded with these data items for these nodes.
    Implementationally, create an :class:`asyncio.Queue` instance and
    call ``await queue.put(item)`` as desired to pre-load the queue with data items,
    then pass this queue object to the ``queue`` parameter of the destination node
    at :func:`~async_graph_data_flow.AsyncGraph.add_node`.
* Do something with the data after it's received from a source node and before it's fed to the destination node:
    If you would like to transform the data or perform any other operation on it,
    your custom queue likely comes from a subclass of :class:`asyncio.Queue`
    where you override the ``get`` and/or ``put`` methods,
    becase these methods control what happens to the data item
    after it has arrived at the queue and before it is fed to the destination node.

In the following examples, we focus on the second use case, where
flexible edge behaviors are achieved by a subclass of :class:`asyncio.Queue`.


Batching
--------

Instead of the edge queue receiving and feeding data items one at a time,
you may want to batch the data items before feeding them to the destination node.
To do so, let's define the following:

* A ``BatchQueue`` class that subclasses :class:`asyncio.Queue` for batching data items.
* A sentinel class ``EndOfData`` to signal the end of data.

Perhaps the most common use case for batching is to group data items into batches of a fixed size:

.. mermaid::

    flowchart LR

    start1[ ] -.- queue1(("&nbsp;"))
    subgraph data_source
        queue1 --> node1["&nbsp;&nbsp;"]
    end
    style start1 fill-opacity:0, stroke-opacity:0;

    queue2((custom queue<br/>to batch data))
    node2["async gen<br/>function"]
    subgraph batched_inputs
        queue2 --> |"three inputs:<br/>[1, 2, 3, 4]<br/>[5, 6, 7, 8]<br/>[9, 10]"| node2
    end
    style queue2 fill:#ffccff, stroke:#030303, stroke-width:2px;

    node1 --> |yields<br/>1, 2, 3, ..., 10| queue2

.. literalinclude:: ../../examples/batching_by_batch_size.py
   :language: python
   :emphasize-lines: 6, 10, 49

Using the same ``BatchQueue`` and ``EndOfData`` defined here,
it's also possible to have the effect of waiting for all data items
from the source nodes before feeding them to the destination node,
by setting the batch size to ``float('inf')`` (infinity, for no batch size limit)
--- this is an actual use case in production code maintained by the package developers.

Beyond batch size, batching can be controlled by other criteria using your own custom queue class,
such as special data items or markers (in a way, the ``EndOfData`` marker above is an example),
time intervals, or other conditions.

Combining Data from Multiple Source Nodes
------------------------------------------

By default, a source node must yield data that matches the function signature
of the destination node. To work around this constraint, a custom queue object
at the edge between the source and destination nodes can be used.
One use case is to combine data from multiple source nodes
before feeding it to the destination node. For example:

.. mermaid::

    flowchart LR

    start1[ ] -.- queue1(("&nbsp;"))
    subgraph threes
        queue1 --> node1["&nbsp;&nbsp;"]
    end
    style start1 fill-opacity:0, stroke-opacity:0;

    start2[ ] -.- queue2(("&nbsp;"))
    subgraph fours
        queue2 --> node2["&nbsp;&nbsp;"]
    end
    style start2 fill-opacity:0, stroke-opacity:0;

    start3[ ] -.- queue3(("&nbsp;"))
    subgraph fives
        queue3 --> node3["&nbsp;&nbsp;"]
    end
    style start3 fill-opacity:0, stroke-opacity:0;

    queue4((custom queue<br/>to combine data))
    node4["async gen<br/>function"]
    subgraph final_node
        queue4 --> |"three inputs<br/>to the func:<br/>(3, 4, 5)<br/>(3, 4, 5)<br/>(3, 4, 5)"| node4
    end
    style queue4 fill:#ffccff, stroke:#030303, stroke-width:2px;

    node1 --> |yields<br/>3, 3, 3| queue4
    node2 --> |yields<br/>4, 4, 4, 4| queue4
    node3 --> |yields<br/>5, 5, 5, 5, 5| queue4


.. literalinclude:: ../../examples/combine_data_from_multiple_source_nodes.py
   :language: python
   :emphasize-lines: 7, 72
