.. _flexible_edge_behaviors_between_nodes:

Flexible Edge Behaviors Between Nodes
=====================================

Batch
End of data token
batch size = 0 for blocking / synchronization


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
        queue4 --> |"(3, 4, 5)<br/>(3, 4, 5)<br/>(3, 4, 5)"| node4
    end
    style queue4 fill:#ffbbff, stroke:#030303, stroke-width:2px;

    node1 --> |yields<br/>3, 3, 3| queue4
    node2 --> |yields<br/>4, 4, 4, 4| queue4
    node3 --> |yields<br/>5, 5, 5, 5, 5| queue4


.. literalinclude:: ../../examples/combine_data_from_multiple_source_nodes.py
   :language: python
   :emphasize-lines: 7, 72
