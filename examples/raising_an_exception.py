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

    print(executor.data_flow_stats)
    print(executor.exceptions)

    if any(excs := executor.exceptions.values()):
        for i, exc in enumerate(excs, 1):
            print(f"Exception #{i}: {exc}")
        raise RuntimeError("oh no! something went wrong in the graph execution")

    # Output:
    # -------
    # Graph: {'node1': {'node2'}, 'node2': set()}
    #
    # ... (logging for the unhandled exceptions from the nodes,
    #      without actually raising the exceptions)
    #
    # Exception #1
    # ValueError: bad data: hello
    # Exception #2
    # ValueError: bad data: world
    # Traceback (most recent call last):
    #   ...
    # RuntimeError: oh no! something went wrong in the graph execution
