import asyncio
import time

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def node1():
    print("from node1")
    await asyncio.sleep(2)
    yield


async def node2():
    print("from node2")
    await asyncio.sleep(2)
    yield


async def node3():
    print("from node3")
    await asyncio.sleep(2)
    yield


if __name__ == "__main__":
    graph = AsyncGraph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    # Nodes are added, but there are no edges.

    print(f"Graph: {graph.nodes_to_edges}")
    executor = AsyncExecutor(graph)

    t1 = time.time()
    executor.execute()
    t2 = time.time()
    print("execution time:", t2 - t1)
    print("start nodes:", executor.start_nodes)

    # Output:
    # -------
    # Graph: {'node1': set(), 'node2': set(), 'node3': set()}
    # from node1
    # from node2
    # from node3
    # execution time: 2.0039637088775635
    # start nodes: {'node3': (), 'node1': (), 'node2': ()}
