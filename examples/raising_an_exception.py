from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def node1():
    yield "hello"
    yield "world"


async def node2(data):
    raise ValueError(f"bad data: {data}")
    yield



if __name__ == "__main__":
    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    executor = AsyncExecutor(etl_graph)
    executor.execute()

    if any(excs := executor.exceptions.values()):
        for exc in excs:
            print(f"Exceptions: {exc}")
        raise RuntimeError("oh no! something went wrong in the graph execution")

    # Output:
    # -------
    # Graph: {'node1': {'node2'}, 'node2': set()}
    #
    # ... (logging for the unhandled exceptions from the nodes,
    #      without actually raising the exceptions)
    #
    # Exceptions: []
    # Exceptions: [ValueError('bad data: hello'), ValueError('bad data: world')]
    # Traceback (most recent call last):
    # File "/path/to/examples/raising_an_exception.py", line 28, in <module>
    #     raise RuntimeError("oh no! something went wrong in the graph execution")
    # RuntimeError: oh no! something went wrong in the graph execution
