import asyncio
import itertools

from async_graph_data_flow import AsyncExecutor, AsyncGraph


class CombineDataQueue(asyncio.Queue):
    def __init__(self, node_order: list[str]):
        super().__init__()
        # This custom queue class assumes that a source node yields a tuple
        # where the first element is the node marker and the rest are the data.
        # `node_order` has the node markers for all the source nodes,
        # in the order that the data from all source nodes will be combined.
        self.node_order = node_order
        self.queues = {node: asyncio.Queue() for node in node_order}

    async def put(self, item):
        node_marker, *data = item
        if node_marker not in self.node_order:
            raise ValueError(f"Node {node_marker} not in node order {self.node_order}")
        if not data:
            raise ValueError(f"Data missing for node {node_marker}")
        await self.queues[node_marker].put(data)
        # In this specific example, if and only if the individual queues
        # for *all* source nodes have data,
        # combine the data and put the result in the main queue.
        # This means that the k-th item in the main queue will be a tuple
        # of the k-th items from each source node, and that any additional data
        # from a source node will either wait until all source nodes have data
        # to create a new item for the main queue, or be ignored altogether.
        if all(not q.empty() for q in self.queues.values()):
            new = tuple(
                itertools.chain(*((q.get_nowait()) for q in self.queues.values()))
            )
            await super().put(new)


async def threes():
    for _ in range(3):
        await asyncio.sleep(0.001)
        print("threes yielding 3")
        # Yielding a tuple with the node marker and the data.
        # The node marker tells the custom queue which source node the data is from.
        yield "threes", 3


async def fours():
    for _ in range(4):
        await asyncio.sleep(0.001)
        print("fours yielding 4")
        yield "fours", 4


async def fives():
    for _ in range(5):
        await asyncio.sleep(0.001)
        print("fives yielding 5")
        yield "fives", 5


async def final_node(int1, int2, int3):
    print(f"Final node received {int1}, {int2}, {int3}")
    yield


if __name__ == "__main__":
    graph = AsyncGraph()

    graph.add_node(threes)
    graph.add_node(fours)
    graph.add_node(fives)
    graph.add_node(final_node, queue=CombineDataQueue(["threes", "fours", "fives"]))

    graph.add_edge("threes", "final_node")
    graph.add_edge("fours", "final_node")
    graph.add_edge("fives", "final_node")

    AsyncExecutor(graph).execute()

    # Output:
    # -------
    # threes yielding 3
    # fours yielding 4
    # fives yielding 5
    # Final node received 3, 4, 5
    # threes yielding 3
    # fours yielding 4
    # fives yielding 5
    # Final node received 3, 4, 5
    # threes yielding 3
    # fours yielding 4
    # fives yielding 5
    # Final node received 3, 4, 5
    # fours yielding 4
    # fives yielding 5
    # fives yielding 5
