.. _technical:

Technical Notes
===============

Functions Arranged as a Graph
-----------------------------

The ``async-graph-data-flow`` package provides a framework for arranging
functions in a directed acyclic graph (DAG).

.. mermaid::

    flowchart LR

    A[func1] --> B[func2]
    B --> C[func3]
    B --> D[func4]
    C --> E[func5]
    D --> E

Each function must be an asynchronous generator function,
which means it is defined with the ``async`` keyword
and yields something.

.. code-block:: python

    async def func1(arg1, arg2):
        ...
        yield output

For two nodes to be connected correctly in terms of function definition,
the source node's function must yield what the destination node's function
expects as input
(for more information,
see the ``unpack_input`` parameter of :func:`~async_graph_data_flow.AsyncGraph.add_node`).

.. mermaid::

    flowchart LR

    START[ ] -.-> A
    B -.-> STOP[ ]
    A["async def func2(...):<br/>&nbsp;&nbsp;&nbsp;&nbsp;...<br/>&nbsp;&nbsp;&nbsp;&nbsp;yield <strong>foo, bar</strong>"] --> B["async def func3(<strong>foo, bar</strong>):<br/>&nbsp;&nbsp;&nbsp;&nbsp;...<br/>&nbsp;&nbsp;&nbsp;&nbsp;yield ..."]
    style A text-align:left
    style B text-align:left
    style START fill-opacity:0, stroke-opacity:0;
    style STOP  fill-opacity:0, stroke-opacity:0;

Tasks and Queues
----------------

During runtime, each node's function is run concurrently
as one or more :class:`tasks<asyncio.Task>` in the event loop.
The number of tasks for a given node is controlled by
the ``max_tasks`` parameter that can be set at :func:`~async_graph_data_flow.AsyncGraph.add_node`.

By default, a node is associated with an :class:`asyncio.Queue` instance
responsible for providing the items to the tasks of the node.
The queue receives its items as the source nodes yield them.
The queue is first-in-first-out, which means that
it keeps track of the items yielded from the tasks of the source nodes
and feeds them one by one in the order by which the queue has received them.
An item leaves a queue when a task of the destination node becomes
available to process it.

.. mermaid::

    flowchart LR

    start1[ ] -.- queue1(("&nbsp;&nbsp;"))
    subgraph box1 [ ]
        queue1 --> node1["&nbsp;&nbsp;&nbsp;&nbsp;"]
    end
    style start1 fill-opacity:0, stroke-opacity:0;

    start2[ ] -.- queue2(("&nbsp;&nbsp;"))
    subgraph box2 [ ]
        queue2 --> node2["&nbsp;&nbsp;&nbsp;&nbsp;"]
    end
    style start2 fill-opacity:0, stroke-opacity:0;

    subgraph node and its associated queue
        queue3((queue)) --> node3[task 1, task 2,<br/>task 3, ...]
    end

    node1 --> |yield<br/>items| queue3
    node2 --> |yields<br/>items| queue3
    node3 -.-> |yields<br/>items| STOP[ ]
    style STOP  fill-opacity:0, stroke-opacity:0;

While the default queue of a node doesn't process the data after receiving it
from the source nodes and before feeding it to the tasks of the destination node,
you can customize the queue behavior by passing in a custom queue object
to the ``queue`` parameter of :func:`~async_graph_data_flow.AsyncGraph.add_node`,
see :ref:`flexible_edge_behaviors_between_nodes`.

Example
-------

Let's check out a sample script using async-graph-data-flow and processing actual data
that brings together some of the components discussed above.
The example below pulls data from `Open Brewery DB <https://www.openbrewerydb.org/>`_
into a local CSV file.


.. code-block:: python

    # This Python script was tested with Python 3.11.
    # Apart from async-graph-data-flow, it requires several other third-party dependencies,
    # which can be installed by `pip install aiocsv aiofile aiohttp`.

    import aiocsv
    import aiofile
    import aiohttp
    from async_graph_data_flow import AsyncGraph, AsyncExecutor

    # API doc: https://www.openbrewerydb.org/documentation
    URL = "https://api.openbrewerydb.org/v1/breweries"
    CSV_HEADER = [
        "id",
        "name",
        "brewery_type",
        "address_1",
        "address_2",
        "address_3",
        "city",
        "state_province",
        "postal_code",
        "country",
        "longitude",
        "latitude",
        "phone",
        "website_url",
        "state",
        "street",
    ]
    OUTPUT_FILENAME = "breweries_us_async.csv"

    has_written_csv_header = False


    async def get_open_brewery_data():
        page = 1
        async with aiohttp.ClientSession() as session:
            while True:
                params = {
                    "by_country": "United States",
                    "page": page,
                    "per_page": 200,
                }
                async with session.get(URL, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if not data:
                        break
                    else:
                        yield data
                        page += 1


    async def write_to_csv(data: list[dict[str, str]]):
        global has_written_csv_header
        async with aiofile.async_open(OUTPUT_FILENAME, mode="a", encoding="utf8") as f:
            csv_writer = aiocsv.AsyncDictWriter(f, CSV_HEADER)
            if not has_written_csv_header:
                await csv_writer.writeheader()
                has_written_csv_header = True
            await csv_writer.writerows(data)
            yield


    def main():
        graph = AsyncGraph()
        graph.add_node(get_open_brewery_data)
        graph.add_node(write_to_csv)
        graph.add_edge(get_open_brewery_data, write_to_csv)

        executor = AsyncExecutor(graph)
        executor.execute()
        print("data downloaded:", OUTPUT_FILENAME)


    if __name__ == "__main__":
        main()

In this code, ``main()`` defines a graph and executes it.
The graph has two connected nodes.
The source node, with the asynchronous generator function ``get_open_brewery_data()``,
yields items to the destination node with ``write_to_csv()``:

.. mermaid::

    flowchart LR

    A[get_open_brewery_data] --> B[write_to_csv]

For the source node,
the following shows an abridged version of ``get_open_brewery_data()``
to highlight what the function yields:

.. code-block:: python

    async def get_open_brewery_data():
        page = 1
        ...
        while True:
            params = {"page": page, ...}
            ...
            yield data
            page += 1

As the data from Open Brewery DB is paginated from its API,
``get_open_brewery_data()`` makes an API call for one page worth of data,
yields this data to the destination node (``write_to_csv()``),
repeats this process, and stops once all pages of data have been retrieved.

The destination node with ``write_to_csv()`` has its associated queue provide
inputs from the items yielded by ``get_open_brewery_data()``.


.. mermaid::

    flowchart LR

    Q(("Queue items:<br/>[{'col1': 'val1', ...}, ...]<br/>[{'col1': 'val1', ...}, ...]<br/>...<br/>"))
    A[get_open_brewery_data]
    B[write_to_csv]
    A --> |yields<br/>items| Q
    Q --> B

``get_open_brewery_data()`` yields a page of the Open Brewery DB data,
which is a list of records where each record is a dictionary of column names
mapped to values. The function signature of ``write_to_csv()`` expects exactly
such a list of dictionaries:

.. code-block:: python

    async def write_to_csv(data: list[dict[str, str]]):
        ...

