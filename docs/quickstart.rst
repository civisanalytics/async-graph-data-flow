.. _quickstart:

Quickstart
==========

To use the ``async-graph-data-flow`` package:

1. Create an :class:`~async_graph_data_flow.AsyncGraph` object by adding your asynchronous functions as nodes to this graph and setting the edges.
2. Create an :class:`~async_graph_data_flow.AsyncExecutor` object that takes this :class:`~async_graph_data_flow.AsyncGraph` object.
3. Execute the graph by calling :meth:`~async_graph_data_flow.AsyncExecutor.execute`.

As an example, let's say you have the following five functions connected in a DAG as follows:

.. mermaid::

    flowchart LR

    A[func1] --> B[func2]
    B --> C[func3]
    B --> D[func4]
    C --> E[func5]
    D --> E

To represent this graph and execute its functions with ``async-graph-data-flow``:

.. code-block:: python

    import asyncio
    import time

    from async_graph_data_flow import AsyncGraph, AsyncExecutor


    async def func1():
        for i in range(2):
            await asyncio.sleep(1)
            print(f"At func1: {i}")
            yield f"From func1: {i}"


    async def func2(data):
        print(f"At func2: {data}")
        yield f"From func2: {data}"


    async def func3(data):
        print(f"At func3: {data}")
        yield data, "2nd arg from func3"


    async def func4(data):
        print(f"At func4: {data}")
        yield data, "2nd arg from func4"


    async def func5(data1, data2):
        print(f"At func5: {data1} + {data2}")
        yield


    if __name__ == "__main__":
        graph = AsyncGraph()

        graph.add_node(func1)
        graph.add_node(func2)
        graph.add_node(func3)
        graph.add_node(func4)
        graph.add_node(func5)
        graph.add_edge("func1", "func2")
        graph.add_edge("func2", "func3")
        graph.add_edge("func2", "func4")
        graph.add_edge("func3", "func5")
        graph.add_edge("func4", "func5")

        print(f"Graph: {graph.nodes_to_edges}")

        executor = AsyncExecutor(graph)

        t1 = time.time()
        executor.execute()
        t2 = time.time()
        print(f"execution time:", t2 - t1)

Executing this script gives the following output:

.. code-block:: text

    Graph: {'func1': {'func2'}, 'func2': {'func3', 'func4'}, 'func3': {'func5'}, 'func4': {'func5'}, 'func5': set()}
    At func1: 0
    At func2: From func1: 0
    At func3: From func2: From func1: 0
    At func4: From func2: From func1: 0
    At func5: From func2: From func1: 0 + 2nd arg from func3
    At func5: From func2: From func1: 0 + 2nd arg from func4
    At func1: 1
    At func2: From func1: 1
    At func3: From func2: From func1: 1
    At func4: From func2: From func1: 1
    At func5: From func2: From func1: 1 + 2nd arg from func3
    At func5: From func2: From func1: 1 + 2nd arg from func4
    execution time: 2.0111138820648193
