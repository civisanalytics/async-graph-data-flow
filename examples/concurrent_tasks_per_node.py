import asyncio
import time

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def node1():
    for i in range(5):
        yield i


async def node2(i):
    await asyncio.sleep(2)
    print(f"node2 received {i}")
    yield


if __name__ == "__main__":
    for max_tasks in (1, 5):
        print(f"max_tasks: {max_tasks}")
        graph = AsyncGraph()
        graph.add_node(node1)
        graph.add_node(
            node2,
            max_tasks=max_tasks,
        )
        graph.add_edge("node1", "node2")

        print(f"Graph: {graph.nodes_to_edges}")
        executor = AsyncExecutor(graph)

        t1 = time.time()
        executor.execute()
        t2 = time.time()
        print(f"execution time: {t2 - t1}")
        print()

        # Output:
        # -------
        # max_tasks: 1
        # Graph: {'node1': {'node2'}, 'node2': set()}
        # node2 received 0
        # node2 received 1
        # node2 received 2
        # node2 received 3
        # node2 received 4
        # execution time: 10.004492044448853
        #
        # max_tasks: 5
        # Graph: {'node1': {'node2'}, 'node2': set()}
        # node2 received 0
        # node2 received 1
        # node2 received 2
        # node2 received 3
        # node2 received 4
        # execution time: 2.001836061477661
