from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def node1(data):
    print(f"node1 received: {data}")
    yield data
    yield "hello"
    yield "world"


async def node2(data):
    print(f"node2 received: {data}")
    yield data
    yield "data1"
    yield "data2"


async def node3(data):
    print(f"node3 received: {data}")
    yield


if __name__ == "__main__":
    graph = AsyncGraph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_edge("node1", "node3")
    graph.add_edge("node2", "node3")

    print(f"Graph: {graph.nodes_to_edges}")

    executor = AsyncExecutor(graph)
    executor.execute(start_nodes={"node1": ("foo",), "node2": ("bar",)})

    # Output:
    # -------
    # Graph: {'node1': {'node3'}, 'node2': {'node3'}, 'node3': set()}
    # node1 received: foo
    # node2 received: bar
    # node3 received: foo
    # node3 received: hello
    # node3 received: world
    # node3 received: bar
    # node3 received: data1
    # node3 received: data2
